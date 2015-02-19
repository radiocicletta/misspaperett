from django.conf.urls import patterns

from . import views

urlpatterns = patterns(
    '',
    (r'^view/(\d*)$', views.view),
    (r'^edit$', views.edit),
)
