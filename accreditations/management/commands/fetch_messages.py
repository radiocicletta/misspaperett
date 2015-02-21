from django.core.management.base import NoArgsCommand
from accreditations.models import Message, Request


class Command(NoArgsCommand):

    def handle_noargs(self, *args, **options):
        for req in Request.objects.filter(status__lte=4):
            messages = sorted(
                list(req.messages.all()),
                lambda x, y: x > y and 1 or -1
            )
            imap = messages[0].imap
            references = [r.message_id for r in messages]
            for msg in imap.thread_fetch(references):
                if not Message.objects.filter(message_id=msg.headers["message-id"]):

                    message = Message()
                    message.headers = msg.to_string()
                    if msg.content_type.is_singlepart():
                        message.body = msg.body
                        message.content_type = msg.content_type[0]
                    elif msg.content_type.is_multipart():
                        for part in msg.parts:
                            message.body = part.body
                            message.content_type = part.content_type[0]
                            if part.content_type.sub == "html":
                                break

                    message.sender = msg.headers['from']
                    message.to = msg.headers['to']
                    message.message_id = msg.headers["message-id"]

                    message.imap = messages[0].imap
                    message.smtp = messages[0].smtp

                    message.refs.add(*list(Message.objects.filter(
                        message_id__in=msg.headers["message-id"])))

                    message.request = req
                    message.save()
                    print message
