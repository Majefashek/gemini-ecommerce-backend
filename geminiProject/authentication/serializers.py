from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from .models import CustomUser

class CustomUserTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        data = super().validate(attrs)
        email = attrs.get("email", "")
        password = attrs.get("password", "")

        # Validate student credentials
        user = CustomUser.objects.filter(email=email).first()
        if user and user.check_password(password):
            return data
        else:
            raise serializers.ValidationError("Invalid student credentials")


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = CustomUser
        fields = [
            'email',
            'password',
            'username',
            'first_name',
            'last_name',
            'country',
            'phone_number',
        ]
         
    def create(self, validated_data):
        # Extract the password from the validated data
        password = validated_data.pop('password', None)
        # Create a new user instance with the remaining validated data
        user = CustomUser.objects.create(**validated_data)
        # Set the password for the user
        if password:
            user.set_password(password)
            user.save()
        return user