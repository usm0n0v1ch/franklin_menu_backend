import requests
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Category,
    Product,
    Table,
    Order,
    OptionType,
    Option, OrderItem
)
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    TableSerializer,
    OrderSerializer,
    OptionTypeSerializer,
    OptionSerializer, OrderItemSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class TableViewSet(viewsets.ModelViewSet):
    queryset = Table.objects.all()
    serializer_class = TableSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def create(self, request, *args, **kwargs):
        table_id = request.data.get('table_id')

        if not table_id:
            return Response({"error": "table_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            table = Table.objects.get(id=table_id)
        except Table.DoesNotExist:
            return Response({"error": "Invalid table_id"}, status=status.HTTP_404_NOT_FOUND)

        # Проверяем, есть ли открытый заказ
        open_order = table.orders.filter(status='open').first()

        if open_order:
            # Если заказ уже есть — возвращаем его
            serializer = self.get_serializer(open_order)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Иначе — создаём новый
        new_order = Order.objects.create(table=table)
        serializer = self.get_serializer(new_order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OptionTypeViewSet(viewsets.ModelViewSet):
    queryset = OptionType.objects.all()
    serializer_class = OptionTypeSerializer


class OptionViewSet(viewsets.ModelViewSet):
    queryset = Option.objects.all()
    serializer_class = OptionSerializer

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

    def create(self, request, *args, **kwargs):
        table_id = request.data.get('table_id')
        product_id = request.data.get('product')
        quantity = request.data.get('quantity', 1)  # 🔹 Вот здесь получаем quantity
        options = request.data.get('options', [])

        if not table_id or not product_id:
            return Response({"error": "table_id and product are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            table = Table.objects.get(id=table_id)
        except Table.DoesNotExist:
            return Response({"error": "Invalid table_id"}, status=status.HTTP_404_NOT_FOUND)

        # Проверяем существующий открытый заказ
        order = table.orders.filter(status='open').first()
        if not order:
            order = Order.objects.create(table=table)

        # ✅ Передаём quantity при создании
        order_item = OrderItem.objects.create(
            order=order,
            product_id=product_id,
            quantity=quantity  # 🔥 Фикс здесь
        )

        if options:
            order_item.options.set(options)

        serializer = self.get_serializer(order_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)



class TableFromTokenView(APIView):
    def get(self, request, token):
        try:
            table = Table.objects.get(qr_token=token)
            return Response({"table_id": table.id})
        except Table.DoesNotExist:
            return Response({"error": "Invalid token"}, status=status.HTTP_404_NOT_FOUND)





