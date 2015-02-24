from django.conf.urls import patterns

from . import views

urlpatterns = patterns(
    '',
    (r'^/*$', views.index),
    (r'^view/(\d*)$', views.view),
    (r'^close/(\d*)$', views.close),
    (r'^block/(\d*)$', views.block),
    (r'^reply/*$', views.reply),
    (r'^edit/*$', views.edit),
)
