from django.conf.urls import patterns

from . import views

urlpatterns = patterns(
    '',
    (r'^/*$', views.index),
    (r'^new/(\d*)$', views.view),
    (r'^view/(\d*)$', views.view),
    (r'^close/(\d*)$', views.close),
    (r'^block/(\d*)$', views.block),
    (r'^reply/(\d*)$', views.reply),
    (r'^edit/*$', views.edit),
)
