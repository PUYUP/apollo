# Generated by Django 3.0.7 on 2020-06-10 02:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learn', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activitylog',
            name='action_flag',
            field=models.PositiveSmallIntegerField(choices=[(1, 'ddition'), (2, 'Change'), (3, 'Deletion')], verbose_name='action flag'),
        ),
    ]
