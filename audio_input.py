import pyaudio
import queue
from . import config

class AudioInput:
    def __init__(self, sample_rate=config.AUDIO_SAMPLE_RATE, channels=config.AUDIO_CHANNELS, 
                 chunk_size=config.AUDIO_CHUNK_SIZE, device_index=config.AUDIO_INPUT_DEVICE_INDEX):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.device_index = device_index
        self.audio_queue = queue.Queue()
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.running = False

    def _callback(self, in_data, frame_count, time_info, status):
        if self.running:
            self.audio_queue.put(in_data)
        return (None, pyaudio.paContinue)

    def start_listening(self):
        if self.running:
            print("AudioInput is already listening.")
            return

        try:
            self.stream = self.p.open(format=pyaudio.paInt16, # Standard format for Vosk
                                     channels=self.channels,
                                     rate=self.sample_rate,
                                     input=True,
                                     frames_per_buffer=self.chunk_size,
                                     input_device_index=self.device_index,
                                     stream_callback=self._callback)
            self.running = True
            self.stream.start_stream()
            print("AudioInput: Started listening...")
        except Exception as e:
            print(f"Error starting audio input stream: {e}")
            if "Invalid input device" in str(e) or "No Default Input Device Available" in str(e):
                print("Please check your microphone connection and configuration.")
                print("Available audio devices:")
                for i in range(self.p.get_device_count()):
                    dev_info = self.p.get_device_info_by_index(i)
                    if dev_info.get('maxInputChannels') > 0:
                        print(f"  Device {i}: {dev_info.get('name')} (Input Channels: {dev_info.get('maxInputChannels')})")
            self.running = False
            self.stream = None # Ensure stream is None if not opened

    def stop_listening(self):
        if not self.running or not self.stream:
            print("AudioInput is not currently listening or stream is not active.")
            return
        
        self.running = False
        try:
            if self.stream.is_active(): # Check if stream is active before stopping/closing
                self.stream.stop_stream()
                self.stream.close()
            print("AudioInput: Stopped listening.")
        except Exception as e:
            print(f"Error stopping audio input stream: {e}")
        finally:
            self.stream = None
            # Clear the queue after stopping
            while not self.audio_queue.empty():
                try:
                    self.audio_queue.get_nowait()
                except queue.Empty:
                    continue

    def get_audio_chunk(self, timeout=1):
        """Gets an audio chunk from the queue. Returns None if timeout."""
        if not self.running:
            # print("AudioInput is not running. Cannot get audio chunk.")
            return None
        try:
            return self.audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def __del__(self):
        if self.stream and self.stream.is_active():
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()
        print("AudioInput: Resources released.")

if __name__ == '__main__':
    import time
    print("Testing AudioInput module...")
    audio_input = AudioInput()
    audio_input.start_listening()

    if not audio_input.running:
        print("Failed to start audio input. Exiting test.")
    else:
        print("Listening for 5 seconds. Speak into your microphone.")
        start_time = time.time()
        frames_collected = 0
        try:
            while time.time() - start_time < 5:
                chunk = audio_input.get_audio_chunk(timeout=0.1) # Non-blocking with small timeout
                if chunk:
                    # In a real application, you would process this chunk (e.g., send to STT)
                    # print(f"Got audio chunk of size: {len(chunk)} bytes")
                    frames_collected += 1
                time.sleep(0.01) # Small sleep to prevent busy-waiting if queue is empty
        except KeyboardInterrupt:
            print("Test interrupted by user.")
        finally:
            audio_input.stop_listening()
            print(f"Collected {frames_collected} audio chunks during the test.")
            if frames_collected == 0 and audio_input.running:
                 print("No audio chunks collected. Ensure your microphone is working and selected correctly.")
    print("AudioInput module test finished.")

