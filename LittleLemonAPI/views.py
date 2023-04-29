from django.shortcuts import render, get_object_or_404
from .models import MenuItem, Category, Cart
from .serializers import MenuItemSerializer, UserSerializer, CartSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth.models import Group, User

# Create your views here.


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def menu_items(request):
    """
    View list of menu items in the system.

    * Only Manager user can create new menu items.
    """

    if request.method == 'GET':
        items = MenuItem.objects.all()
        serialized_item = MenuItemSerializer(items, many=True)

        return Response(serialized_item.data, status.HTTP_200_OK)

    elif request.method == 'POST':
        if request.user.groups.filter(name="Manager").exists():
            title = request.POST.get('title')
            price = request.POST.get('price')
            featured = request.POST.get('featured')
            categoryId = request.POST.get('category')

            category = Category.objects.get(pk=categoryId)
            menu_item = MenuItem(
                title=title,
                price=price,
                featured=bool(featured),
                category=category
            )
            try:
                menu_item.save()
                return Response(status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": e}, status.HTTP_500_INTERNAL_SERVER_ERROR)

        else:
            return Response({"message": "this operation is permited!"}, status.HTTP_403_FORBIDDEN)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def menu_item(request, menuItem):

    try:
        item = MenuItem.objects.get(pk=menuItem)
    except MenuItem.DoesNotExist:
        return Response(status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serialized_item = MenuItemSerializer(item, many=False)

        return Response(serialized_item.data, status.HTTP_200_OK)

    if request.method == 'PUT':
        if request.user.groups.filter(name="Manager").exists():
            serializer = MenuItemSerializer(item, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(status.HTTP_200_OK)

        return Response({"message": "this operation is permited!"}, status.HTTP_403_FORBIDDEN)

    if request.method == 'PATCH':
        if request.user.groups.filter(name="Manager").exists():
            serializer = MenuItemSerializer(item, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(status.HTTP_200_OK)

        return Response({"message": "this operation is permited!"}, status.HTTP_403_FORBIDDEN)

    if request.method == 'DELETE':
        if request.user.groups.filter(name="Manager").exists():
            item.delete()
            return Response(serialized_item.data, status.HTTP_200_OK)

        return Response({"message": "this operation is permited!"}, status.HTTP_403_FORBIDDEN)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def managers_group_view(request):
    """
        view for user with Manager role to assign or see all managers in system.

    * [GET] Only Manager user can get a list of Managers in system.
    * [POST] Only Manager could assign via POST method new Manager to system from payload aka body
    """
    if request.user.groups.filter(name="Manager").exists():
        if request.method == 'GET':
            managers = User.objects.filter(groups__name='Manager')
            serialized_item = UserSerializer(managers, many=True)

            return Response(serialized_item.data, status.HTTP_200_OK)

        if request.method == 'POST':
            username = request.data['username']

            if username:
                user = get_object_or_404(User, username=username)
                managers = Group.objects.get(name='Manager')
                managers.user_set.add(user)
                return Response(status.HTTP_201_CREATED)

    else:
        return Response({'message': 'this operation is permited!'}, status.HTTP_403_FORBIDDEN)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def manager_view(request, userId):
    """
    View to delete user with Manager role, only users with Manager role could do that.

    * [DELETE] Removes this particular user from the manager group
    """
    if request.user.groups.filter(name="Manager").exists():
        user = get_object_or_404(User, id=userId)
        if request.method == 'DELETE':
            managers = Group.objects.get(name='Manager')
            managers.user_set.remove(user)

            return Response(status.HTTP_200_OK)

    else:
        return Response({'message': 'this operation is permited!'}, status.HTTP_403_FORBIDDEN)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def delivery_crew_view(request):
    """
    View for user with Manager role to manipulate with user with role delivery_crew.

    * [GET] Get list of all users with role delivery crew.
    * [POST] Assign user to delivery crew
    """
    if request.user.groups.filter(name='Manager').exists():
        if request.method == 'GET':
            deliver_crews = User.objects.filter(groups__name='Delivery crew')
            serialized_item = UserSerializer(deliver_crews, many=True)

            return Response(serialized_item.data, status.HTTP_200_OK)

        if request.method == 'POST':
            username = request.data['username']

            if username:
                user = get_object_or_404(User, username=username)
                # TODO: make group names as constants
                delivery_crews = Group.objects.get(name='Delivery crew')
                delivery_crews.user_set.add(user)
                return Response(status.HTTP_201_CREATED)
            else:
                return Response({'message': 'no user name was provided in payload!'}, status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'message': 'this operation is permited!'}, status.HTTP_403_FORBIDDEN)


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def cart_management_view(request):
    """
        Cart managment view for Customers and authenticated users
        
        * [GET] Returns current items in the cart for the current user 
        * [POST] Adds the menu item to the cart.
        * [DELETE] Deletes all menu items created by the current user token
    """
    if request.method == 'GET':
        menu_items = Cart.objects.get(user__username=request.user).menuitem
        serialized_item = MenuItemSerializer(menu_items, many=False)

        return Response(serialized_item.data, status.HTTP_200_OK)

    if request.method == 'POST':
        menuitem_id = request.POST.get('menuitem_id')
        quantity = request.POST.get('quantity')
        unit_price = request.POST.get('unit_price')
        price = request.POST.get('price')

        users_cart = Cart.objects.get(user__username=request.user)
        menuitem = get_object_or_404(MenuItem,pk=menuitem_id)

        users_cart.menuitem = menuitem
        users_cart.quantity = quantity
        users_cart.unit_price = unit_price
        users_cart.price= price

        users_cart.save()


        return Response(status.HTTP_201_CREATED)

    if request.method == 'DELETE':

        user_cart = Cart.objects.get(user__username=request.user)
        user_cart.menuitem = None

        return Response(status.HTTP_200_OK)
