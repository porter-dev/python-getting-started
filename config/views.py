import django
from django.shortcuts import render


def index(request):
    return render(request, 'index.html', {'django_version': django.get_version()})
