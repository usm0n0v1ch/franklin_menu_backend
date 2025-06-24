from django.urls import path
from . import views

urlpatterns = [
    path('call-waiter/', views.call_waiter, name='call-waiter'),
    path('waiter-status/<int:table_id>/', views.waiter_status, name='waiter-status'),
    path('telegram-webhook/', views.telegram_webhook, name='telegram-webhook'),
]