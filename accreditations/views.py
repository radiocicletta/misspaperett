from django.shortcuts import render
from django.template.loader import render_to_string
from .models import Request, IMAP, Message
from datetime import datetime
from django.db.models import Q
from django.contrib import messages
import re
from .utils import create_message
from flanker.addresslib import address
from django.contrib.auth.decorators import login_required


@login_required
def view(request, reqid=None):
    if reqid:
        req = Request.objects.filter(id=reqid).get()
        if req.status == Request.BLOCKED:
            messages.add_message(
                request,
                messages.ERROR,
                "Questa richiesta &egrave; bloccata"
            )
    else:
        req = None
    return render(
        request,
        "accreditations/form.html",
        {"req": req}
    )


@login_required
def close(request, reqid=None):
    if request.user.is_staff:
        req = Request.objects.filter(id=reqid).get()
        req.status = Request.CLOSED
        req.save()
    else:
        messages.add_message(request, messages.ERROR, "Solo gli addetti possono usare questa azione")
    return view(request, reqid)


@login_required
def block(request, reqid=None):
    if request.user.is_staff:
        req = Request.objects.filter(id=reqid).get()
        req.status = Request.BLOCKED
        req.save()
    else:
        messages.add_message(request, messages.ERROR, "Solo gli addetti possono usare questa azione")
    return view(request, reqid)


@login_required
def reply(request, reqid=None):
    if request.method == "POST":
        attribs = request.POST
    elif request.method == "GET":
        attribs = request.GET

    req = Request.objects.filter(id=reqid or attribs["reqid"]).get()
    msg_original = Message.objects.filter(id=attribs["mailid"]).get()
    names = attribs.getlist("requestname", [])
    link = "link" in attribs and attribs["link"] or None
    podcast = attribs.get("contenttype", None) == "podcast"
    article = attribs.get("contenttype", None) == "article"

    subject = "Re: " + re.sub(
        "^Re: ",
        "",
        re.search(
            "\nSubject: ([^\r\n]*)[\r\n]",
            msg_original.headers,
            re.M
        ).groups()[0]
    )
    imap = msg_original.imap
    now = datetime.now()
    quote = re.sub(
        "\n",
        "<br>\n&gt;",
        re.sub("<\/{0,1}[^>]+>", "", msg_original.body)
    )
    html_body = render_to_string(
        "reply_it.html",
        {
            "req": req,
            "imap": imap,
            "msg": msg_original,
            "quote": quote,
            "names": names,
            "podcast": podcast,
            "article": article,
            "link": link,
            "action": attribs["action"]
        })
    smtp = imap.smtp
    sender = [
        a.address for a in
        address.parse_list(
            msg_original.sender
        )
    ]
    smtp.send(
        re.sub("<\/{0,1}[^>]+>", "", html_body),
        imap.mail,
        sender,
        html_body,
        subject,
        {
            "In-Reply-To": msg_original.message_id,
            "References": msg_original.message_id
        }
    )
    msg = imap.thread_head(
        sender[0],
        now,
        subject
    )

    message = create_message(msg)

    message.sender = imap.mail
    message.to = msg_original.sender

    message.imap = imap
    message.smtp = smtp

    message.references = message

    message.request = req
    message.save()

    if attribs["action"] == "names":
        req.status = Request.ACCEPTED
    elif attribs["action"] == "link":
        req.status = Request.USED
    elif attribs["action"] == "thanks":
        req.status = Request.CLOSED

    req.save()

    return view(request, reqid or attribs["reqid"])


def index(request):
    return render(
        request,
        "accreditations/index.html",
        {
            "pending": Request.objects.filter(status__lte=Request.ACCEPTED),
            "complete": Request.objects.filter(status__gt=Request.ACCEPTED)
        }
    )


@login_required
def edit(request):
    if request.method == "POST":
        attribs = request.POST

        if not attribs['name'] or \
            not attribs['email'] or \
            not attribs['event'] or \
            not attribs['where'] or \
            not attribs['when'] or \
                not attribs['how']:

            messages.add_message(
                request,
                messages.ERROR,
                'Tutti i campi devono essere compilati'
            )
            return render(
                request,
                "accreditations/form.html",
            )

        accr_request = Request()
        accr_request.name_1 = attribs['name']
        accr_request.mail_1 = attribs['email']

        accr_request.event = attribs['event']
        accr_request.where = attribs['where']
        accr_request.when = datetime.strptime(attribs['when'], '%Y-%m-%d').date()
        #accr_request.when = attribs['when']

        accr_request.how = attribs['how']

        accr_request.requested_by = request.user

        opened = Request.objects.filter(
            Q(event__icontains=accr_request.event) |
            Q(mail_1__icontains=accr_request.event) |
            Q(where__icontains=accr_request.where) |
            Q(when=accr_request.when),
            status__lte=Request.USED
        )

        if len(opened):
            messages.add_message(
                request,
                messages.WARNING,
                'Alcune richieste di eventi ancora in corso hanno '
                'in comune alcune informazioni con questa richiesta. '
                'Verifica che la tua richiesta sia diversa da queste: '
                '<ul> ' + " ".join(
                    ['<li><a href="view/{}">{}</a></li>'.format(o.id, o) for o in opened]
                )
            )
            return render(
                request,
                "accreditations/form.html",
            )

        accr_request.status = Request.SENT
        accr_request.save()

        subject = "Richiesta Accredito Stampa"
        now = datetime.now()

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

            message = create_message(msg)

            message.sender = imap.mail
            message.to = accr_request.mail_1

            message.imap = imap
            message.smtp = smtp

            message.references = message

            message.request = accr_request
            message.save()

        return view(request, reqid=accr_request.id)
