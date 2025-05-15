import cv2
import mediapipe as mp
import numpy as np
from . import config # Assuming config.py exists for potential configurations
from .video_input import VideoInput # Assuming video_input.py is in the same directory
import time

class VisionModule:
    def __init__(self):
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_objectron = mp.solutions.objectron # For 3D object detection
        self.mp_object_detection = mp.solutions.object_detection # For 2D object detection
        self.mp_hands = mp.solutions.hands
        self.mp_face_detection = mp.solutions.face_detection

        # Initialize models - can be done on first use or here
        # For object detection (2D), which is generally faster and good for "what is this"
        self.object_detector = self.mp_object_detection.ObjectDetection(
            model_selection=0, # 0 for general purpose model, 1 for more fine-grained
            min_detection_confidence=0.5)
        
        # For more specific tasks, other models can be initialized as needed
        # self.hands_detector = self.mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5)
        # self.face_detector = self.mp_face_detection.FaceDetection(min_detection_confidence=0.5)
        # self.objectron_detector = self.mp_objectron.Objectron(static_image_mode=False, max_num_objects=5, min_detection_confidence=0.5, model_name=\'Cup\') # Example: Cup
        print("VisionModule: Initialized MediaPipe Object Detection.")

    def detect_objects(self, frame: np.ndarray) -> tuple[np.ndarray, list[dict]]:
        """
        Detects objects in a given frame using MediaPipe ObjectDetection.

        Args:
            frame: The input image/frame (NumPy array, BGR format from OpenCV).

        Returns:
            A tuple containing:
            - annotated_frame: The frame with bounding boxes drawn around detected objects.
            - objects: A list of dictionaries, where each dictionary contains information
                       about a detected object (label, score, box).
        """
        if frame is None:
            return None, []

        # Convert the BGR image to RGB, and make it non-writeable for performance
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image_rgb.flags.writeable = False

        # Process the image and find objects
        results = self.object_detector.process(image_rgb)

        # To draw the bounding boxes, make the image writeable again
        annotated_frame = frame.copy()
        detected_objects_info = []

        if results.detections:
            for detection in results.detections:
                # detection.label_id gives index, detection.score gives confidence
                # detection.location_data.relative_bounding_box gives normalized coords
                
                # Get the label - MediaPipe ObjectDetection provides label_id and score directly.
                # The actual string label might need mapping if not directly provided or if using a custom model.
                # For the default model, scores often come with a list of labels.
                # Here, we assume `detection.label_id` can be used or we might need a label map.
                # For simplicity, we will try to get the first label if available in `detection.label` (newer versions)
                # or use a placeholder if only `label_id` is present.
                
                label = "UnknownObject"
                if hasattr(detection, "label") and detection.label:
                    label = detection.label[0] # Assuming label is a list of strings
                elif hasattr(detection, "label_id") and detection.label_id:
                    # You might need a mapping from label_id to string names for some models
                    # For now, just use the ID as a placeholder if no direct label string
                    label = f"ID:{detection.label_id[0] if isinstance(detection.label_id, list) else detection.label_id}"
                
                score = detection.score[0] if isinstance(detection.score, list) else detection.score # Confidence score
                
                if score < self.object_detector.min_detection_confidence:
                    continue

                # Get bounding box
                box = detection.location_data.relative_bounding_box
                h, w, _ = annotated_frame.shape
                xmin = int(box.xmin * w)
                ymin = int(box.ymin * h)
                width = int(box.width * w)
                height = int(box.height * h)
                
                cv2.rectangle(annotated_frame, (xmin, ymin), (xmin + width, ymin + height), (0, 255, 0), 2)
                cv2.putText(annotated_frame, f"{label}: {score:.2f}", (xmin, ymin - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                detected_objects_info.append({
                    "label": label,
                    "score": float(score),
                    "box_normalized": {"xmin": box.xmin, "ymin": box.ymin, "width": box.width, "height": box.height},
                    "box_pixels": {"xmin": xmin, "ymin": ymin, "width": width, "height": height}
                })
        
        return annotated_frame, detected_objects_info

    def analyze_frame_for_prompt(self, frame: np.ndarray) -> str:
        """
        Analyzes a frame to generate a textual description of detected objects for an LLM prompt.
        """
        _, objects = self.detect_objects(frame)
        if not objects:
            return "No distinct objects were detected in the current view."
        
        description = "In the current view, the following objects are detected: "
        object_descriptions = []
        for obj in objects:
            object_descriptions.append(f"a {obj["label"]} (confidence: {obj["score"]:.2f})")
        
        if len(object_descriptions) > 1:
            description += ", ".join(object_descriptions[:-1]) + " and " + object_descriptions[-1] + "."
        elif object_descriptions:
            description += object_descriptions[0] + "."
        else: # Should not happen if objects list was not empty
            return "No distinct objects were detected after filtering."
            
        return description

    def close(self):
        """Release MediaPipe resources."""
        if hasattr(self, 'object_detector') and self.object_detector:
            self.object_detector.close()
        # Close other detectors if they were initialized
        # if hasattr(self, 'hands_detector') and self.hands_detector: self.hands_detector.close()
        # if hasattr(self, 'face_detector') and self.face_detector: self.face_detector.close()
        # if hasattr(self, 'objectron_detector') and self.objectron_detector: self.objectron_detector.close()
        print("VisionModule: MediaPipe resources released.")

    def __del__(self):
        self.close()

if __name__ == '__main__':
    print("Testing VisionModule...")
    # This test requires a connected camera and OpenCV for display.
    video_input = VideoInput(camera_index=0, fps_limit=5) # Lower FPS for testing vision processing
    vision_module = VisionModule()

    video_input.start_capture()

    if not video_input.running:
        print("Failed to start video input. Exiting VisionModule test.")
    else:
        print("Displaying video with object detection. Press 'q' to quit.")
        cv2.namedWindow("Vision Test", cv2.WINDOW_NORMAL)
        try:
            while True:
                frame = video_input.get_frame(timeout=0.2)
                if frame is not None:
                    annotated_frame, detected_objects = vision_module.detect_objects(frame)
                    
                    if annotated_frame is not None:
                        cv2.imshow("Vision Test", annotated_frame)
                    
                    if detected_objects:
                        # print(f"Detected: {detected_objects}")
                        # Pass, print only if changed or periodically to avoid spam
                        pass 

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        print("Quit signal received.")
                        break
                else:
                    # print("Waiting for frame...")
                    time.sleep(0.05)
        except KeyboardInterrupt:
            print("Test interrupted by user.")
        finally:
            video_input.stop_capture()
            vision_module.close()
            cv2.destroyAllWindows()
            print("VisionModule test finished.")

