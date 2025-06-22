from django.shortcuts import render

# Create your views here.
# telegrambot/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utils import send_message


@api_view(['POST'])
def call_waiter(request):
    table_id = request.data.get('table_id')
    if not table_id:
        return Response({'error': 'table_id is required'}, status=400)

    send_message(f"🛎 Столик #{table_id} вызывает официанта!")
    return Response({'status': 'called'})
