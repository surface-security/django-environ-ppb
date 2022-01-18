import tempfile

from unittest import mock
from django.test import TestCase

from ppbenviron import CustomEnv


class Test(TestCase):
    def setUp(self):
        self.env = CustomEnv()
        self.env.ENVIRON = {}

    def test_env(self):
        self.env.ENVIRON['TEST'] = 'OK'
        self.assertEqual(self.env('TEST'), 'OK')

    def test_file(self):
        with tempfile.NamedTemporaryFile(delete=False, mode='w') as tf:
            tf.write('OK')

            self.env.ENVIRON['TEST_FILE'] = tf.name
        self.assertEqual(self.env('TEST'), 'OK')
