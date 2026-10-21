from django.test import SimpleTestCase


class SmokeTests(SimpleTestCase):
    def test_healthz(self):
        response = self.client.get('/healthz')
        self.assertEqual((response.status_code, response.content), (200, b'ok'))

    def test_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Django is running on Porter')
