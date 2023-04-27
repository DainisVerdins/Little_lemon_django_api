from django.shortcuts import render
from .models import MenuItem, Category
from .serializers import MenuItemSerializer
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

# Create your views here.

class MenuItemList(generics.ListCreateAPIView):
    """
    View list of menu items in the system.

    * Only Manager user can create new menu items.
    """

    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get(self, request):
        items = MenuItem.objects.all()
        serialized_item = MenuItemSerializer(items, many=True)
        return Response(serialized_item.data, status.HTTP_200_OK)
    
    def post(self, request):
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
