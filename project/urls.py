from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin

from welcome.views import index, health
#from benchmarks.views import home, ssd_benchmarks, cpu_benchmarks

urlpatterns = [
    # Examples:
    # url(r'^$', 'project.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', index),
    url(r'^health$', health),
    url(r'^admin/', include(admin.site.urls)),
#    url(r'^ssd$', ssd_benchmarks),
#    url(r'^cpu$', cpu_benchmarks),
#    url(r'^home$', home),
#    url(r'^benchmarks/', include('benchmarks.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
