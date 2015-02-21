from django.shortcuts import render
from django.template.loader import render_to_string
from .models import Request, IMAP, Message
from django.http import HttpResponseRedirect
from datetime import datetime
import re

def view(request, reqid=None):
    if reqid:
        req = Request.objects.filter(id=reqid).get()
    else:
        req = None
    return render(
        request,
        "accreditations/form.html",
        {"req": req}
    )


def edit(request):
    if request.method == "POST":
        attribs = request.POST

        print attribs

        accr_request = Request()
        accr_request.name_1 = attribs['name']
        accr_request.mail_1 = attribs['email']

        accr_request.event = attribs['event']
        accr_request.where = attribs['where']
        accr_request.when = attribs['when']

        accr_request.requested_by = request.user

        subject = "Richiesta Accredito Stampa"
        now = datetime.now()
        #messages = []

        accr_request.save()
        for imap in IMAP.objects.all():
            html_body = render_to_string(
                "message_it.html",
                {
                    "req": accr_request,
                    "imap": imap
                })
            smtp = imap.smtp
            smtp.send(
                re.sub("<\/{0,1}[^>]+>", "", html_body),
                imap.mail,
                [accr_request.mail_1],
                html_body,
                subject
            )
            msg = imap.thread_head(
                accr_request.mail_1,
                now,
                subject
            )

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

            message.sender = imap.mail
            message.to = accr_request.mail_1
            message.message_id = msg.headers["message-id"]


            message.imap = imap
            message.smtp = smtp

            message.references = message

            message.request = accr_request
            message.save()
            #messages.append(message)

        #for m in messages:
        #    accr_request.messages.add(m)

        return view(request, reqid=accr_request.id)
