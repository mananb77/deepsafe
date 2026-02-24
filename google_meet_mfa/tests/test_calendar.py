import unittest
from unittest.mock import MagicMock
from src.calendar import get_meeting_metadata

class TestGetMeetingMetadata(unittest.TestCase):
    
    def setUp(self):
        self.mock_calendar_service = MagicMock()
        self.mock_event = {
            'summary': 'Meeting',
            'start': {'dateTime': '2024-08-01T10:00:00Z'},
            'end': {'dateTime': '2024-08-01T11:00:00Z'},
            'description': 'Meeting Description'
        }
        self.mock_calendar_service.events().get().execute.return_value = self.mock_event

    def test_get_meeting_metadata(self):
        event_id = 'test_event_id'
        metadata = get_meeting_metadata(self.mock_calendar_service, event_id=event_id)
        
        self.assertEqual(metadata['summary'], 'Meeting')
        self.assertEqual(metadata['start'], '2024-08-01T10:00:00Z')
        self.assertEqual(metadata['end'], '2024-08-01T11:00:00Z')
        self.assertEqual(metadata['description'], 'Meeting Description')

if __name__ == '__main__':
    unittest.main()
