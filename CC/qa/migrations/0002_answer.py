# Generated by Django 4.0.3 on 2022-11-02 18:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import martor.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('qa', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('body', martor.models.MartorField()),
                ('accepted', models.BooleanField(default=False)),
                ('a_vote_downs', models.ManyToManyField(blank=True, related_name='a_vote_down', to=settings.AUTH_USER_MODEL)),
                ('a_vote_ups', models.ManyToManyField(blank=True, related_name='a_vote_up', to=settings.AUTH_USER_MODEL)),
                ('answer_owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('questionans', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='qa.question')),
            ],
        ),
    ]
