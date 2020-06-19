import base64
import os

from django.conf import settings
from django.db import transaction, IntegrityError
from django.db.models import Q, Case, When, Value
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.models import User, Permission
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import EmailValidator
from django.core.files import File

# THIRD PARTY
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotAcceptable

# PROJECT UTILS
from utils.generals import get_model
from apps.person.utils.auth import clear_otp_session
from apps.person.utils.constant import (
    REGISTER_VALIDATION,
    CHANGE_MSISDN,
    CHANGE_MSISDN_VALIDATION,
    CHANGE_EMAIL,
    CHANGE_EMAIL_VALIDATION,
    CHANGE_USERNAME
)

Profile = get_model('person', 'Profile')
Account = get_model('person', 'Account')
OTPFactory = get_model('person', 'OTPFactory')


def handle_upload_profile_picture(instance, file):
    if instance and file:
        name, ext = os.path.splitext(file.name)
        username = instance.user.username
        instance.picture.save('%s%s' % (username, ext), file, save=False)
        instance.save(update_fields=['picture'])


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields is not None and fields != '__all__':
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


# Check duplicate email if has verified
class EmailDuplicateValidator(object):
    requires_context = True

    def __call__(self, value, serializer_field):
        user = User.objects \
            .prefetch_related('account') \
            .select_related('account') \
            .filter(email=value, account__email_verified=True)

        if user.exists():
            raise serializers.ValidationError(
                _(u"Email {email} sudah terdaftar.".format(email=value))
            )


# Check email is validate for registration purpose
class EmailVerifiedForRegistrationValidator(object):
    requires_context = True

    def __call__(self, value, serializer_field):
        otp = OTPFactory.objects.filter(challenge=REGISTER_VALIDATION, email=value,
                                        is_used=False, is_verified=True, is_expired=False)

        if not otp.exists():
            raise serializers.ValidationError(_(u"Alamat email belum tervalidasi."))


# Check duplicate msisdn if has verified
class MSISDNDuplicateValidator(object):
    requires_context = True

    def __call__(self, value, serializer_field):
        user = User.objects \
            .prefetch_related('account') \
            .select_related('account') \
            .filter(account__msisdn=value, account__msisdn_verified=True)

        if user.exists():
            raise serializers.ValidationError(_(u"Nomor telepon sudah digunakan."))


# Check msisdn is validate for registration purpose
class MSISDNVerifiedForRegistrationValidator(object):
    requires_context = True

    def __call__(self, value, serializer_field):
        otp = OTPFactory.objects.filter(challenge=REGISTER_VALIDATION, msisdn=value,
                                        is_used=False, is_verified=True, is_expired=False)

        if not otp.exists():
            raise serializers.ValidationError(_(u"Nomor telepon belum tervalidasi."))


# Check duplicate msisdn if has verified
class MSISDNNumberValidator(object):
    requires_context = True

    def __call__(self, value, serializer_field):
        if not value.isnumeric():
            raise serializers.ValidationError(_(u"Nomor telepon hanya boleh angka."))


# Password verification
class PasswordValidator(object):
    requires_context = True

    def __call__(self, value, serializer_field):
        validate_password(value)


# User profile serializer
class ProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField()

    class Meta:
        model = Profile
        exclude = ('user', 'id', 'date_created', 'date_updated',)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['gender'] = instance.get_gender_display()
        return ret

    @transaction.atomic
    def update(self, instance, validated_data):
        request = self.context.get('request', None)

        # upload picture / avatar use celery task
        picture = validated_data.pop('picture', None)
        if picture:
            fsize = picture.size
            fname = picture.name

            # max size 2.5 MB
            if fsize > 312500:
                raise serializers.ValidationError(_(u"Maksimal ukuran file 2.5 MB"))

            # only accept JPG, JPEG & PNG
            if not fname.endswith('.jpg') and not fname.endswith('.jpeg') and not fname.endswith('.png'):
                raise serializers.ValidationError(_(u"File hanya boleh .jpg, .jpeg dan .png"))

            file = request.FILES.get('picture')
            handle_upload_profile_picture(instance, file)

        # update user instance
        first_name = validated_data.pop('first_name', None)
        if first_name:
            instance.user.first_name = first_name
            instance.user.save()

        # this is real profile instance
        update_fields = list()
        for key, value in validated_data.items():
            if hasattr(instance, key):
                old_value = getattr(instance, key, None)
                if value and old_value != value:
                    update_fields.append(key)
                    setattr(instance, key, value)
        
        if update_fields:
            instance.save(update_fields=update_fields)
        return instance


# User account serializer
class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        exclude = ('user', 'id', 'date_created', 'date_updated',)
        extra_kwargs = {
            'msisdn': {
                'min_length': 8,
                'max_length': 14,
                'validators': [MSISDNNumberValidator()]
            }
        }
    
    def __init__(self, *args, **kwargs):
        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)

        # default otp
        self.otp_obj = None

        # data available only on PATCH and POST
        data = kwargs.get('data', None)
        if data:
            if settings.STRICT_MSISDN_DUPLICATE:
                self.fields['msisdn'].validators.extend([MSISDNDuplicateValidator()])

    def validate_msisdn(self, value):
        if self.instance:
            with transaction.atomic():
                try:
                    self.otp_obj = OTPFactory.objects.select_for_update() \
                        .get_verified_unused(msisdn=value, challenge=CHANGE_MSISDN_VALIDATION)
                except ObjectDoesNotExist:
                    raise serializers.ValidationError(_(u"Kode OTP pembaruan msisdn salah."))
        return value

    def to_internal_value(self, data):
        data = super().to_internal_value(data)

        # one field each update request
        if len(data) > 1:
            raise serializers.ValidationError({
                'field': _("Hanya boleh satu data.")
            })

        # field can't empty to
        if len(data) == 0:
            raise serializers.ValidationError({
                'field': _("Tidak ada yang diperbarui.")
            })
        return data

    @transaction.atomic
    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            if hasattr(instance, key):
                old_value = getattr(instance, key, None)
                if value and old_value != value:
                    setattr(instance, key, value)
        instance.save()

        # all done mark otp used
        self.otp_obj.mark_used()
        return instance


