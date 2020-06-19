import pyotp

from django.views import View
from django.shortcuts import render
from django.db import IntegrityError
from django.db.models import Q, Case, When, Value
from django.utils import timezone
from django.contrib.auth.models import User

from utils.generals import get_model

OTPFactory = get_model('person', 'OTPFactory')


class HomeView(View):
    template_name = 'global/home.html'
    context = dict()

    def get(self, request):
        """
        token = 'pbkdf2_sha256$180000$KKxhXFvPgP03$Tx3Iu6KKqbQUges1760j7AaRikPHPBn0iVUWziMQv+E='
        email = 'hellopuyup@gmail.coma'
        msisdn = '1234568'

        xo = OTPFactory.objects.get(
            Q(token=token),
            Q(email=Case(When(email__isnull=False, then=Value(email))))
            | Q(msisdn=Case(When(msisdn__isnull=False, then=Value(msisdn))))
        )
        print(xo)
        """

        # 136552 1592187034.910067 LI3R3MA3ILI6CRBV

        valid_until = timezone.now() + timezone.timedelta(hours=2)
        valid_until_timestamp = valid_until.replace(microsecond=0).timestamp()
        token = pyotp.random_base32()
        totp = pyotp.TOTP('LI3R3MA3ILI6CRBV')
        passcode = totp.at(valid_until_timestamp)
        is_passed = totp.verify(136552, for_time=1592187034.910067)
        
        """
        try:
            User.objects.create_user(token, '%s@lll.com' % token, '561799AA', first_name=token)
        except IntegrityError as e:
            print(e)
        """
        print(is_passed)
        print(passcode, valid_until_timestamp, token)

        x = User.objects.exclude(username='admineet')
        print(x.count())
        return render(request, self.template_name, self.context)
