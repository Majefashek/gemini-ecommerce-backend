from algoliasearch_django import AlgoliaIndex
from algoliasearch_django.decorators import register
from . models import Product

@register(Product)
class ProductIndex(AlgoliaIndex):
    fields = ('name', 'category','description','season')
    settings = {'searchableAttributes': ['name', 'category','description','season']}
    index_name = 'my_index'