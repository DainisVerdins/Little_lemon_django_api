from django.shortcuts import render
from .models import MenuItem, Category
from .serializers import MenuItemSerializer
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

# Create your views here.
@api_view(['GET','POST'])
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
                title = title,
                price = price,
                featured = bool(featured),
                category = category
            )
            try:
                menu_item.save()
                return Response(status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": e}, status.HTTP_500_INTERNAL_SERVER_ERROR)

        else:
            return Response({"message": "this operation is permited!"}, status.HTTP_403_FORBIDDEN)

@api_view(['GET','PUT','PATCH','DELETE'])
def menu_item(request, pk):

    try:
        item = MenuItem.objects.get(pk=pk)
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