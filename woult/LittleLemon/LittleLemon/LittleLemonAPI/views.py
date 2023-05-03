from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User, Group

from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, BasePermission
from rest_framework.pagination import PageNumberPagination
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from .models import Category, MenuItem, Cart, Order, OrderItem
from .serializers import MenuItemSerializer, CategorySerializer, ManagerSerializer, DeliveryCrewSerializer, CartSerializer, CartAddSerializer, OrderSerializer, SingleOrderSerializer, OrderPutSerializer

import math
from datetime import date


# Create your views here.
class IsManager(BasePermission):
    def has_permission(self, request, view):
       if request.user.groups.filter(name='Manager').exists():
            return True

class IsDeliveryCrew(BasePermission):
    def has_permission(self, request, view):
       if request.user.groups.filter(name='Delivery crew').exists():
            return True

class MenuItemPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'perpage'
    max_page_size = 20
    page_query_param = 'page'


class CategoriesView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser | IsManager]


class MenuItemsView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    pagination_class = MenuItemPagination
    ordering_fields=['price','category']
    search_fields = ['title','category__title']

    def get_permissions(self):
        permission_classes = []
        if self.request.method != 'GET':
            permission_classes = [IsAuthenticated, IsAdminUser | IsManager]
        return[permission() for permission in permission_classes]

        
class SingleMenuItemsView(generics.RetrieveUpdateDestroyAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
        
    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.request.method == 'PATCH' or "DELETE":
            permission_classes = [IsAuthenticated, IsAdminUser | IsManager]
        return[permission() for permission in permission_classes]

    def patch(self, request, pk, format=None):
        menuitem = MenuItem.objects.get(pk=self.kwargs['pk'])
        menuitem.save()
        return Response(status=status.HTTP_200_OK)


class ManagersView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = User.objects.filter(groups__name='Manager')
    serializer_class = ManagerSerializer
    permission_classes = [IsAuthenticated, IsAdminUser | IsManager]

    def post(self, request, *args, **kwargs):
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            managers = Group.objects.get(name='Manager')
            managers.user_set.add(user)
            return Response({"message": "User added to Manager group."},status=status.HTTP_201_CREATED)


class ManagersRemoveView(generics.DestroyAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = User.objects.filter(groups__name='Manager')
    permission_classes = [IsAuthenticated, IsAdminUser | IsManager]

    def delete(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        user = get_object_or_404(User, pk=pk)
        managers = Group.objects.get(name='Manager')
        managers.user_set.remove(user)
        return Response({"message": "User removed from Manager group."},status=status.HTTP_200_OK)


class DeliveryCrewView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = User.objects.filter(groups__name='Delivery crew')
    serializer_class = DeliveryCrewSerializer
    permission_classes = [IsAuthenticated, IsAdminUser | IsManager]

    def post(self, request, *args, **kwargs):
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            delivery = Group.objects.get(name='Delivery crew')
            delivery.user_set.add(user)
            return Response({"message": "User added to Delivery crew group."},status=status.HTTP_201_CREATED)


class DeliveryCrewRemoveView(generics.DestroyAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = User.objects.filter(groups__name='Delivery crew')
    permission_classes = [IsAuthenticated, IsAdminUser | IsManager]

    def delete(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        user = get_object_or_404(User, pk=pk)
        delivery = Group.objects.get(name='Delivery crew')
        delivery.user_set.remove(user)
        return Response({"message": "User removed from Delivery crew group."},status=status.HTTP_200_OK)


class CartView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self, *args, **kwargs):
        cart = Cart.objects.filter(user=self.request.user)
        return cart

    def post(self, request, *arg, **kwargs):
        serialized_item = CartAddSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        id = request.data['menuitem']
        quantity = request.data['quantity']
        item = get_object_or_404(MenuItem, id=id)
        price = int(quantity) * item.price

        Cart.objects.create(user=request.user, menuitem_id=id, quantity=quantity, unit_price=item.price, price=price)
        return Response({'message':'Item added to cart'}, status.HTTP_201_CREATED)

    def delete(self, request, *arg, **kwargs):
        Cart.objects.filter(user=request.user).delete()
        return Response({'message':'All Items removed from cart'}, status.HTTP_201_CREATED)


class OrderView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = OrderSerializer
        
    def get_queryset(self, *args, **kwargs):
        if self.request.user.groups.filter(name='Manager').exists() or self.request.user.is_superuser == True :
            query = Order.objects.all()
        elif self.request.user.groups.filter(name='Delivery crew').exists():
            query = Order.objects.filter(delivery_crew=self.request.user)
        else:
            query = Order.objects.filter(user=self.request.user)
        return query

    def get_permissions(self):
        if self.request.method == 'GET' or 'POST' : 
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated, IsAdminUser | IsManager]
        return[permission() for permission in permission_classes]

    def post(self, request, *args, **kwargs):
        cart = Cart.objects.filter(user=request.user)
        x=cart.values_list()
        if len(x) == 0:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        total = math.fsum([float(x[-1]) for x in x])
        order = Order.objects.create(user=request.user, status=False, total=total, date=date.today())
        for i in cart.values():
            menuitem = get_object_or_404(MenuItem, id=i['menuitem_id'])
            orderitem = OrderItem.objects.create(order=order, menuitem=menuitem, quantity=i['quantity'])
            orderitem.save()
        cart.delete()
        return Response({'message':'Order #{} created'.format(str(order.id))}, status.HTTP_201_CREATED)


class SingleOrderView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = SingleOrderSerializer
    
    def get_permissions(self):
        order = Order.objects.get(pk=self.kwargs['pk'])
        if self.request.user == order.user and self.request.method == 'GET':
            permission_classes = [IsAuthenticated]
        elif self.request.method == 'PUT' or self.request.method == 'DELETE':
            permission_classes = [IsAuthenticated, IsAdminUser | IsManager]
        else:
            permission_classes = [IsAuthenticated, IsAdminUser | IsManager | IsDeliveryCrew]
        return[permission() for permission in permission_classes] 

    def get_queryset(self, *args, **kwargs):
            query = OrderItem.objects.filter(order_id=self.kwargs['pk'])
            return query

    def patch(self, request, *args, **kwargs):
        order = Order.objects.get(pk=self.kwargs['pk'])
        order.status = not order.status
        order.save()
        return Response({'message':'Order #'+ str(order.id)+'s\' status changed to '+str(order.status)}, status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        serialized_item = OrderPutSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        order_pk = self.kwargs['pk']
        crew_pk = request.data['delivery_crew'] 
        order = get_object_or_404(Order, pk=order_pk)
        crew = get_object_or_404(User, pk=crew_pk)
        order.delivery_crew = crew
        order.save()
        return Response({'message':str(crew.username)+' was assigned to order #'+str(order.id)}, status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        order = Order.objects.get(pk=self.kwargs['pk'])
        order_number = str(order.id)
        order.delete()
        return Response({'message':'Order #{} was deleted'.format(order_number)}, status.HTTP_200_OK)

