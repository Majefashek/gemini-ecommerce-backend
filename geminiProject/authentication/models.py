from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.db import models

class CustomUserManager(BaseUserManager):
    
    def create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user =self.model(email=email,**extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
    username = models.CharField(max_length=150,null=True, blank=True)
    first_name = models.CharField(max_length=30,null=True, blank=True)
    last_name = models.CharField(max_length=30,null=True, blank=True)
    password = models.CharField(max_length=128)
    country=models.CharField(max_length=150,blank=True,null=True)
    phone_number=models.CharField(max_length=11,blank=True,null=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    
    def __str__(self):
        return self.email
