# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import onetomany.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('django_mailbox', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(max_length=256, choices=[(0, b'Request Sent'), (1, b'Reply'), (2, b'Accepted'), (3, b'Used'), (4, b'Content Added')])),
                ('language', models.CharField(max_length=256, choices=[(b'it', b'Italian'), (b'en', b'English')])),
                ('status_update', models.DateTimeField(auto_now=True)),
                ('event', models.CharField(default=b'Event', max_length=1024)),
                ('where', models.CharField(default=b'Place', max_length=1024)),
                ('when', models.DateTimeField(auto_now=True)),
                ('mail_1', models.EmailField(max_length=256)),
                ('mail_2', models.EmailField(max_length=256)),
                ('mail_3', models.EmailField(max_length=256)),
                ('mail_4', models.EmailField(max_length=256)),
                ('name_1', models.CharField(max_length=256)),
                ('name_2', models.CharField(max_length=256)),
                ('name_3', models.CharField(max_length=256)),
                ('name_4', models.CharField(max_length=256)),
                ('office', models.CharField(max_length=256)),
                ('messages', onetomany.models.OneToManyField(to='django_mailbox.Message')),
                ('requested_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SMTP',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('host', models.CharField(max_length=256)),
                ('port', models.IntegerField(default=25)),
                ('user', models.CharField(default=b'anonymous', max_length=256)),
                ('password', models.CharField(default=b'password', max_length=256)),
                ('use_tls', models.BooleanField(default=False)),
                ('use_ssl', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
