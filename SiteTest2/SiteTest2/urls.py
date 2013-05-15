# -*- coding: utf-8 -*- 
from django.conf.urls import patterns, include, url
from django.conf import settings
import os

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'SiteTest2.views.home', name='home'),
    # url(r'^SiteTest2/', include('SiteTest2.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls))
	url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': 'D:\Programming\www\SiteTest2\SiteTest2\static'}),
	
	
)

urlpatterns += patterns('blog.views',
	url(r'^(?P<page_id>\d*)$', 'index'),
	url(r'^post/(?P<post_id>\d+)/$', 'post' ),
	url(r'^.*add_article/$', 'dealWithArticle'),
	url(r'^delete_article/$', 'delete_article'),
	url(r'^edit_article/(?P<post_id>\d+)$', 'dealWithArticle'),
	url(r'^test.*','testView'),
)
	
# if settings.DEBUG:
    # from django.conf.urls.static import static
    # urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT, show_indexes=True)