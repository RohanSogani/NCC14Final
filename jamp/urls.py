from django.conf.urls import patterns, include, url
from login_db import views
from django.contrib import admin
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'jamp.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', RedirectView.as_view(url='ncc/')),
    url(r'^AsNRstyqJ63DT9VNjE92zngW/', include(admin.site.urls)),
    #url(r'^$', views.register_page),
    url(r'^ncc/',include('login_db.urls')),
    
)
