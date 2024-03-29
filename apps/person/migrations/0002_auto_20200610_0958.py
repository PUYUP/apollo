# Generated by Django 3.0.7 on 2020-06-10 02:58

import django.core.validators
from django.db import migrations, models
import utils.validators


class Migration(migrations.Migration):

    dependencies = [
        ('person', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='birthdate',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='gender',
            field=models.CharField(blank=True, choices=[('undefined', 'Undefined'), ('male', 'Male'), ('female', 'Female')], default='undefined', max_length=255, null=True, validators=[django.core.validators.RegexValidator(message='Can only contain the letters a-z and underscores.', regex='^[a-zA-Z_][a-zA-Z_]*$'), utils.validators.non_python_keyword]),
        ),
        migrations.AlterField(
            model_name='otpcode',
            name='identifier',
            field=models.SlugField(choices=[('email_validation', 'Email Validation'), ('change_email_validation', 'Change Email Validation'), ('telephone_validation', 'Telephone Validation'), ('change_telephone_validation', 'Change Telephone Validation'), ('register_validation', 'Register Validation'), ('password_reset_validation', 'Password Reset Validation')], max_length=128, null=True, validators=[django.core.validators.RegexValidator(message="Code can only contain the letters a-z, A-Z, digits, and underscores, and can't start with a digit.", regex='^[a-zA-Z_][0-9a-zA-Z_]*$'), utils.validators.non_python_keyword]),
        ),
    ]
