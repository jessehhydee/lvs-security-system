# lvs-security-system

## Assumptions

<ol>
<li>External package use acceptable</li>
<li>Systems log does not need to be formatted as JSON</li>
<li>HTTP API's to follow RESTful practices</li>
<li>The users system has given permissions to the application to access their camera</li>
</ol>

## Additional Features

<ol>
<li>Empty image-captures directory - handled via HTTP call</li>
<li>Empty events-log - handled via HTTP call</li>
<li>Empty systems-log - handled via HTTP call</li>
</ol>

## AI Assistant Use

**Prompt**:
<br>
In Python, I am trying to validate that a files contents are valid JSON.
Using the following line to open the file, please provide a code snippet that reads the file content and checks that the file contents are valid json. If not, raise an exception. If it is valid, store the file content as a dict.
<br>
``with open(events_filename) as events_file:``
<br><br>
**Response**:
```
with open(events_filename) as events_file:
    try:
        events_data = json.load(events_file)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in file {events_filename}: {e}")
```
<br><br>
**Prompt**:
<br>
How would you catch any errors to in the following method:
```
def update_json_file(filename, json_content):
    with open(filename, 'w') as file:
        json.dump(json_content, file, indent=4)
```
<br>

**Response**:
```
def update_json_file(filename, json_content):
    try:
        with open(filename, 'w') as file:
            json.dump(json_content, file, indent=4)
    except (IOError, OSError) as e:
        raise RuntimeError(f"An error occurred while trying to write to the file: {e}")
    except (TypeError, json.JSONDecodeError) as e:
        raise ValueError(f"An error occurred while serializing the content to JSON: {e}")
```
<br><br>
**Prompt**:
<br>
In Python, how would you capture the devices local ip address?
<br>

**Response**:
```
import socket

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        # Try to connect to an external server (Google's public DNS server in this case)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]  # Get the local IP address
    except Exception as e:
        local_ip = None
        print(f"Error obtaining local IP address: {e}")
    finally:
        s.close()
    
    return local_ip

local_ip = get_local_ip()
print(f"Local IP address: {local_ip}")
```
<br>

