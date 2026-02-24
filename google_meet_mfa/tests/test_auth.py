import unittest
from unittest.mock import patch, MagicMock
from src.auth import authenticate_google_services

class TestAuthenticateGoogleServices(unittest.TestCase):
    
    @patch('src.auth.Credentials.from_authorized_user_file')
    @patch('src.auth.InstalledAppFlow.from_client_secrets_file')
    @patch('src.auth.build')
    def test_authenticate_google_services(self, mock_build, mock_from_client_secrets_file, mock_from_authorized_user_file):
        # Setup mocks
        mock_creds = MagicMock()
        mock_from_authorized_user_file.return_value = mock_creds
        mock_build.return_value = MagicMock(), MagicMock()
        
        # Call the function
        calendar_service, drive_service = authenticate_google_services()
        
        # Check if build was called with correct arguments
        mock_build.assert_any_call('calendar', 'v3', credentials=mock_creds)
        mock_build.assert_any_call('drive', 'v3', credentials=mock_creds)
        
        # Ensure that the returned services are instances of the correct types
        self.assertIsNotNone(calendar_service)
        self.assertIsNotNone(drive_service)

if __name__ == '__main__':
    unittest.main()
