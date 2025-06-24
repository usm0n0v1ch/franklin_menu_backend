from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import WaiterCall
from .telegram_config import TELEGRAM_TOKEN
from .utils import send_waiter_request, update_waiter_status
import json
import requests

@api_view(['POST'])
def call_waiter(request):
    table_id = request.data.get('table_id')
    if not table_id:
        return Response({'error': 'table_id is required'}, status=400)

    call = send_waiter_request(table_id)
    if call:
        return Response({
            'status': call.status,
            'called_at': call.called_at,
            'message_id': call.message_id
        })
    return Response({'error': 'Failed to call waiter'}, status=500)


@csrf_exempt
def telegram_webhook(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            callback_query = data.get('callback_query')

            if callback_query:
                message = callback_query.get('message', {})
                callback_data = callback_query.get('data')
                message_id = message.get('message_id')

                if callback_data and message_id:
                    action, table_id = callback_data.split('_')

                    # Подтверждаем нажатие кнопки
                    requests.post(
                        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/answerCallbackQuery",
                        json={'callback_query_id': callback_query['id']}
                    )

                    # Обновляем статус
                    if action == 'coming':
                        update_waiter_status(
                            table_id=int(table_id),
                            status='coming',
                            message_id=message_id
                        )

                    return JsonResponse({'status': 'ok'})

        except Exception as e:
            print(f"Webhook error: {str(e)}")

    return JsonResponse({'status': 'ok'})


@api_view(['GET'])
def waiter_status(request, table_id):
    call = WaiterCall.objects.filter(table_id=table_id).order_by('-called_at').first()

    if not call:
        return Response({'error': 'No calls found'}, status=404)

    return Response({
        'status': call.status,
        'called_at': call.called_at,
        'coming_at': call.coming_at,
        'arrived_at': call.arrived_at
    })