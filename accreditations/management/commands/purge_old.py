from django.core.management.base import NoArgsCommand
from accreditations.models import Request
from datetime import date


class Command(NoArgsCommand):

    def handle_noargs(self, *args, **options):
        for req in Request.objects.filter(status__lt=Request.CLOSED, when__lt=date.today()):
            req.status = Request.CLOSED
            req.save()
            print "Closed", req
