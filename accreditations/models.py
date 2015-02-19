from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.core.mail.backends.smtp import EmailBackend
from onetomany.models import OneToManyField
from django_mailbox.models import Message


class Request(models.Model):

    STATUS = (
        (0, 'Request Sent'),
        (1, 'Reply'),
        (2, 'Accepted'),
        (3, 'Used'),
        (4, 'Content Added')
    )

    LANG = (
        ('it', 'Italian'),
        ('en', 'English'),
    )

    status = models.CharField(choices=STATUS, max_length=256)
    language = models.CharField(choices=LANG, max_length=256)
    status_update = models.DateTimeField(auto_now=True)

    event = models.CharField(max_length=1024, blank=False, null=False, default="Event")
    where = models.CharField(max_length=1024, blank=False, null=False, default="Place")
    when = models.DateTimeField(auto_now=True)

    mail_1 = models.EmailField(blank=False, null=False, max_length=256)
    mail_2 = models.EmailField(max_length=256)
    mail_3 = models.EmailField(max_length=256)
    mail_4 = models.EmailField(max_length=256)

    name_1 = models.CharField(max_length=256)
    name_2 = models.CharField(max_length=256)
    name_3 = models.CharField(max_length=256)
    name_4 = models.CharField(max_length=256)

    office = models.CharField(max_length=256)

    messages = OneToManyField(Message)

    requested_by = models.ForeignKey(User)


class SMTP(models.Model):

    host = models.CharField(max_length=256)
    port = models.IntegerField(default=25)
    user = models.CharField(max_length=256, default="anonymous")
    password = models.CharField(max_length=256, default="password")
    use_tls = models.BooleanField(default=False)
    use_ssl = models.BooleanField(default=False)

    def send(self, message, from_email, recipient_list, html_message):

        backend = EmailBackend(
            self.host,
            self.port,
            self.user,
            self.password,
            self.use_tls,
            False,
            self.use_ssl
        )

        subject, from_email = 'Richiesta Accredito Stampa', from_email
        text_content = message
        html_content = html_message
        msg = EmailMultiAlternatives(
            subject,
            text_content,
            from_email,
            recipient_list,
            [from_email],  # bcc
            backend,
            [],  # attachments
            {},  # headers
            []  # cc
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
