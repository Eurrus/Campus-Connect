# Generated by Django 4.0.3 on 2022-10-23 17:21

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Profile', '0004_alter_profile_branch_alter_profile_studentid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='studentId',
            field=models.IntegerField(default=10000, max_length=5, validators=[django.core.validators.MaxValueValidator(99999), django.core.validators.MinValueValidator(10000)]),
        ),
    ]
