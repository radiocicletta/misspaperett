from django.contrib import admin
from .models import Request, SMTP

class RequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'event', 'requested_by', 'status')

admin.site.register(Request, RequestAdmin)
admin.site.register(SMTP)
