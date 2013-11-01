from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
     url(r'^login/', 'django.contrib.auth.views.login'),
     url(r'^accounts/$','image.views.account_view'),
     url(r'^accounts/upload/', 'image.views.upload'),
     url(r'^encrypt/$', 'image.views.encrypt'),
     url(r'^decrypt/$', 'image.views.decrypt'),
     url(r'^delimg/$', 'image.views.del_img'),
     url(r'^tagimg/$', 'image.views.tag_img'),
     url(r'^deleteimg/$', 'image.views.delete_img'),
     url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)

