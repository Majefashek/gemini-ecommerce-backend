import datetime
from haystack import indexes
from .models import Product

class ProductIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr='name')
    description = indexes.CharField(model_attr='description')
    price = indexes.DecimalField(model_attr='price')
    category = indexes.CharField(model_attr='category')  # Added category field
    season = indexes.CharField(model_attr='season')      # Added season field
    stock = indexes.IntegerField(model_attr='stock')      # Added stock field

    def get_model(self):
        return Product

    def index_queryset(self, using=None):
        return self.get_model().objects.all()