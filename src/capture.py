import os
import shutil
import time
import cv2

class Capture:
    images_dir = "../image-captures"

    """
    Method captures an image using the device's webcam and saves it to disk.
    If successful, updates event log with new image information.
    Camera capture info came from: https://www.geeksforgeeks.org/how-to-capture-a-image-from-webcam-in-python/
    
    Returns:
        dict: A dictionary containing event details, including a timestamp, event type, and image filename.
    """
    def handle_capture(self, cam_port = 0) -> dict:
        cam_port = self.__check_incoming_port(cam_port)

        cam = cv2.VideoCapture(cam_port)
        result, image = cam.read()

        if not result:
            raise ValueError("An error occurred capturing the image, ensure you are targeting the correct camera port")

        self.__create_images_dir()

        timestamp = time.strftime("%Y_%m_%d__%H_%M_%S")
        image_file_created = cv2.imwrite(f"{self.images_dir}/{timestamp}.png", image)

        if not image_file_created:
            raise ValueError("An error occurred saving image capture to file")

        return {
            "timestamp": timestamp,
            "event_type": "Camera Capture",
            "image_filename": f"{timestamp}.png"
        }

    """
    Returns:
        int: An integer that indicates the camera port to use to capture an image
    """
    def __check_incoming_port(self, cam_port) -> int:
        try:
            cam_port = int(cam_port)
        except ValueError:
            raise ValueError("cam_port needs to be an integer")
        return cam_port

    def __create_images_dir(self) -> None:
        if not os.path.exists(self.images_dir):
            os.makedirs(self.images_dir)

    def clear_images_dir(self) -> None:
        if os.path.exists(self.images_dir):
            shutil.rmtree(self.images_dir)
        self.__create_images_dir()