import unittest
from unittest.mock import patch, MagicMock
from infra.email_service import EmailService
from core.errors import ExternalServiceError

class TestEmailService(unittest.TestCase):
    def setUp(self):
        self.service = EmailService('smtp.test.com', 587, 'from@test.com', 'pwd')

    def test_format_email_subject_single_and_multi_brand(self):
        subj1 = self.service.format_email_subject('Italy', ['TOUJEO'])
        subj2 = self.service.format_email_subject('Italy', ['TOUJEO', 'SOLIQUA'])
        self.assertIn('TOUJEO', subj1)
        self.assertIn('TOUJEO', subj2)
        self.assertIn('SOLIQUA', subj2)

    def test_format_email_body_single_and_multi_brand(self):
        body1 = self.service.format_email_body('Italy', ['TOUJEO'], 'SL1', 'C1 2024')
        body2 = self.service.format_email_body('Italy', ['TOUJEO', 'SOLIQUA'], 'SL1', 'C1 2024')
        self.assertIn('TOUJEO', body1)
        self.assertIn('TOUJEO', body2)
        self.assertIn('SOLIQUA', body2)
        self.assertIn('Italy', body1)
        self.assertIn('SL1', body1)
        self.assertIn('C1 2024', body1)

    @patch('infra.email_service.smtplib.SMTP')
    def test_send_success(self, mock_smtp):
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        self.service.send('subj', 'body', ['to@test.com'], b'bytes', 'file.xlsx')
        mock_server.sendmail.assert_called_once()

    @patch('infra.email_service.smtplib.SMTP')
    def test_send_failure(self, mock_smtp):
        mock_smtp.side_effect = Exception('SMTP error')
        with self.assertRaises(ExternalServiceError):
            self.service.send('subj', 'body', ['to@test.com'], b'bytes', 'file.xlsx')

if __name__ == '__main__':
    unittest.main() 