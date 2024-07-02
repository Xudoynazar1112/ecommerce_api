from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from .models import Product, Category, Order, Review, ProductViewHistory


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'product', 'customer', 'quantity', 'created_at', 'status', 'total_price']

    def get_total_price(self, obj):
        return obj.product.price * obj.quantity

    def validate_quantity(self, value):
        try:
            # Fetch the product instance from the database
            product_id = self.initial_data['product']
            product = Product.objects.get(id=product_id)
            # Check the stock
            if value > product.stock:
                raise serializers.ValidationError("Not enough items in stock.")

            if value < 1:
                raise serializers.ValidationError("Quantity must be at least 1.")

            return value

        except ObjectDoesNotExist:
            raise serializers.ValidationError("Product does not exist")

    def create(self, validated_data):
        order = Order.objects.create(**validated_data)
        product = order.product
        product.stock -= order.quantity
        product.save()
        # self.send_confirmation_email(order)
        return order

    def cancel(self, id):
        order = Order.objects.get(id=id)
        product = order.product
        product.stock += order.quantity
        product.save()
        order.delete()
        return True


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'


class ProductViewHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductViewHistory
        fields = '__all__'