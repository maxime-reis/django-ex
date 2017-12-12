from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^cpu$', views.cpu_benchmarks, name='cpu_benchmarks'),
    url(r'^ssd$', views.ssd_benchmarks, name='ssd_benchmarks'),
    url(
        r'^import_benchmarks/$',
        views.import_benchmarks,
        name='import_benchmarks'
    ),
]
