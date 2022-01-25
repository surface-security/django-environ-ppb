import tempfile

from unittest import mock
from django.test import TestCase

from ppbenviron import CustomEnv


class Test(TestCase):
    def setUp(self):
        self.env = CustomEnv()
        self.env.ENVIRON = {}

    def test_vault(self):
        self.env.ENVIRON = {
            'URL': 'https://vault.local',
            'TOKEN': 'token123',
            'PATHS': 'common,notprd',
            'MOUNT': '/testsurf',
        }
        self.env.setup_vault('URL', 'TOKEN', 'MOUNT', 'PATHS')
        self.env.ENVIRON['TEST_VAULT'] = 'secretkey'
        with mock.patch('hvac.Client') as mh:
            mh().read.return_value = {'data': {'secretkey': 'OK'}}
            mh.reset_mock()
            self.assertEqual(self.env('TEST'), 'OK')
            mh.assert_called_once_with(token='token123', url='https://vault.local')
            mh().read.assert_has_calls((mock.call('/testsurf/common'), mock.call('/testsurf/notprd')))

        self.assertEqual(self.env.vault_cache, {'secretkey': 'OK'})

    def test_vault_persistence(self):
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            environ = {
                'URL': 'https://vault.local',
                'TOKEN': 'token123',
                'PATHS': 'common,notprd',
                'MOUNT': '/testsurf',
                'CACHE': tf.name,
            }

        self.env.ENVIRON = environ.copy()
        self.env.setup_vault('URL', 'TOKEN', 'MOUNT', 'PATHS', persist_cache_var='CACHE')

        self.assertIsNone(self.env.vault_cache)

        self.env.ENVIRON['TEST_VAULT'] = 'secretkey'
        with mock.patch('hvac.Client') as mh:
            mh().read.return_value = {'data': {'secretkey': 'OK'}}
            mh.reset_mock()
            self.assertEqual(self.env('TEST'), 'OK')
            mh.assert_called()

        self.assertEqual(self.env.vault_cache, {'secretkey': 'OK'})

        new_env = CustomEnv()
        new_env.ENVIRON = environ.copy()
        self.assertIsNone(new_env.vault_cache)
        new_env.setup_vault('URL', 'TOKEN', 'MOUNT', 'PATHS', persist_cache_var='CACHE')
        self.assertEqual(new_env.vault_cache, {'secretkey': 'OK'})
