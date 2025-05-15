import cv2
import queue
import threading
import time
from . import config

class VideoInput:
    def __init__(self, camera_index=0, fps_limit=15):
        self.camera_index = camera_index
        self.cap = None
        self.running = False
        self.frame_queue = queue.Queue(maxsize=5) # Limit queue size to prevent stale frames
        self.thread = None
        self.fps_limit = fps_limit # Limit FPS to reduce CPU load on Raspberry Pi
        self.frame_interval = 1.0 / fps_limit if fps_limit > 0 else 0

    def _capture_loop(self):
        last_frame_time = 0
        while self.running:
            if self.cap and self.cap.isOpened():
                current_time = time.time()
                if current_time - last_frame_time < self.frame_interval:
                    time.sleep(self.frame_interval - (current_time - last_frame_time))
                
                ret, frame = self.cap.read()
                last_frame_time = time.time()
                if ret:
                    if not self.frame_queue.full():
                        self.frame_queue.put(frame, block=False) # Non-blocking put
                    else:
                        try:
                            self.frame_queue.get_nowait() # Discard oldest frame if full
                            self.frame_queue.put(frame, block=False)
                        except queue.Empty:
                            pass # Should not happen if full was true
                else:
                    print("VideoInput: Failed to grab frame. Camera might be disconnected.")
                    # Optionally, try to reopen the camera or signal an error
                    time.sleep(0.5) # Wait a bit before retrying or stopping
            else:
                print("VideoInput: Camera not opened. Stopping capture loop.")
                self.running = False # Stop if camera is not available
                break
        print("VideoInput: Capture loop stopped.")

    def start_capture(self):
        if self.running:
            print("VideoInput is already capturing.")
            return

        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            if not self.cap.isOpened():
                print(f"Error: Could not open video device at index {self.camera_index}.")
                print("Please check your camera connection and permissions.")
                # List available cameras (this might not always work or be accurate)
                # for i in range(5): # Check first 5 indices
                #     cap_test = cv2.VideoCapture(i)
                #     if cap_test.isOpened():
                #         print(f"Camera found at index: {i}")
                #         cap_test.release()
                self.cap = None
                return
            
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640) # Set a reasonable resolution
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, self.fps_limit if self.fps_limit > 0 else 30) # Request FPS

            self.running = True
            self.thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.thread.start()
            print(f"VideoInput: Started video capture from camera index {self.camera_index} at ~{self.fps_limit} FPS.")
        except Exception as e:
            print(f"Error starting video capture: {e}")
            if self.cap:
                self.cap.release()
            self.cap = None
            self.running = False

    def stop_capture(self):
        if not self.running:
            print("VideoInput is not currently capturing.")
            return

        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2) # Wait for the thread to finish
        
        if self.cap:
            self.cap.release()
            self.cap = None
        print("VideoInput: Stopped video capture.")
        # Clear the queue
        while not self.frame_queue.empty():
            try:
                self.frame_queue.get_nowait()
            except queue.Empty:
                continue

    def get_frame(self, timeout=0.1):
        """Gets a frame from the queue. Returns None if timeout or not running."""
        if not self.running:
            # print("VideoInput is not running. Cannot get frame.")
            return None
        try:
            return self.frame_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def __del__(self):
        self.stop_capture() # Ensure resources are released

if __name__ == '__main__':
    print("Testing VideoInput module...")
    video_input = VideoInput(camera_index=0, fps_limit=10) # Use camera 0, limit to 10 FPS
    video_input.start_capture()

    if not video_input.running:
        print("Failed to start video input. Exiting test.")
    else:
        print("Capturing video for 5 seconds. Press Ctrl+C to stop early.")
        # In a real app, you might display the frames or process them.
        # For this test, we just try to get frames.
        # cv2.namedWindow("Video Test", cv2.WINDOW_NORMAL)
        start_time = time.time()
        frames_received = 0
        try:
            while time.time() - start_time < 5:
                frame = video_input.get_frame(timeout=0.1)
                if frame is not None:
                    frames_received += 1
                    # print(f"Got frame of shape: {frame.shape}")
                    # cv2.imshow("Video Test", frame)
                    # if cv2.waitKey(1) & 0xFF == ord(\'q\'):
                    #    break
                else:
                    # print("No frame received in this iteration.")
                    pass
                time.sleep(0.05) # Simulate some processing or reduce busy-wait
        except KeyboardInterrupt:
            print("Test interrupted by user.")
        finally:
            video_input.stop_capture()
            # cv2.destroyAllWindows()
            print(f"Received {frames_received} frames during the test.")
            if frames_received == 0 and video_input.cap is not None : # Check if cap was successfully opened
                print("No frames received. Ensure your camera is working and accessible by OpenCV.")
    print("VideoInput module test finished.")

