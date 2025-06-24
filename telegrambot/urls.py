from django.urls import path
from . import views

urlpatterns = [
    path('new_orders/', views.new_orders),
    path('mark_done/<int:item_id>/', views.mark_done),
]
