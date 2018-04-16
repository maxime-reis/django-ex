import os
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse

from . import database
from .models import PageView

# Create your views here.

def index(request):
    hostname = os.getenv('HOSTNAME', 'unknown')
    PageView.objects.create(hostname=hostname)

    adfs_groups = [request.META[key] for key in request.META if key.startswith('ADFS_GROUP')]

    return render(request, 'welcome/index.html', {
        'hostname': hostname,
        'database': database.info(),
        'count': PageView.objects.count(),
        'user': request.user,
        'groups': adfs_groups,
    })

def health(request):
    return HttpResponse(PageView.objects.count())
