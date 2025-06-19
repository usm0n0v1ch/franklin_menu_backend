from django.contrib import admin
from .models import Table, Category, Product, Order, Option, OptionType, OrderItem

admin.site.register([Category, Product, Table, Order,OptionType, Option,OrderItem])
