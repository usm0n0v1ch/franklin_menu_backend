from rest_framework import serializers
from menu.models import OrderItem, Option

class OptionMiniSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()

    class Meta:
        model = Option
        fields = ['name', 'type']

    def get_type(self, obj):
        return obj.type.name

class TelegramOrderItemSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    order = serializers.SerializerMethodField()
    options = OptionMiniSerializer(many=True)
    is_done = serializers.BooleanField()
    done_at = serializers.DateTimeField(format='%H:%M %d-%m-%Y', required=False, allow_null=True)

    class Meta:
        model = OrderItem
        fields = "__all__"

    def get_product(self, obj):
        return {
            'name': obj.product.name,
            'price': float(obj.product.price)
        }

    def get_order(self, obj):
        return {
            'table': obj.order.table.number,
            'created_at': obj.order.created_at.strftime('%H:%M %d-%m-%Y')
        }
