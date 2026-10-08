import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quickstore.settings')
django.setup()

from store.models import Category, Product

# Clear existing products
Product.objects.all().delete()

# Ensure categories exist
c_snacks, _ = Category.objects.get_or_create(name='Snacks & Treats')
c_toys, _ = Category.objects.get_or_create(name='Toys & Fun')
c_dairy, _ = Category.objects.get_or_create(name='Dairy & Breakfast')
c_essentials, _ = Category.objects.get_or_create(name='Family Essentials')

adjectives = ['Yummy', 'Crunchy', 'Super', 'Organic', 'Magical', 'Sweet', 'Healthy', 'Fluffy', 'Delightful', 'Fresh', 'Choco-Berry', 'Rainbow']

# Using direct open image links for categories
items = [
    ('Gummy Bears', 149, 199, c_snacks, 'https://images.unsplash.com/photo-1582058091505-f87a2e55a40f?w=400'),
    ('Teddy Bear Plush', 499, 699, c_toys, 'https://images.unsplash.com/photo-1559454403-b8fb8852101d?w=400'),
    ('Farm Fresh Milk (1L)', 75, 85, c_dairy, 'https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400'),
    ('Chocolate Cookies', 120, 150, c_snacks, 'https://images.unsplash.com/photo-1499636136210-6f4ee915583e?w=400'), 
    ('Building Blocks Set', 599, 899, c_toys, 'https://images.unsplash.com/photo-1587654780291-39c9404d746b?w=400'),
    ('Greek Yogurt', 95, 110, c_dairy, 'https://images.unsplash.com/photo-1488477181946-6428a0291777?w=400'),
    ('Fruit Juice Box', 30, 40, c_snacks, 'https://images.unsplash.com/photo-1621263764928-df1444c5e859?w=400'),
    ('Cereal Crunch Pack', 250, 299, c_dairy, 'https://images.unsplash.com/photo-1521483451571-c045053ba21e?w=400'),
    ('Mini RC Car', 799, 1099, c_toys, 'https://images.unsplash.com/photo-1594787318286-3d835c1d207f?w=400'),
    ('Baby Wet Wipes', 180, 220, c_essentials, 'https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=400'),
]

count = 0
for i in range(1, 101):
    base_item = random.choice(items)
    adj = random.choice(adjectives)
    name = f"{adj} {base_item[0]} #{i}"
    price = base_item[1] + random.randint(-10, 20)
    mrp = base_item[2] + random.randint(0, 30)
    category = base_item[3]
    image_url = base_item[4]
    weight = "500g" if category == c_snacks else ("1 Unit" if category == c_toys else "1L")

    Product.objects.create(
        name=name,
        category=category,
        price=max(price, 20),
        mrp=max(mrp, price + 10),
        weight=weight,
        stock=150,
        image=image_url
    )
    count += 1

print(f"Successfully generated {count} products with automatic images!")