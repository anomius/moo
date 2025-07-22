import unittest
from unittest.mock import patch, MagicMock
from infra.api_client import ApiClient
from core.dto import DTOBundle
from core.errors import ExternalServiceError

class TestApiClient(unittest.TestCase):
    @patch('infra.api_client.requests.post')
    def test_post_success(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.text = 'OK'
        client = ApiClient('http://fake-url')
        resp = client.post({'foo': 'bar'})
        self.assertEqual(resp['status'], 'success')
        self.assertIn('data', resp)

    @patch('infra.api_client.requests.post')
    def test_post_failure(self, mock_post):
        mock_post.return_value.status_code = 400
        mock_post.return_value.text = 'Bad Request'
        client = ApiClient('http://fake-url')
        with self.assertRaises(ExternalServiceError):
            client.post({'foo': 'bar'})

    @patch('infra.api_client.ConstraintBuilder')
    @patch.object(ApiClient, 'post')
    def test_post_bundle_calls_constraint_builder(self, mock_post, mock_cb):
        bundle = MagicMock(spec=DTOBundle)
        mock_cb.return_value.build.return_value = {'payload': 1}
        client = ApiClient('http://fake-url')
        client.post_bundle(bundle)
        mock_cb.return_value.build.assert_called_once_with(bundle)
        mock_post.assert_called_once()

    def test_env_url_selection(self):
        prod = ApiClient.create_for_environment('PROD')
        uat = ApiClient.create_for_environment('UAT')
        dev = ApiClient.create_for_environment('DEV')
        self.assertIn('prod', prod.base_url)
        self.assertIn('uat', uat.base_url)
        self.assertIn('localhost', dev.base_url)
        self.assertTrue(prod.verify_ssl)
        self.assertTrue(uat.verify_ssl)
        self.assertFalse(dev.verify_ssl)

if __name__ == '__main__':
    unittest.main() 