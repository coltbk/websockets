from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from django.template import loader
from .models import SensorReading



def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def detail(request, reading_id):
    reading = get_object_or_404(SensorReading, pk=reading_id)
    return render(request, "sensors/detail.html", {"reading": reading})
