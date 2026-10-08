from django.test import Client, TestCase
from django.urls import reverse

from .models import Task


class TaskTests(TestCase):
    def test_empty_home(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'No tasks yet.')
        self.assertNotContains(response, 'Hello, world!')

    def test_add_and_refresh(self):
        response = self.client.post(reverse('add_task'), {'text': '  Study Python  '})
        self.assertRedirects(response, reverse('home'))
        task = Task.objects.get()
        self.assertEqual(task.text, 'Study Python')
        self.assertFalse(task.completed)
        self.assertContains(self.client.get(reverse('home')), 'Study Python')

    def test_invalid_text(self):
        for text in ['', '   ', 'x' * 201]:
            with self.subTest(text=text):
                response = self.client.post(reverse('add_task'), {'text': text})
                self.assertEqual(response.status_code, 400)
                self.assertTrue(response.context['form'].errors)
        self.assertFalse(Task.objects.exists())

    def test_invalid_form_keeps_existing_tasks(self):
        Task.objects.create(text='Existing task')
        response = self.client.post(reverse('add_task'), {'text': ''})
        self.assertContains(response, 'Existing task', status_code=400)

    def test_complete_and_reopen(self):
        task = Task.objects.create(text='Study Python')
        url = reverse('toggle_task', args=[task.pk])
        response = self.client.post(url)
        self.assertRedirects(response, reverse('home'))
        task.refresh_from_db()
        self.assertTrue(task.completed)
        self.assertContains(self.client.get(reverse('home')), 'Completed')
        self.client.post(url)
        task.refresh_from_db()
        self.assertFalse(task.completed)
        self.assertContains(self.client.get(reverse('home')), 'Pending')

    def test_delete_only_selected_task(self):
        task = Task.objects.create(text='Delete this')
        remaining = Task.objects.create(text='Keep this')
        response = self.client.post(reverse('delete_task', args=[task.pk]))
        self.assertRedirects(response, reverse('home'))
        self.assertFalse(Task.objects.filter(pk=task.pk).exists())
        self.assertTrue(Task.objects.filter(pk=remaining.pk).exists())

    def test_delete_last_task_restores_empty_state(self):
        task = Task.objects.create(text='Last task')
        self.client.post(reverse('delete_task', args=[task.pk]))
        self.assertContains(self.client.get(reverse('home')), 'No tasks yet.')

    def test_mutations_require_post(self):
        task = Task.objects.create(text='Keep this')
        urls = [
            reverse('add_task'),
            reverse('toggle_task', args=[task.pk]),
            reverse('delete_task', args=[task.pk]),
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 405)
        task.refresh_from_db()
        self.assertFalse(task.completed)
        self.assertEqual(Task.objects.count(), 1)

    def test_missing_task_returns_404(self):
        for name in ['toggle_task', 'delete_task']:
            with self.subTest(name=name):
                response = self.client.post(reverse(name, args=[999]))
                self.assertEqual(response.status_code, 404)

    def test_csrf_protection(self):
        client = Client(enforce_csrf_checks=True)
        task = Task.objects.create(text='Protected task')
        urls = [
            reverse('add_task'),
            reverse('toggle_task', args=[task.pk]),
            reverse('delete_task', args=[task.pk]),
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(client.post(url, {'text': 'New task'}).status_code, 403)
        task.refresh_from_db()
        self.assertFalse(task.completed)
        self.assertEqual(Task.objects.count(), 1)
        client.get(reverse('home'))
        token = client.cookies['csrftoken'].value
        response = client.post(reverse('add_task'), {
            'text': 'Valid task',
            'csrfmiddlewaretoken': token,
        })
        self.assertRedirects(response, reverse('home'))

    def test_task_text_is_escaped(self):
        Task.objects.create(text='<script>alert("test")</script>')
        response = self.client.get(reverse('home'))
        self.assertNotContains(response, '<script>alert("test")</script>')
        self.assertContains(response, '&lt;script&gt;')

    def test_about_still_works(self):
        self.assertContains(self.client.get(reverse('about')), 'About me!')
