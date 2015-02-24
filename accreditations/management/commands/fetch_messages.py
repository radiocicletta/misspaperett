from django.core.management.base import NoArgsCommand
from accreditations.models import Message, Request
from accreditations.utils import create_message


class Command(NoArgsCommand):

    def handle_noargs(self, *args, **options):
        for req in Request.objects.filter(status__lt=Request.CLOSED):
            messages = sorted(
                list(req.messages.all()),
                lambda x, y: x > y and 1 or -1
            )
            imap = messages[0].imap
            references = [r.message_id for r in messages]
            for msg in imap.thread_fetch(references):
                if not Message.objects.filter(message_id=msg.headers["message-id"]):

                    message = create_message(msg)

                    message.sender = msg.headers['from']
                    message.to = msg.headers['to']

                    message.imap = messages[0].imap
                    message.smtp = messages[0].smtp

                    message.refs.add(*list(Message.objects.filter(
                        message_id__in=msg.headers["message-id"])))

                    message.request = req
                    if req.status <= Request.SENT:
                        req.status = Request.REPLY
                    message.save()
                    print message
