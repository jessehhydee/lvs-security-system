import sys
import os
sys.path.append("..")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
import unittest
from unittest.mock import patch, MagicMock
from src.capture import Capture

class TestCapture(unittest.TestCase):
    def setUp(self):
        self.capture = Capture()

    @patch('cv2.VideoCapture')
    @patch('os.path.exists', return_value = True)
    @patch('cv2.imwrite', return_value = True)
    def test_handle_capture_success(self, mock_imwrite, mock_image_dir_exists, mock_VideoCapture):
        mock_cam = MagicMock()
        mock_VideoCapture.return_value = mock_cam
        mock_cam.read.return_value = (True, 'dummy_image_data')

        result = self.capture.handle_capture()

        self.assertEqual(result['event_type'], 'Camera Capture')
        self.assertIn('timestamp', result)
        self.assertTrue(result['image_filename'].endswith('.png'))

    @patch('cv2.VideoCapture')
    def test_handle_capture_camera_error(self, mock_VideoCapture):
        mock_cam = MagicMock()
        mock_VideoCapture.return_value = mock_cam
        mock_cam.read.return_value = (False, None)

        with self.assertRaises(ValueError):
            self.capture.handle_capture()

    @patch('cv2.VideoCapture')
    @patch('os.path.exists', return_value = True)
    @patch('cv2.imwrite', return_value = False)
    def test_handle_capture_image_save_error(self, mock_imwrite, mock_image_dir_exists, mock_VideoCapture):
        mock_cam = MagicMock()
        mock_VideoCapture.return_value = mock_cam
        mock_cam.read.return_value = (True, 'dummy_image_data')

        with self.assertRaises(ValueError):
            self.capture.handle_capture()

    def test___check_incoming_port_valid(self):
        self.assertEqual(self.capture._Capture__check_incoming_port(0), 0)
        self.assertEqual(self.capture._Capture__check_incoming_port(1), 1)

    def test___check_incoming_port_invalid(self):
        with self.assertRaises(ValueError):
            self.capture._Capture__check_incoming_port("invalid_port")

    @patch('os.path.exists', return_value = True)
    @patch('shutil.rmtree')
    @patch.object(Capture, '_Capture__create_images_dir')
    def test_clear_images_dir(self, mock_create_images_dir, mock_rmtree, mock_image_dir_exists):
        self.capture.clear_images_dir()
        mock_rmtree.assert_called_once_with(self.capture.images_dir)

    @patch('shutil.rmtree')
    @patch.object(Capture, '_Capture__create_images_dir')
    def test_clear_images_dir_no_dir(self, mock_create_images_dir, mock_rmtree):
        self.capture.images_dir = 'dummy-dir'
        self.capture.clear_images_dir()

        mock_rmtree.assert_not_called()

if __name__ == '__main__':
    unittest.main()