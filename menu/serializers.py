from rest_framework import serializers
from .models import (
    Category,
    Product,
    Table,
    Order,
    OptionType,
    Option, OrderItem
)

# Категория
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


# Продукт
class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )

    class Meta:
        model = Product
        fields = "__all__"


# Столик
class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = "__all__"
        read_only_fields = ['qr_token']


# Заказ



# Тип опции (например: крепость, вкус и т.д.)
class OptionTypeSerializer(serializers.ModelSerializer):
    applies_to = CategorySerializer(many=True, read_only=True)
    applies_to_ids = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        many=True,
        source='applies_to',
        write_only=True
    )

    class Meta:
        model = OptionType
        fields = "__all__"


# Конкретная опция (например: "лёгкий", "яблоко", "с мятой")
class OptionSerializer(serializers.ModelSerializer):
    type = OptionTypeSerializer(read_only=True)
    type_id = serializers.PrimaryKeyRelatedField(
        queryset=OptionType.objects.all(),
        source='type',
        write_only=True
    )

    class Meta:
        model = Option
        fields = "__all__"


class OrderItemInlineSerializer(serializers.ModelSerializer):
    product = serializers.StringRelatedField()
    options = serializers.StringRelatedField(many=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = "__all__"

    def get_total_price(self, obj):
        product_price = obj.product.price
        options_price = sum([opt.price or 0 for opt in obj.options.all()])
        total = (product_price + options_price) * obj.quantity
        return total

class OrderSerializer(serializers.ModelSerializer):
    table = TableSerializer(read_only=True)
    table_id = serializers.PrimaryKeyRelatedField(
        queryset=Table.objects.all(),
        source='table',
        write_only=True
    )
    items = OrderItemInlineSerializer(many=True, read_only=True, source='order_items')  # ключ: source='order_items'

    class Meta:
        model = Order
        fields ="__all__"


class OrderItemSerializer(serializers.ModelSerializer):
    options = serializers.PrimaryKeyRelatedField(queryset=Option.objects.all(), many=True)
    table_id = serializers.PrimaryKeyRelatedField(
        queryset=Table.objects.all(),
        write_only=True
    )
    quantity = serializers.IntegerField(required=False, default=1, min_value=1)
    class Meta:
        model = OrderItem
        fields = "__all__"
        extra_kwargs = {
            'order': {'read_only': True},
        }


