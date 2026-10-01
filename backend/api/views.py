from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from users.models import User
from .serializers import UserSerializer

# Create your views here.


class UserListView(APIView):

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)