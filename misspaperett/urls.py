from django.conf.urls import patterns, include, url
from django.contrib import admin
from accreditations import urls

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'misspaperett.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    (r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'registration/login.html'}),
    (r'^logout/$', 'django.contrib.auth.views.logout', {'template_name': 'registration/login.html'}),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^djangojs/', include('djangojs.urls')),
) + urls.urlpatterns
