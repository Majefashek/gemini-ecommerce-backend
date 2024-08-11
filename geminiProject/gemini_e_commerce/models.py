from django.db import models
from django.db import models
from authentication.models import CustomUser
from django.utils import timezone
from datetime import timedelta


class ChatHistory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    chat_text = models.CharField(max_length=200)
    response_text = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Chat History for {self.user.email}"



class Product(models.Model):
    name = models.CharField(max_length=200,blank=True,null=True)
    category = models.CharField(max_length=200,blank=True,null=True)
    description = models.TextField(blank=True,null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    season = models.CharField(max_length=200,blank=True,null=True)
    stock = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"