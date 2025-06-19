from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    photo = models.ImageField(upload_to='products/', blank=True, null=True)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.category.name})"


class Table(models.Model):
    number = models.PositiveIntegerField(unique=True)
    qr_token = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return f"Столик {self.number}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('open', 'Открыт'),
        ('closed', 'Закрыт'),
    ]

    table = models.ForeignKey(Table, on_delete=models.PROTECT, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    closed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Order #{self.id} | {self.table} | {self.status}"


class OptionType(models.Model):
    name = models.CharField(max_length=100)  # напр. "Крепость", "Вкус", "Лёд"
    applies_to = models.ManyToManyField(Category, related_name='option_types')

    def __str__(self):
        return self.name


class Option(models.Model):
    type = models.ForeignKey(OptionType, on_delete=models.CASCADE, related_name='options')
    name = models.CharField(max_length=100)  # напр. "Лёгкий", "Арбуз", "С мятой"
    photo = models.ImageField(upload_to='options/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"{self.type.name}: {self.name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    options = models.ManyToManyField(Option, blank=True)


    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order #{self.order.id})"