**Explanation**:
- socket.socket(socket.AF_INET, socket.SOCK_DGRAM): This creates a UDP socket (which doesn't require establishing a full connection).
- s.connect(("8.8.8.8", 80)): This doesn't actually send any data, but it uses the network to figure out which local IP address would be used to communicate with Google's public DNS server (8.8.8.8). This ensures that we get the correct local IP address that would be used on the local network.
- s.getsockname()[0]: The getsockname() method returns a tuple containing the local address and port, and we access the first element to get the local IP address.

**Note from Jesse**:
<br>
Gave me further clarification on: https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
<br><br><br>
**Prompt**:
<br>
I get the following error when trying to run this file with python3 -m app:
AttributeError: module 'logging' has no attribute 'StreamHandler'
```
from flask import Flask, jsonify, request
import socket
from capture import handle_capture, clear_images_dir
from logging import new_system_log, clear_event_logs, clear_system_logs
```

**Response**:
<br>
In your code, you're importing new_system_log and other logging-related functions from logging.
However, Python's built-in logging module does not have a new_system_log function, which suggests that you either have a custom logging module in your project named logging.py, or new_system_log is defined elsewhere in your project.
<br><br><br><br>
**Prompt**:
<br>
Write unit test for the following class: ***I provided the Capture class***
<br><br>
**Response**:
```
import unittest
from unittest.mock import patch, MagicMock
from capture import Capture  # Assuming the class is in capture.py


class TestCapture(unittest.TestCase):
    @patch('capture.VideoCapture')  # Mock the VideoCapture class
    @patch('capture.imwrite')  # Mock the imwrite function
    @patch('capture.makedirs')  # Mock makedirs
    @patch('capture.path.exists')  # Mock path.exists
    def test_handle_capture_success(self, mock_exists, mock_makedirs, mock_imwrite, mock_VideoCapture):
        # Setup the mocks
        mock_exists.return_value = False  # Simulate that the directory does not exist
        mock_imwrite.return_value = True  # Simulate that the image was saved successfully

        # Mock the behavior of the VideoCapture object
        mock_cam = MagicMock()
        mock_VideoCapture.return_value = mock_cam
        mock_cam.read.return_value = (True, 'fake_image_data')  # Simulate successful image capture

        # Initialize Capture instance
        capture = Capture()

        # Call the handle_capture method
        result = capture.handle_capture(cam_port=0)

        # Assertions
        self.assertEqual(result['event_type'], 'Camera Capture')
        self.assertIn('timestamp', result)
        self.assertTrue(result['image_filename'].endswith('.png'))

        # Check that makedirs was called to create the images directory
        mock_makedirs.assert_called_once_with(capture.images_dir)

        # Check that imwrite was called with the correct parameters
        timestamp = result['timestamp']
        mock_imwrite.assert_called_once_with(f"{capture.images_dir}/{timestamp}.png", 'fake_image_data')

    @patch('capture.VideoCapture')  # Mock the VideoCapture class
    def test_handle_capture_camera_error(self, mock_VideoCapture):
        # Mock the behavior of the VideoCapture object
        mock_cam = MagicMock()
        mock_VideoCapture.return_value = mock_cam
        mock_cam.read.return_value = (False, None)  # Simulate failed image capture

        # Initialize Capture instance
        capture = Capture()

        # Call the handle_capture method and assert that it raises a ValueError
        with self.assertRaises(ValueError):
            capture.handle_capture(cam_port=0)

    @patch('capture.VideoCapture')  # Mock the VideoCapture class
    @patch('capture.imwrite')  # Mock the imwrite function
    def test_handle_capture_image_save_error(self, mock_imwrite, mock_VideoCapture):
        # Setup the mocks
        mock_imwrite.return_value = False  # Simulate a failed image save

        # Mock the behavior of the VideoCapture object
        mock_cam = MagicMock()
        mock_VideoCapture.return_value = mock_cam
        mock_cam.read.return_value = (True, 'fake_image_data')  # Simulate successful image capture

        # Initialize Capture instance
        capture = Capture()

        # Call the handle_capture method and assert that it raises a ValueError
        with self.assertRaises(ValueError):
            capture.handle_capture(cam_port=0)

    @patch('capture.VideoCapture')  # Mock the VideoCapture class
    def test_check_incoming_port_valid(self, mock_VideoCapture):
        capture = Capture()

        # Test with valid integer port
        self.assertEqual(capture._Capture__check_incoming_port(0), 0)
        self.assertEqual(capture._Capture__check_incoming_port(1), 1)

    def test_check_incoming_port_invalid(self):
        capture = Capture()

        # Test with invalid port type
        with self.assertRaises(ValueError):
            capture._Capture__check_incoming_port("invalid_port")

    @patch('capture.shutil.rmtree')  # Mock rmtree
    @patch('capture.path.exists')  # Mock path.exists
    def test_clear_images_dir(self, mock_exists, mock_rmtree):
        capture = Capture()

        # Simulate that the directory exists
        mock_exists.return_value = True

        # Call clear_images_dir
        capture.clear_images_dir()

        # Assert that rmtree was called to delete the images directory
        mock_rmtree.assert_called_once_with(capture.images_dir)

    @patch('capture.path.exists')  # Mock path.exists
    def test_clear_images_dir_no_dir(self, mock_exists):
        capture = Capture()

        # Simulate that the directory does not exist
        mock_exists.return_value = False

        # Call clear_images_dir
        capture.clear_images_dir()

        # Assert that rmtree was not called since the directory does not exist
        with patch('capture.shutil.rmtree') as mock_rmtree:
            mock_rmtree.assert_not_called()


if __name__ == '__main__':
    unittest.main()
```
<br><br>
**Prompt**:
<br>
Write unit test for the following class: ***I provided the Logs class***
<br>

**Response**:
```
import unittest
from unittest.mock import patch, mock_open
import os
import json
from io import StringIO
from time import time
from logs import Logs


class TestLogs(unittest.TestCase):

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists", return_value=False)  # Mocking that the log file doesn't exist
    def test_new_event_log_creates_log_file_and_writes_event(self, mock_exists, mock_open):
        log_data = {
            "timestamp": "2024-12-19T10:00:00",
            "event_type": "INFO",
            "message": "Event created successfully"
        }
        
        # Initialize the Logs class
        logs = Logs()

        # Run the method
        logs.new_event_log(log_data)

        # Check if the events file was created
        mock_open.assert_called_once_with('../logs/events.json', 'w')
        
        # Retrieve the JSON content that was written
        written_data = json.loads(mock_open().write.call_args[0][0])
        
        # Check if the event was correctly appended to the "events" list
        self.assertIn('events', written_data)
        self.assertEqual(len(written_data['events']), 1)
        self.assertEqual(written_data['events'][0], log_data)

    @patch("builtins.open", new_callable=mock_open)
    def test_check_incoming_events_log_missing_timestamp(self, mock_open):
        log_data = {
            "event_type": "INFO",
            "message": "Missing timestamp"
        }

        # Initialize the Logs class
        logs = Logs()

        # Expecting KeyError for missing timestamp
        with self.assertRaises(KeyError):
            logs._Logs__check_incoming_events_log(log_data)

    @patch("builtins.open", new_callable=mock_open)
    def test_check_incoming_events_log_missing_event_type(self, mock_open):
        log_data = {
            "timestamp": "2024-12-19T10:00:00",
            "message": "Missing event type"
        }

        # Initialize the Logs class
        logs = Logs()

        # Expecting KeyError for missing event_type
        with self.assertRaises(KeyError):
            logs._Logs__check_incoming_events_log(log_data)

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists", return_value=False)  # Mocking that the log file doesn't exist
    def test_create_events_log_file_creates_new_file(self, mock_exists, mock_open):
        logs = Logs()
        
        # Run the method
        logs._Logs__create_events_log_file()

        # Ensure that the file creation was called
        mock_open.assert_called_once_with('../logs/events.json', 'w')

    @patch("builtins.open", new_callable=mock_open)
    def test_update_json_file(self, mock_open):
        logs = Logs()
        json_content = {"events": [{"timestamp": "2024-12-19T10:00:00", "event_type": "INFO"}]}
        
        # Run the method
        logs._Logs__update_json_file('../logs/events.json', json_content)
        
        # Check if the file was written with the correct content
        mock_open.assert_called_once_with('../logs/events.json', 'w')
        written_data = json.loads(mock_open().write.call_args[0][0])
        self.assertEqual(written_data, json_content)

    @patch("builtins.open", new_callable=mock_open)
    def test_new_system_log(self, mock_open):
        logs = Logs()
        
        # Test writing a normal log
        logs.new_system_log("System started")
        mock_open.assert_called_once_with('../logs/system.log', 'a')
        written_log = mock_open().write.call_args[0][0]
        self.assertIn("[LOG]", written_log)
        self.assertIn("System started", written_log)
        
        # Test writing an error log
        logs.new_system_log("System error occurred", is_error=True)
        mock_open.assert_called_with('../logs/system.log', 'a')
        written_log = mock_open().write.call_args[0][0]
        self.assertIn("[ERR]", written_log)
        self.assertIn("System error occurred", written_log)

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists", return_value=False)
    def test_create_systems_log_file_creates_file(self, mock_exists, mock_open):
        logs = Logs()
        
        # Run the method
        logs._Logs__create_systems_log_file()

        # Ensure the file creation was called
        mock_open.assert_called_once_with('../logs/system.log', 'x')

    @patch("builtins.open", new_callable=mock_open)
    def test_clear_event_logs(self, mock_open):
        logs = Logs()
        
        # Run the method to clear event logs
        logs.clear_event_logs()
        
        # Ensure the file is cleared and recreated
        mock_open.assert_called_with('../logs/events.json', 'w')

    @patch("builtins.open", new_callable=mock_open)
    def test_clear_system_logs(self, mock_open):
        logs = Logs()
        
        # Run the method to clear system logs
        logs.clear_system_logs()
        
        # Ensure the system log is cleared
        mock_open.assert_called_with('../logs/system.log', 'w')


if __name__ == '__main__':
    unittest.main()
```
<br><br>
**Prompt**:
<br>
I have two tests that test the code block below:
```
def clear_images_dir(self) -> None:
        if os.path.exists(self.images_dir):
            shutil.rmtree(self.images_dir)
        self.__create_images_dir()

@patch('os.path.exists', return_value = True)
@patch('shutil.rmtree')
def test_clear_images_dir(self, mock_rmtree, mock_image_dir_exists):
    self.capture.clear_images_dir()
    mock_rmtree.assert_called_once_with(self.capture.images_dir)

@patch('shutil.rmtree')
def test_clear_images_dir_no_dir(self, mock_rmtree):
    self.capture.images_dir = 'dummy-dir'
    self.capture.clear_images_dir()

    mock_rmtree.assert_not_called()
```
How can I prevent ``self.__create_images_dir()`` from being called? The test code is currently creating a new 'dummy-dir' directory
<br>

**Response**:
```
@patch('os.path.exists', return_value=True)
@patch('shutil.rmtree')
@patch.object(MyClass, '_MyClass__create_images_dir')
def test_clear_images_dir(self, mock_create_images_dir, mock_rmtree, mock_image_dir_exists):
    self.capture.clear_images_dir()

    mock_rmtree.assert_called_once_with(self.capture.images_dir)
```
<br><br>
**Prompt**:
<br>
Please write unit test for the following functions:
<ol>
<li>new_event_log</li>
<li>__update_json_file</li>
</ol>

```
def new_event_log(self, log) -> None:
        self.__check_incoming_events_log(log)
        self.__create_events_log_file()

        with open(self.events_filename) as events_file:
            try:
                events_file_json = json.load(events_file)
            except json.JSONDecodeError as err:
                raise ValueError(f"Invalid JSON in file {self.events_filename}: {err}")

        if not events_file_json.get('events'):
            events_file_json['events'] = []

        events_file_json['events'].append(log)
        self.__update_json_file(self.events_filename, events_file_json)

    def __check_incoming_events_log(self, log) -> None:
        if not log.get('timestamp'):
            raise KeyError("No timestamp provided in event log")
        if not log.get('event_type'):
            raise KeyError("No event_type provided in event log")

    def __create_events_log_file(self) -> None:
        if not os.path.exists(self.events_filename) or os.stat(self.events_filename).st_size == 0:
            self.__update_json_file(self.events_filename, {"events": []})

    def __update_json_file(self, filename, json_content) -> None:
        try:
            with open(filename, 'w') as file:
                json.dump(json_content, file, indent=4)
        except (IOError, OSError) as err:
            raise RuntimeError(f"An error occurred while trying to write to the file {filename}: {err}")
        except (TypeError, json.JSONDecodeError) as err:
            raise ValueError(f"An error occurred while serializing the content to JSON for {filename}: {err}")
```
<br>

**Response**:
```
import unittest
from unittest.mock import mock_open, patch, MagicMock
import json
import os


class TestEventLog(unittest.TestCase):
    def setUp(self):
        # Mock initialization for event log instance
        self.event_log_instance = MagicMock()
        self.event_log_instance.events_filename = 'test_events.json'

    @patch('builtins.open', new_callable=mock_open, read_data='{"events": []}')
    def test_new_event_log_valid_log(self, mock_file):
        log = {'timestamp': '2024-12-20T00:00:00Z', 'event_type': 'user_login'}
        
        # Simulate that the __update_json_file method is called correctly
        self.event_log_instance.__update_json_file = MagicMock()

        self.event_log_instance.new_event_log(log)

        # Check that the file is opened with the correct filename
        mock_file.assert_called_once_with(self.event_log_instance.events_filename, 'r')

        # Check that __update_json_file was called to update the file with the new log
        self.event_log_instance.__update_json_file.assert_called_once_with(
            self.event_log_instance.events_filename,
            {'events': [log]}
        )

    @patch('builtins.open', new_callable=mock_open, read_data='{}')
    def test_new_event_log_invalid_json(self, mock_file):
        log = {'timestamp': '2024-12-20T00:00:00Z', 'event_type': 'user_login'}
        
        with self.assertRaises(ValueError):
            self.event_log_instance.new_event_log(log)

    @patch('os.path.exists', return_value=False)
    @patch('builtins.open', new_callable=mock_open)
    def test_create_events_log_file_creates_new_file(self, mock_file, mock_exists):
        # Test case where file does not exist and should be created
        self.event_log_instance.__create_events_log_file()

        # Check that the file was opened for writing
        mock_file.assert_called_once_with(self.event_log_instance.events_filename, 'w')

    @patch('os.path.exists', return_value=True)
    @patch('os.stat', return_value=MagicMock(st_size=0))
    @patch('builtins.open', new_callable=mock_open)
    def test_create_events_log_file_creates_empty_json(self, mock_file, mock_stat, mock_exists):
        # Test case where file exists but is empty
        self.event_log_instance.__create_events_log_file()

        # Check that the file was opened for writing with empty events list
        mock_file.assert_called_once_with(self.event_log_instance.events_filename, 'w')
        mock_file().write.assert_called_once_with('{"events": []}\n')

    def test_check_incoming_events_log_valid(self):
        log = {'timestamp': '2024-12-20T00:00:00Z', 'event_type': 'user_login'}
        
        # Should not raise any exception for a valid log
        try:
            self.event_log_instance.__check_incoming_events_log(log)
        except KeyError:
            self.fail("KeyError raised unexpectedly!")

    def test_check_incoming_events_log_missing_timestamp(self):
        log = {'event_type': 'user_login'}
        
        # Should raise KeyError for missing timestamp
        with self.assertRaises(KeyError):
            self.event_log_instance.__check_incoming_events_log(log)

    def test_check_incoming_events_log_missing_event_type(self):
        log = {'timestamp': '2024-12-20T00:00:00Z'}
        
        # Should raise KeyError for missing event_type
        with self.assertRaises(KeyError):
            self.event_log_instance.__check_incoming_events_log(log)

    @patch('builtins.open', new_callable=mock_open)
    def test_update_json_file(self, mock_file):
        json_content = {'events': [{'timestamp': '2024-12-20T00:00:00Z', 'event_type': 'user_login'}]}
        
        # Simulate writing to the file using __update_json_file method
        self.event_log_instance.__update_json_file(self.event_log_instance.events_filename, json_content)

        # Check if the file was opened for writing with correct content
        mock_file.assert_called_once_with(self.event_log_instance.events_filename, 'w')
        mock_file().write.assert_called_once_with('{\n    "events": [\n        {\n            "timestamp": "2024-12-20T00:00:00Z",\n            "event_type": "user_login"\n        }\n    ]\n}\n')

    @patch('builtins.open', new_callable=mock_open)
    def test_update_json_file_io_error(self, mock_file):
        # Simulate an IOError when attempting to write to the file
        mock_file.side_effect = IOError("File write error")
        
        with self.assertRaises(RuntimeError):
            self.event_log_instance.__update_json_file(self.event_log_instance.events_filename, {'events': []})

    @patch('builtins.open', new_callable=mock_open)
    def test_update_json_file_type_error(self, mock_file):
        # Simulate a TypeError during JSON serialization
        mock_file.side_effect = TypeError("Serialization error")
        
        with self.assertRaises(ValueError):
            self.event_log_instance.__update_json_file(self.event_log_instance.events_filename, {'events': []})


if __name__ == '__main__':
    unittest.main()
```