import csv
from datetime import datetime
from gemini_e_commerce.models import Product  # Replace 'myapp' with your actual app name

def import_products(file_path):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            Product.objects.create(
                name=row['name'],
                category=row['category'],
                description=row['description'],
                price=row['price'],
                stock=row['stock'],
                season=row['season']
            )

if __name__ == '__main__':
    csv_file_path = 'products_catalog.csv'  # Replace with your actual file path
    import_products(csv_file_path)