# Generated by Django 4.0.3 on 2022-10-23 17:18

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Profile', '0003_alter_profile_enrollmentid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='branch',
            field=models.CharField(default='', max_length=4),
        ),
        migrations.AlterField(
            model_name='profile',
            name='studentId',
            field=models.IntegerField(default=0, max_length=5, validators=[django.core.validators.MinLengthValidator(5)]),
        ),
    ]
