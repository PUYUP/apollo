from django.db import transaction
from django.db.models import Q, F, Case, When, Value
from django.utils import timezone

from utils.generals import get_model
from apps.person.utils.constant import ROLE_DEFAULTS
from apps.person.utils.auth import set_roles

# Celery task
from apps.person.tasks import send_otp_email

Account = get_model('person', 'Account')
Profile = get_model('person', 'Profile')
Role = get_model('person', 'Role')


@transaction.atomic
def user_save_handler(sender, instance, created, **kwargs):
    if created:
        Account.objects.create(user=instance, email=instance.email,
                               email_verified=True)
        Profile.objects.create(user=instance)
        Role.objects.create(user=instance)

        # set default roles
        roles = list()
        for item in ROLE_DEFAULTS:
            roles.append(item[0])

        if roles:
            set_roles(user=instance, roles=roles)

    if not created:
        instance.account.email = instance.email
        instance.account.save()


@transaction.atomic
def otpcode_save_handler(sender, instance, created, **kwargs):
    # create tasks
    # run only on resend and created
    if instance.is_used == False and instance.is_verified == False:
        if instance.email:
            data = {
                'email': getattr(instance, 'email', None),
                'passcode': getattr(instance, 'passcode', None)
            }
            send_otp_email.delay(data)

        # mark older OTP Code to expired
        oldest = instance.__class__.objects \
            .filter(
                Q(challenge=instance.challenge),
                Q(is_used=False), Q(is_expired=False),
                Q(email=Case(When(email__isnull=False, then=Value(instance.email))))
                | Q(msisdn=Case(When(msisdn__isnull=False, then=Value(instance.msisdn))))
            ).exclude(passcode=instance.passcode)

        if oldest.exists():
            oldest.update(is_expired=True)
