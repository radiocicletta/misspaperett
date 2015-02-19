from django.shortcuts import render
from .models import Request, SMTP
from django.http import HttpResponseRedirect

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

        accr_request.save()

        for smtp in SMTP.objects.all():
            smtp.send("test", "radiociclettatest@gmail.com", [accr_request.mail_1], "<div>Test</div>")

        return view(request, reqid=accr_request.id)
