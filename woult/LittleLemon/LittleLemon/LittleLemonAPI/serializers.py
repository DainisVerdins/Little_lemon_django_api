from rest_framework import serializers
from .models import Category, MenuItem, Cart, Order, OrderItem
from django.contrib.auth.models import User

class CategorySerializer (serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','title']

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category']

class ManagerSerializer(serializers.ModelSerializer):
    class Meta():
        model = User
        fields = ['id','username','email']

class DeliveryCrewSerializer(serializers.ModelSerializer):
    class Meta():
        model = User
        fields = ['id','username','email']

class CartMenuItemSerializer(serializers.ModelSerializer):
    class Meta():
        model = MenuItem
        fields = ['id','title','price']

class CartSerializer(serializers.ModelSerializer):
    menuitem = CartMenuItemSerializer()
    class Meta():
        model = Cart
        fields = ['menuitem','quantity','price']
        
class CartAddSerializer(serializers.ModelSerializer):
    class Meta():
        model = Cart
        fields = ['menuitem','quantity']
        extra_kwargs = {
            'quantity': {'min_value': 1},
        }

class UserSerializer(serializers.ModelSerializer):
    class Meta():
        model = User
        fields = ['username']

class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta():
        model = Order
        fields = ['id','user','total','status','delivery_crew','date']

class OrderMenuItemSerializer(serializers.ModelSerializer):
    class Meta():
        model = MenuItem
        fields = ['title','price']

class SingleOrderSerializer(serializers.ModelSerializer):
    menuitem = OrderMenuItemSerializer()
    class Meta():
        model = OrderItem
        fields = ['menuitem','quantity']

class OrderPutSerializer(serializers.ModelSerializer):
    class Meta():
        model = Order
        fields = ['delivery_crew']