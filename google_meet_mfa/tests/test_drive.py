import unittest
from unittest.mock import patch, MagicMock
from src.drive import get_meeting_transcripts

class TestGetMeetingTranscripts(unittest.TestCase):
    
    @patch('src.drive.googleapiclient.http.MediaIoBaseDownload')
    @patch('src.drive.open')
    def test_get_meeting_transcripts(self, mock_open, mock_media_io_base_download):
        # Setup mock data
        mock_request = MagicMock()
        mock_downloader = MagicMock()
        mock_media_io_base_download.return_value = mock_downloader
        mock_downloader.next_chunk.return_value = (MagicMock(progress=lambda: 1.0), True)
        
        drive_service = MagicMock()
        drive_service.files().get_media.return_value = mock_request
        
        # Call the function
        transcript_file = get_meeting_transcripts(drive_service, 'test_file_id')
        
        # Check if the file was downloaded
        mock_open.assert_called_once_with('transcript.txt', 'wb')
        mock_media_io_base_download.assert_called_once()
        
        # Ensure correct filename was returned
        self.assertEqual(transcript_file, 'transcript.txt')

if __name__ == '__main__':
    unittest.main()
