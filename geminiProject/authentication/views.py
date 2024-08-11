from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_yasg.utils import swagger_auto_schema
from .serializers import CustomUserSerializer, CustomUserTokenObtainPairSerializer

class BaseAPIView(APIView):
    def create_response(self, success, message, data=None, status=status.HTTP_200_OK):
        response = {'success': success, 'message': message}
        if data:
            response['data'] = data
        return Response(response, status=status)

class CustomUserTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomUserTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            return self.create_response(True, 'Login successful', response.data)
        except Exception as e:
            return self.handle_exception(e)

    def handle_exception(self, exc):
        return self.create_response(False, str(exc), status=status.HTTP_400_BAD_REQUEST)

    def create_response(self, success, message, data=None, status=status.HTTP_200_OK):
        response = {'success': success, 'message': message}
        if data:
            response.update(data)
        return Response(response, status=status)

class CreateUser(BaseAPIView):
    @swagger_auto_schema(request_body=CustomUserSerializer)
    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return self.create_response(True, 'User created successfully', status=status.HTTP_201_CREATED)
        
        return self.create_response(False, 'User not created successfully', {'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class GetUserDetails(BaseAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            serialized = CustomUserSerializer(request.user)
            return self.create_response(True, 'User retrieved successfully', serialized.data)
        except Exception as e:
            return self.create_response(False, str(e))