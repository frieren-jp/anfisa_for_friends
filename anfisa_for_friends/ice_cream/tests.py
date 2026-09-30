from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Category, IceCream, Topping, Wrapper


class CatalogTests(TestCase):
    fixtures = ['catalog.json']

    def test_fixture_and_public_pages(self):
        self.assertEqual(IceCream.objects.count(), 11)
        for url in ['/', '/about/', '/ice_cream/', '/admin/login/']:
            self.assertEqual(self.client.get(url).status_code, 200)
        item = IceCream.objects.filter(
            is_published=True, category__is_published=True,
        ).first()
        self.assertContains(self.client.get('/ice_cream/'), item.title)
        self.assertContains(self.client.get(f'/ice_cream/{item.pk}/'), item.title)

    def test_unpublished_and_missing_items_are_hidden(self):
        item = IceCream.objects.first()
        item.is_published = False
        item.save()
        self.assertEqual(self.client.get(f'/ice_cream/{item.pk}/').status_code, 404)
        item.is_published = True
        item.save()
        item.category.is_published = False
        item.category.save()
        self.assertEqual(self.client.get(f'/ice_cream/{item.pk}/').status_code, 404)
        self.assertEqual(self.client.get('/ice_cream/99999/').status_code, 404)

    def test_homepage_selection(self):
        response = self.client.get('/')
        for item in response.context['ice_cream_list']:
            self.assertTrue(item.is_on_main and item.is_published)

    def test_admin_login_and_add_ice_cream(self):
        get_user_model().objects.create_superuser(
            username='editor', password='test-editor-password',
        )
        add_url = reverse('admin:ice_cream_icecream_add')
        self.assertEqual(self.client.get(add_url).status_code, 302)
        response = self.client.post(reverse('admin:login'), {
            'username': 'editor', 'password': 'test-editor-password',
            'next': add_url,
        })
        self.assertRedirects(response, add_url)
        response = self.client.post(add_url, {
            'title': 'Тестовое ванильное мороженое',
            'description': 'Добавлено через форму администратора.',
            'category': Category.objects.first().pk,
            'toppings': [Topping.objects.first().pk],
            'is_published': 'on', 'is_on_main': 'on', '_save': 'Сохранить',
        })
        self.assertEqual(response.status_code, 302)
        item = IceCream.objects.get(title='Тестовое ванильное мороженое')
        self.assertContains(self.client.get('/ice_cream/'), item.title)
        self.assertContains(self.client.get(f'/ice_cream/{item.pk}/'), item.title)
        self.assertContains(self.client.get('/'), item.title)

    def test_site_login_for_regular_user(self):
        get_user_model().objects.create_user(username='reader', password='reader-test-pass')
        response = self.client.post('/login/', {'username': 'reader', 'password': 'reader-test-pass'})
        self.assertRedirects(response, '/ice_cream/')
        self.assertNotContains(self.client.get('/ice_cream/'), 'Добавить мороженое')
        self.assertEqual(self.client.get('/admin/ice_cream/icecream/add/').status_code, 302)
        self.assertRedirects(self.client.post('/logout/'), '/')

    def test_admin_models_are_registered_and_translated(self):
        user = get_user_model().objects.create_superuser(
            username='testadmin', password='test-only-password',
        )
        self.client.force_login(user)
        response = self.client.get('/admin/')
        self.assertContains(response, 'Каталог мороженого')
        for model in [Category, Topping, Wrapper, IceCream]:
            url = reverse(f'admin:ice_cream_{model._meta.model_name}_changelist')
            self.assertEqual(self.client.get(url).status_code, 200)
            self.assertEqual(str(model.objects.first()), model.objects.first().title)
