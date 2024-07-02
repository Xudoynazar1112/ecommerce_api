from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    def reduce_stock(self, amount):
        if amount > self.stock:
            return False

        self.stock -= amount
        self.save()
        return True

    def increase_stock(self, amount):
        self.stock += amount
        self.save()

    class Meta:
        ordering = ['name']


class Order(models.Model):
    PENDING = 'Pending'
    PROCESSING = 'Processing'
    SHIPPED = 'Shipped'
    DELIVERED = 'Delivered'
    CANCELED = 'Canceled'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (PROCESSING, 'Processing'),
        (SHIPPED, 'Shipped'),
        (DELIVERED, 'Delivered'),
        (CANCELED, 'Canceled')
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices=STATUS_CHOICES, default=PENDING, max_length=10)

    def set_status(self, new_status):
        if new_status not in dict(self.STATUS_CHOICES):
            raise ValueError("Invalid status")
        self.status = new_status
        self.save()

    def is_transition_allowed(self, new_status):
        allowed_transitions = {
            self.PENDING: [self.PROCESSING, self.CANCELED],
            self.PROCESSING: [self.SHIPPED, self.CANCELED],
            self.SHIPPED: [self.DELIVERED, self.CANCELED]
        }

        return new_status in allowed_transitions.get(self.status, [])

    def __str__(self):
        return f"Order({self.product.name} by {self.customer.username})"


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    body = models.TextField()
    rating = models.DecimalField(max_digits=1, decimal_places=1)
    posted_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.rating}"


class FlashSale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    discount_percentage = models.PositiveIntegerField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def is_active(self):
        now = timezone.now()
        return self.start_date <= now <= self.end_date

    class Meta:
        unique_together = ('product', 'start_date', 'end_date')


class ProductViewHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)