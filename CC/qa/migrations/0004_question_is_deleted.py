# Generated by Django 4.0.3 on 2022-11-04 12:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qa', '0003_answer_is_deleted'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
