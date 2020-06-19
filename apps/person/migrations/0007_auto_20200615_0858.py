# Generated by Django 3.0.7 on 2020-06-15 01:58

import django.core.validators
from django.db import migrations, models
import utils.validators


class Migration(migrations.Migration):

    dependencies = [
        ('person', '0006_otpfactory_valid_until_timestamp'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='otpfactory',
            name='attempt_allowed',
        ),
        migrations.RemoveField(
            model_name='otpfactory',
            name='attempt_used',
        ),
        migrations.RemoveField(
            model_name='otpfactory',
            name='identifier',
        ),
        migrations.AddField(
            model_name='otpfactory',
            name='challenge',
            field=models.SlugField(choices=[('email_validation', 'Email Validation'), ('msisdn_validation', 'Telephone Validation'), ('register_validation', 'Register Validation'), ('password_reset', 'Password Reset'), ('change_msisdn', 'Change Telephone'), ('change_email', 'Change Email'), ('change_username', 'Change Username'), ('change_password', 'Change Password')], max_length=128, null=True, validators=[django.core.validators.RegexValidator(message="Code can only contain the letters a-z, A-Z, digits, and underscores, and can't start with a digit.", regex='^[a-zA-Z_][0-9a-zA-Z_]*$'), utils.validators.non_python_keyword]),
        ),
    ]
