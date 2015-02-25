from django.db import models
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.core.mail.backends.smtp import EmailBackend
import imaplib
from flanker import mime


class Request(models.Model):

    SENT, REPLY, ACCEPTED, USED, CONTENT, CLOSED, BLOCKED = (0, 1, 2, 3, 4, 5, 6)

    STATUS = (
        (SENT, 'Request Sent'),
        (REPLY, 'Reply'),
        (ACCEPTED, 'Accepted'),
        (USED, 'Used'),
        (CONTENT, 'Content Added'),
        (CLOSED, 'Closed'),
        (BLOCKED, 'Blocked')
    )

    LANG = (
        ('it', 'Italian'),
        ('en', 'English'),
    )

    status = models.IntegerField(choices=STATUS, default=0)
    language = models.CharField(choices=LANG, max_length=256)
    status_update = models.DateTimeField(auto_now=True)

    event = models.CharField(
        max_length=1024,
        blank=False,
        null=False,
        default="Event")
    where = models.CharField(
        max_length=1024,
        blank=False,
        null=False,
        default="Place")
    when = models.DateField()

    mail_1 = models.EmailField(blank=False, null=False, max_length=256)
    mail_2 = models.EmailField(max_length=256)
    mail_3 = models.EmailField(max_length=256)
    mail_4 = models.EmailField(max_length=256)

    name_1 = models.CharField(max_length=256)
    name_2 = models.CharField(max_length=256)
    name_3 = models.CharField(max_length=256)
    name_4 = models.CharField(max_length=256)

    office = models.CharField(max_length=256)


    requested_by = models.ForeignKey(User)
    how = models.IntegerField(default=1)

    def __unicode__(self):
        return "{what} @{where} ({when})".format(
            what=self.event,
            where=self.where,
            when=self.when
        )

    @property
    def url(self):
        return "view/" + str(self.id)


class SMTP(models.Model):

    host = models.CharField(max_length=256)
    port = models.IntegerField(default=25)
    user = models.CharField(max_length=256, default="anonymous")
    password = models.CharField(max_length=256, default="password")
    use_tls = models.BooleanField(default=False)
    use_ssl = models.BooleanField(default=False)

    def __unicode__(self):
        return "{user}@{host}:{port}".format(
            user=self.user,
            port=self.port,
            host=self.host
        )

    def send(self, message, from_email, recipient_list, html_message, subject='Richiesta Accredito Stampa', headers={}):

        backend = EmailBackend(
            self.host,
            self.port,
            self.user,
            self.password,
            self.use_tls,
            False,
            self.use_ssl
        )

        text_content = message
        html_content = html_message
        msg = EmailMultiAlternatives(
            subject,
            text_content,
            from_email,
            recipient_list,
            [],  # [from_email],  # bcc
            backend,
            [],  # attachments
            headers,
            []  # cc
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()


class IMAP(models.Model):

    host = models.CharField(max_length=256)
    port = models.IntegerField(default=imaplib.IMAP4_PORT)
    user = models.CharField(max_length=256, default="anonymous")
    password = models.CharField(max_length=256, default="password")
    use_ssl = models.BooleanField(default=False)

    mail = models.CharField(max_length=256, default="mail@example.com")

    inbox_folder = models.CharField(max_length=256, default="INBOX")
    sent_folder = models.CharField(max_length=256, default="Sent")

    smtp = models.OneToOneField(SMTP)

    signature = models.TextField(default="signature")
    organization = models.CharField(max_length=256, default="Organization")
    org_url = models.CharField(max_length=256, default="www.organization.url")
    org_description = models.CharField(max_length=256, default="Organization Description")


    def __unicode__(self):
        return "{user}@{host}:{port}".format(
            user=self.user,
            port=self.port,
            host=self.host
        )

    def _connect(self):

        if self.use_ssl:
            conn = imaplib.IMAP4_SSL(self.host, self.port)
        else:
            conn = imaplib.IMAP4(self.host, self.port)

        conn.login(self.user, self.password)
        return conn

    def _fetch(self, conn, uid):
        result, data = conn.uid("fetch", uid, "(RFC822)")
        if result == "OK":
            message = mime.from_string(data[0][1])
            return message
        else:
            raise Exception()

    def _head(self, conn, uid):
        try:
            result, data = conn.uid("fetch", uid, "(RFC822.HEADER)")
            if result == "OK":
                message = mime.from_string(data[0][1])
                return message
        except:
            result, data = conn.uid("fetch", uid, "(BODY.PEEK[])")
            if result == "OK":
                message = mime.from_string(data[0][1])
                return message

    def thread_head(self, to, date, subject):
        imap = self._connect()
        imap.select(str(self.sent_folder))

        result, data = imap.uid(
            'search',
            None,
            '(HEADER Subject "{subject}" '
            'HEADER To "{to}" '
            'SENTSINCE {date})'.format(
                subject=subject,
                to=to,
                date=date.strftime("%d-%b-%Y"))
        )

        if result == "OK":
            uid = data[0].split()[-1]
        else:
            raise Exception()

        return self._fetch(imap, uid)

    def thread_fetch(self, references):
        imap = self._connect()
        imap.select(str(self.inbox_folder))

        messages = []
        uids = []
        result, data = imap.uid(
            'search',
            None,
            '(UNSEEN)'
        )
        if result == 'OK':
            for uid in data[0].split():
                h = self._head(imap, uid)
                ref_id = set(
                    h.headers['references'] and
                    h.headers['references'].split() or
                    []).union(
                    set(h.headers['in-reply-to'] and
                        h.headers['in-reply-to'].split() or
                        [])
                )
                for r in ref_id:
                    if r in references:
                        uids.append(uid)
                        break

        for uid in uids:
            messages.append(self._fetch(imap, uid))
        return messages


class Message(models.Model):

    headers = models.TextField()
    body = models.TextField()
    sender = models.CharField(max_length=256, default="anonymous")
    to = models.CharField(max_length=256, default="anonymous")
    message_id = models.CharField(max_length=512, default="-1")

    content_type = models.CharField(max_length=128, default="text/html")
    date = models.DateTimeField(auto_now=True)

    imap = models.ForeignKey(IMAP)
    smtp = models.ForeignKey(SMTP)

    references = models.ForeignKey('self', null=True, related_name="refs")
    request = models.ForeignKey(Request, null=True, related_name="messages")

    def __unicode__(self):
        return self.message_id
