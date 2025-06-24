from menu.models import OrderItem


def get_hookah_orders():
    return (
        OrderItem.objects
        .select_related('order', 'product__category')
        .filter(product__category__name='Кальяны', order__status='open')
        .order_by('-order__created_at')
    )


def mark_order_item_as_done(item_id):
    # Здесь ты можешь реализовать обновление статуса или отметку
    print(f"Marked item {item_id} as done.")
    # Пример: OrderItem.objects.filter(id=item_id).update(status='done')
