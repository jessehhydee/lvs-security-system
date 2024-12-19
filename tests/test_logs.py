import sys
import os
sys.path.append("..")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
import unittest
from unittest.mock import patch, mock_open, MagicMock
from src.logs import Logs


class TestLogs(unittest.TestCase):
    def setUp(self):
        self.logs = Logs()

    @patch('builtins.open', new_callable = mock_open, read_data = '{"events": []}')
    @patch("os.path.exists", return_value = True)
    def test_new_event_log_valid_log(self, mock_exists, mock_open):
        log = {
            'timestamp': 'Dummy',
            'event_type': 'Dummy'
        }

        self.logs._Logs__update_json_file = MagicMock()
        self.logs.new_event_log(log)

        mock_open.assert_called_once_with(self.logs.events_filename)
        self.logs._Logs__update_json_file.assert_called_once_with(
            self.logs.events_filename,
            {'events': [log]}
        )

    @patch("builtins.open", new_callable = mock_open)
    def test_check_incoming_events_log_missing_timestamp(self, mock_open):
        log_data = {
            "event_type": "Dummy",
        }

        with self.assertRaises(KeyError):
            self.logs._Logs__check_incoming_events_log(log_data)

    @patch("builtins.open", new_callable = mock_open)
    def test_check_incoming_events_log_missing_event_type(self, mock_open):
        log_data = {
            "timestamp": "Dummy",
        }

        with self.assertRaises(KeyError):
            self.logs._Logs__check_incoming_events_log(log_data)

    @patch("builtins.open", new_callable = mock_open)
    @patch("os.path.exists", return_value = False)
    def test_create_events_log_file_creates_new_file(self, mock_exists, mock_open):
        self.logs._Logs__create_events_log_file()
        mock_open.assert_called_once_with(self.logs.events_filename, 'w')

    @patch('builtins.open', new_callable = mock_open)
    def test_update_json_file(self, mock_open):
        json_content = {
            'events': [
                {
                    'timestamp': 'Dummy',
                    'event_type': 'Dummy'
                }
            ]
        }

        self.logs._Logs__update_json_file(self.logs.events_filename, json_content)

        mock_open.assert_called_once_with(self.logs.events_filename, 'w')
        mock_open().write.assert_any_call('"events"')

    @patch('builtins.open', new_callable = mock_open)
    def test_update_json_file_io_error(self, mock_open):
        mock_open.side_effect = IOError("File write error")

        with self.assertRaises(RuntimeError):
            self.logs._Logs__update_json_file(self.logs.events_filename, {'events': []})

    @patch('builtins.open', new_callable = mock_open)
    def test_update_json_file_type_error(self, mock_open):
        mock_open.side_effect = TypeError("Serialization error")

        with self.assertRaises(ValueError):
            self.logs._Logs__update_json_file(self.logs.events_filename, {'events': []})

    @patch("builtins.open", new_callable = mock_open)
    def test_new_system_log_with_non_error_log(self, mock_open):
        self.logs.new_system_log("Dummy system log")

        mock_open.assert_called_once_with(self.logs.system_filename, 'a')
        written_log = mock_open().write.call_args[0][0]
        self.assertIn("[LOG]", written_log)
        self.assertIn("Dummy system log", written_log)

    @patch("builtins.open", new_callable = mock_open)
    def test_new_system_log_with_error_log(self, mock_open):
        self.logs.new_system_log("Dummy system error log", True)

        mock_open.assert_called_with(self.logs.system_filename, 'a')
        written_log = mock_open().write.call_args[0][0]
        self.assertIn("[ERR]", written_log)
        self.assertIn("Dummy system error log", written_log)

    @patch("builtins.open", new_callable = mock_open)
    @patch("os.path.exists", return_value = False)
    def test___create_systems_log_file_creates_file(self, mock_exists, mock_open):
        self.logs._Logs__create_systems_log_file()
        mock_open.assert_called_once_with(self.logs.system_filename, 'x')

    @patch("builtins.open", new_callable = mock_open)
    def test_clear_event_logs(self, mock_open):
        self.logs.clear_event_logs()
        mock_open.assert_called_with(self.logs.events_filename, 'w')

    @patch("builtins.open", new_callable = mock_open)
    def test_clear_system_logs(self, mock_open):
        self.logs.clear_system_logs()
        mock_open.assert_called_with(self.logs.system_filename, 'w')

if __name__ == '__main__':
    unittest.main()