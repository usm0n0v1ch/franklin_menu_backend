# project/urls.py
from django.urls import path

from telegrambot.views import call_waiter


urlpatterns = [
    path("call-waiter/", call_waiter),
]
