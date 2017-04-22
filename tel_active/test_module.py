from django.test import TestCase
from sms_module.util import gen_num


# Create your tests here.
class UtilTestCase(TestCase):
    def test_gen_num(self):
        n = 6
        num = gen_num(6)
        self.assertTrue(len(num) == n)

    def test_index_view(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
