import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quickstore.settings')
django.setup()

from store.models import Category, Product

# Create categories targeted at women & kids (Snacks, Beauty, Toys, Dairy, Fresh Fruits)
categories = ['Snacks & Munchies', 'Dairy & Breakfast', 'Beauty & Skincare', 'Toys & Kids', 'Fresh Fruits']
cat_objs = {}
for cat_name in categories:
    cat, _ = Category.objects.get_or_create(name=cat_name)
    cat_objs[cat_name] = cat

# Generate 100+ items programmatically or array list
items = [
    ("Kinder Joy Surprise Egg", "Snacks & Munchies", 45, 50, "20 g"),
    ("Cadbury Dairy Milk Silk", "Snacks & Munchies", 175, 190, "150 g"),
    ("Lays Classic Salted Chips", "Snacks & Munchies", 20, 20, "50 g"),
    ("Mamaearth Ubtan Face Wash", "Beauty & Skincare", 249, 399, "100 ml"),
    ("Nivea Soft Light Moisturizer", "Beauty & Skincare", 150, 199, "200 ml"),
    ("Hot Wheels Toy Car", "Toys & Kids", 149, 179, "1 pc"),
    ("Rubik's Magic Cube", "Toys & Kids", 199, 299, "1 pc"),
    ("Amul Fresh Toned Milk", "Dairy & Breakfast", 32, 34, "500 ml"),
    ("Epigamia Greek Yogurt", "Dairy & Breakfast", 50, 60, "90 g"),
]

# Repeat pattern to easily push past 100 items for demo purposes
for i in range(15):
    for name, cat, price, mrp, wt in items:
        Product.objects.create(
            category=cat_objs[cat],
            name=f"{name} #{i+1}",
            price=price,
            mrp=mrp,
            weight=wt,
            stock=50,
            is_featured=(i == 0)
        )

print("Successfully added 100+ products to your SQL database!")