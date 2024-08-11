from django.contrib import admin
from .models import *
from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
  # Replace with your model

class ProductModelAdmin(ImportExportModelAdmin):
    pass

admin.site.register(Product, ProductModelAdmin)

#admin.site.register(Product)
admin.site.register(Order)

admin.site.register(ChatHistory)
# Register your models here.
