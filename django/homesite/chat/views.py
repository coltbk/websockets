# chat/views.py
from django.shortcuts import render
from sensors.models import SensorReading


def index(request):
    return render(request, "chat/index.html")

def room(request, room_name):
    return render(request, "chat/room.html", {"room_name": room_name})

def test(request):
    return render(request, "chat/test.html")

def readings(request):
    latest_readings_list = SensorReading.objects.latest("datetime")[:5]
    context = {"latest_question_list": latest_readings_list}
    return render(request, "chat/readings.html", context)
