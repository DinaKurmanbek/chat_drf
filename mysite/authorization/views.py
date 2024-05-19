from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from rest_framework import generics, views, status
from rest_framework.response import Response

from .models import User
from .serializers import LoginSerializer, RegistrationSerializer, UserSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(username=serializer.validated_data['username'], password=serializer.validated_data['password'])
        if user is not None:
            login(request, user)
            return Response({'token': user.auth_token.key})
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class RegistrationView(generics.CreateAPIView):

    queryset = User.objects.all()
    serializer_class = RegistrationSerializer

    def create(self, request, *args, **kwargs):
        request.data['password'] = make_password(request.data['password'])
        return super().create(request, *args, **kwargs)


class PersonalAreaView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
        return self.request.user



