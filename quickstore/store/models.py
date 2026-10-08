from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    mrp = models.DecimalField(max_digits=8, decimal_places=2)
    weight = models.CharField(max_length=50)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    stock = models.IntegerField(default=100)
    is_featured = models.BooleanField(default=False)

    @admin.display(description='Stock Status')
    def low_stock_alert(self):
        if self.stock < 10:
            return '⚠️ Low Stock'
        return '✅ In Stock'

    def __str__(self):
        return self.name


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=100, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.product.price * self.quantity


class Order(models.Model):
    STATUS_CHOICES = (
        ('Order Placed', 'Order Placed'),
        ('Packing', 'Packing'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Delivered', 'Delivered'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=50, default='Order Placed')
    address = models.TextField()
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    delivery_partner = models.ForeignKey(
        User,
        related_name='deliveries',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        return f'Order #{self.id}'


class Invoice(models.Model):
    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name='invoice'
    )
    invoice_number = models.CharField(max_length=50, unique=True)
    item_total = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_fee = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )
    handling_fee = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )
    grand_total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Invoice #{self.invoice_number} for Order #{self.order.id}'


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    address = models.TextField(blank=True, null=True)
    is_gold_member = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name or "User"} ({self.phone or "No Phone"})'