class UserFactorySerializer(DynamicFieldsModelSerializer, serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='person:user-detail',
                                               lookup_field='id', read_only=True)

    profile = ProfileSerializer(many=False, read_only=True)
    account = AccountSerializer(many=False, read_only=True)

    # for registration only
    # msisdn not part of User model
    # msisdn part of Account
    msisdn = serializers.CharField(required=False, write_only=True,
                                   validators=[MSISDNNumberValidator()],
                                   min_length=8, max_length=14)

    class Meta:
        model = User
        exclude = ('user_permissions', 'groups', 'date_joined',
                   'is_superuser', 'last_login', 'is_staff',)
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 6
            },
            'username': {
                'min_length': 4,
                'max_length': 15
            },
            'email': {
                'required': False,
                'validators': [EmailValidator()]
            }
        }

    def __init__(self, *args, **kwargs):
        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)

        # default otp
        self.otp_obj = None

        # data
        data = kwargs.get('data', dict())
        self.email = data.get('email', None)
        self.msisdn = data.get('msisdn', None)
        
        # used for password change only
        self.password = data.get('password', None)
        self.new_password1 = data.get('new_password1', None)
        self.new_password2 = data.get('new_password2', None)

        # remove password validator if update
        if self.instance and self.new_password1 and self.new_password2:
            pass
        else:
            self.fields['password'].validators.extend([PasswordValidator()])

        if settings.STRICT_MSISDN:
            # MSISDN required if EMAIL not provided
            if not self.email:
                self.fields['msisdn'].required = True

            if settings.STRICT_MSISDN_DUPLICATE:
                self.fields['msisdn'].validators.extend([MSISDNDuplicateValidator()])

            # for registration only
            if settings.STRICT_MSISDN_VERIFIED and not self.instance:
                self.fields['msisdn'].validators.extend([MSISDNVerifiedForRegistrationValidator()])

        if settings.STRICT_EMAIL:
            # EMAIL required if MSISDN not provided
            if not self.msisdn:
                self.fields['email'].required = True

            if settings.STRICT_EMAIL_DUPLICATE:
                self.fields['email'].validators.extend([EmailDuplicateValidator()])

            # for registration only
            if settings.STRICT_EMAIL_VERIFIED and not self.instance:
                self.fields['email'].validators.extend([EmailVerifiedForRegistrationValidator()])

    def validate_email(self, value):
        if self.instance:
            with transaction.atomic():
                try:
                    self.otp_obj = OTPFactory.objects.select_for_update() \
                        .get_verified_unused(email=value, challenge=CHANGE_EMAIL_VALIDATION)
                except ObjectDoesNotExist:
                    raise serializers.ValidationError(_(u"Kode OTP pembaruan email salah."))
        return value

    """
    def validate_username(self, value):
        if self.instance:
            email = self.instance.email
            msisdn = self.instance.account.msisdn

            with transaction.atomic():
                try:
                    self.otp_obj = OTPFactory.objects.select_for_update() \
                        .get_verified_unused(email=email, msisdn=msisdn, challenge=CHANGE_USERNAME)
                except ObjectDoesNotExist:
                    raise serializers.ValidationError(_(u"Kode OTP pembaruan nama pengguna salah."))
        return value
    """

    def validate_password(self, value):
        instance = getattr(self, 'instance', dict())
        if instance:
            username = getattr(instance, 'username', None)

            # make sure new and old password filled
            if not self.new_password1 or not self.new_password2:
                raise serializers.ValidationError(_(u"Kata sandi lama dan baru wajib."))

            if self.new_password1 != self.new_password2:
                raise serializers.ValidationError(_(u"Kata sandi lama dan baru tidak sama."))

            try:
                validate_password(self.new_password2)
            except ValidationError as e:
                raise serializers.ValidationError(e.messages)

            # check current password is passed
            passed = authenticate(username=username, password=self.password)
            if passed is None:
                raise serializers.ValidationError(_(u"Kata sandi lama salah."))

            return self.new_password2
        return value

    @transaction.atomic
    def update(self, instance, validated_data):
        request = self.context.get('request', None)

        for key, value in validated_data.items():
            if hasattr(instance, key):
                # update password
                if key == 'password':
                    instance.set_password(value)

                    # add flash message
                    messages.success(request, _("Kata sandi berhasil dirubah."
                                                " Login dengan kata sandi baru Anda."))
                else:
                    old_value = getattr(instance, key, None)
                    if value and old_value != value:
                        setattr(instance, key, value)
        instance.save()

        # all done mark otp as used
        if self.otp_obj:
            self.otp_obj.mark_used()
        return instance
