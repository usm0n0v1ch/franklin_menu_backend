from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response

from menu.models import OrderItem
from telegrambot.serializers import TelegramOrderItemSerializer


@api_view(['GET'])
def new_orders(request):
    role = request.query_params.get('role')
    role_category_map = {
        'hookah': ['Кальяны'],
        'cook': ['Блюда'],
        'waiter': ['Напитки', 'Прочее'],
    }

    categories = role_category_map.get(role, [])
    order_items = OrderItem.objects.filter(
        is_done=False,
        order__status='open',
        product__category__name__in=categories
    ).select_related('product', 'order', 'product__category', 'order__table').prefetch_related('options__type')

    serializer = TelegramOrderItemSerializer(order_items, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def mark_done(request, item_id):
    try:
        item = OrderItem.objects.get(id=item_id)
        item.is_done = True
        item.done_at = timezone.now()  # сохраняем время
        item.save()
        return Response({"status": "ok", "done_at": item.done_at})
    except OrderItem.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
