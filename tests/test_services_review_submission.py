import unittest
from unittest.mock import patch, MagicMock
from services.review_submission_service import ReviewSubmissionService
from core.dto import DTOBundle

class TestReviewSubmissionService(unittest.TestCase):
    @patch('services.review_submission_service.SnowflakeRepo')
    @patch('services.review_submission_service.EmailService')
    @patch('services.review_submission_service.ExcelExporterService')
    @patch('services.review_submission_service.ApiClient')
    def test_submit_constraints_success(self, mock_api, mock_excel, mock_email, mock_sf):
        svc = ReviewSubmissionService()
        bundle = MagicMock(spec=DTOBundle)
        output_table_dict = {'table': MagicMock()}
        mock_excel.return_value.build.return_value = b'bytes'
        mock_api.create_for_environment.return_value.post_bundle.return_value = {'status': 'success'}
        mock_email.return_value.send.return_value = None
        mock_sf.return_value.snowflake_con = MagicMock()
        mock_sf.return_value.to_sql = MagicMock()
        svc.user_email = 'user@sanofi.com'
        msg = svc.submit_constraints(bundle, output_table_dict)
        self.assertIn('successfully', msg)

    @patch('services.review_submission_service.ApiClient')
    @patch('services.review_submission_service.ExcelExporterService')
    @patch('services.review_submission_service.EmailService')
    @patch('services.review_submission_service.SnowflakeRepo')
    def test_submit_constraints_api_failure(self, mock_sf, mock_email, mock_excel, mock_api):
        svc = ReviewSubmissionService()
        bundle = MagicMock(spec=DTOBundle)
        output_table_dict = {'table': MagicMock()}
        mock_excel.return_value.build.return_value = b'bytes'
        mock_api.create_for_environment.return_value.post_bundle.return_value = {'status': 'fail', 'data': 'API error'}
        svc.user_email = 'user@sanofi.com'
        msg = svc.submit_constraints(bundle, output_table_dict)
        self.assertIn('API submission failed', msg)

    @patch('services.review_submission_service.ApiClient')
    @patch('services.review_submission_service.ExcelExporterService')
    @patch('services.review_submission_service.EmailService')
    @patch('services.review_submission_service.SnowflakeRepo')
    def test_submit_constraints_email_failure(self, mock_sf, mock_email, mock_excel, mock_api):
        svc = ReviewSubmissionService()
        bundle = MagicMock(spec=DTOBundle)
        output_table_dict = {'table': MagicMock()}
        mock_excel.return_value.build.return_value = b'bytes'
        mock_api.create_for_environment.return_value.post_bundle.return_value = {'status': 'success'}
        mock_email.return_value.send.side_effect = Exception('Email error')
        svc.user_email = 'user@sanofi.com'
        msg = svc.submit_constraints(bundle, output_table_dict)
        self.assertIn('Submission failed', msg)

    @patch('services.review_submission_service.ApiClient')
    @patch('services.review_submission_service.ExcelExporterService')
    @patch('services.review_submission_service.EmailService')
    @patch('services.review_submission_service.SnowflakeRepo')
    def test_submit_constraints_snowflake_failure(self, mock_sf, mock_email, mock_excel, mock_api):
        svc = ReviewSubmissionService()
        bundle = MagicMock(spec=DTOBundle)
        output_table_dict = {'table': MagicMock()}
        mock_excel.return_value.build.return_value = b'bytes'
        mock_api.create_for_environment.return_value.post_bundle.return_value = {'status': 'success'}
        mock_email.return_value.send.return_value = None
        mock_sf.return_value.snowflake_con = MagicMock()
        mock_sf.return_value.to_sql.side_effect = Exception('Snowflake error')
        svc.user_email = 'user@sanofi.com'
        msg = svc.submit_constraints(bundle, output_table_dict)
        self.assertIn('Submission failed', msg)

if __name__ == '__main__':
    unittest.main() 