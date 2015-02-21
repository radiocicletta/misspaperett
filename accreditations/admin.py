from django.contrib import admin
from .models import Request, SMTP, IMAP, Message


class RequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'event', 'requested_by', 'status')


class SMTPAdmin(admin.ModelAdmin):
    list_display = ('host', 'port', 'user', 'use_ssl', 'use_tls')


class IMAPAdmin(admin.ModelAdmin):
    list_display = ('host', 'port', 'user', 'use_ssl')


class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'to', 'date')

admin.site.register(Request, RequestAdmin)
admin.site.register(SMTP, SMTPAdmin)
admin.site.register(IMAP, IMAPAdmin)
admin.site.register(Message, MessageAdmin)
