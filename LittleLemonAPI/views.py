from django.shortcuts import render
from .models import MenuItem
from .serializers import MenuItemSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

# Create your views here.
class MenuItemList(APIView):
    """
    View list of menu items in the system.

    * Only Manager user can create new menu items.
    """
    def get(self, request):
        items = MenuItem.objects.all()
        serialized_item = MenuItemSerializer(items, many=True)
        return Response(serialized_item.data, status.HTTP_200_OK)
    
    def post(self, request):
        if request.user.groups.filter(name="Manager").exists():
            title = request.POST.get('title')
            price = request.POST.get('price')
            featured = request.POST.get('featured')
            category = request.POST.get('category')
            menu_item = MenuItem(
                title = title,
                author = price,
                featured = featured,
                category = category,
            )
            try:
                menu_item.save()
                return Response(status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": e}, status.HTTP_500_INTERNAL_SERVER_ERROR)

        else:
            return Response({"message": "this operation is permited!"}, status.HTTP_403_FORBIDDEN)
    
    def put(self, request):
        return Response({"message": "this operation is permited!"}, status.HTTP_403_FORBIDDEN)
    
    def patch(self, request):
        return Response({"message": "this operation is permited!"}, status.HTTP_403_FORBIDDEN)
    
    def delete(self, request):
        return Response({"message": "this operation is permited!"}, status.HTTP_403_FORBIDDEN)
