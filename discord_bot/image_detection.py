import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2

class imageDetection:
    def __init__(self):
        pass

    @staticmethod
    def count_faces(image_path):
        """
        Takes an image path and returns the number of faces detected as an integer.
        """
        # 1. Define the path to your TFLite model
        model_path = r'discord_bot\imageModel\blaze_face_short_range.tflite'

        # 2. Configure the Face Detector
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.FaceDetectorOptions(base_options=base_options)
        
        # 3. Create the detector
        with vision.FaceDetector.create_from_options(options) as detector:
            
            # 4. Load the image using MediaPipe's image format
            try:
                mp_image = mp.Image.create_from_file(image_path)
            except Exception as e:
                print(f"Error loading image: {e}")
                return 0

            # 5. Detect faces
            detection_result = detector.detect(mp_image)
            
            # 6. Return the integer count
            return len(detection_result.detections) #fuck vsc