from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import CartItem, Category, Product


class StoreRoutesTests(TestCase):
    def test_product_list_route_exists(self):
        url = reverse('product_list')
        self.assertEqual(url, '/products/')

    def test_home_page_renders(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_home_page_shows_quantity_stepper_for_cart_items(self):
        category = Category.objects.create(name='Snacks & Treats')
        product = Product.objects.create(
            category=category,
            name='Milk Box',
            price=50,
            mrp=60,
            weight='1L',
        )
        user = User.objects.create_user(username='alice', password='pass123')
        CartItem.objects.create(user=user, product=product, quantity=2)

        self.client.force_login(user)
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'href="/cart/decrease/{product.id}/?next=home"')
        self.assertContains(response, f'href="/cart/add/{product.id}/?next=home"')
        self.assertContains(response, '>2<')
