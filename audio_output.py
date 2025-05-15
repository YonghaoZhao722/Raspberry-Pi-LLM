import pyaudio
import wave
import os
from . import config

class AudioOutput:
    def __init__(self, device_index=None): # Allow specifying output device
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.device_index = device_index
        # You might want to query available output devices if device_index is None
        # and select a default, or let PyAudio choose.

    def play_audio_data(self, audio_data: bytes, sample_rate: int, channels: int, sample_width: int):
        """
        Plays raw audio data.

        Args:
            audio_data: Raw audio bytes.
            sample_rate: Sample rate of the audio (e.g., 22050 for Piper default).
            channels: Number of audio channels (e.g., 1 for mono).
            sample_width: Sample width in bytes (e.g., 2 for 16-bit audio).
        """
        if self.stream and self.stream.is_active():
            print("AudioOutput: Stream is already active. Stopping current playback.")
            self.stop_playback()

        try:
            self.stream = self.p.open(format=self.p.get_format_from_width(sample_width),
                                     channels=channels,
                                     rate=sample_rate,
                                     output=True,
                                     output_device_index=self.device_index)
            
            print(f"AudioOutput: Playing audio data ({len(audio_data)} bytes, {sample_rate}Hz, {channels}ch, {sample_width*8}-bit).")
            self.stream.start_stream() # Ensure stream is started before writing
            self.stream.write(audio_data)
            # self.stream.stop_stream() # Wait for playback to finish before stopping implicitly by close()
            # self.stream.close()
            print("AudioOutput: Finished playing audio data.")
            return True
        except Exception as e:
            print(f"Error playing raw audio data: {e}")
            if "Invalid output device" in str(e):
                print("Please check your speaker/audio output configuration.")
                print("Available audio output devices:")
                for i in range(self.p.get_device_count()):
                    dev_info = self.p.get_device_info_by_index(i)
                    if dev_info.get(\'maxOutputChannels
') > 0:
                        print(f"  Device {i}: {dev_info.get(\'name
')} (Output Channels: {dev_info.get(\'maxOutputChannels
')})")
            return False
        finally:
            if self.stream:
                if not self.stream.is_stopped(): # Ensure it's stopped before closing
                    self.stream.stop_stream()
                if self.stream.is_active(): # Should not be active if stopped, but good check
                     self.stream.close() # Close if it was opened
                self.stream = None

    def play_wav_file(self, file_path: str):
        if not os.path.exists(file_path):
            print(f"AudioOutput Error: WAV file not found: {file_path}")
            return False

        if self.stream and self.stream.is_active():
            print("AudioOutput: Stream is already active. Stopping current playback.")
            self.stop_playback()

        try:
            with wave.open(file_path, \'rb\
') as wf:
                sample_rate = wf.getframerate()
                channels = wf.getnchannels()
                sample_width = wf.getsampwidth()
                
                self.stream = self.p.open(format=self.p.get_format_from_width(sample_width),
                                         channels=channels,
                                         rate=sample_rate,
                                         output=True,
                                         output_device_index=self.device_index)
                
                print(f"AudioOutput: Playing WAV file: {file_path} ({sample_rate}Hz, {channels}ch, {sample_width*8}-bit).")
                data = wf.readframes(config.AUDIO_CHUNK_SIZE) # Read in chunks
                self.stream.start_stream()
                while data:
                    self.stream.write(data)
                    data = wf.readframes(config.AUDIO_CHUNK_SIZE)
                
                # self.stream.stop_stream() # Implicitly handled by close or wait
                # self.stream.close()
                print(f"AudioOutput: Finished playing {file_path}.")
                return True
        except wave.Error as e:
            print(f"Error opening or reading WAV file {file_path}: {e}")
            return False
        except Exception as e:
            print(f"Error playing WAV file {file_path}: {e}")
            if "Invalid output device" in str(e):
                 print("Please check your speaker/audio output configuration.")
            return False
        finally:
            if self.stream:
                if not self.stream.is_stopped():
                    self.stream.stop_stream()
                if self.stream.is_active():
                    self.stream.close()
                self.stream = None

    def stop_playback(self):
        if self.stream and self.stream.is_active():
            try:
                self.stream.stop_stream()
                self.stream.close()
                print("AudioOutput: Playback stopped and stream closed.")
            except Exception as e:
                print(f"Error stopping playback: {e}")
            finally:
                self.stream = None
        else:
            print("AudioOutput: No active stream to stop.")

    def __del__(self):
        self.stop_playback() # Ensure stream is closed
        self.p.terminate()
        print("AudioOutput: Resources released.")

if __name__ == \'__main__\':
    import time
    print("Testing AudioOutput module...")
    # This test requires a speaker/audio output and a test WAV file.
    # We will use the TTS module to generate a test file if possible.

    # Create a dummy output directory if it doesn\'t exist
    test_audio_dir = "test_audio_output"
    if not os.path.exists(test_audio_dir):
        os.makedirs(test_audio_dir)
    
    test_wav_file = os.path.join(test_audio_dir, "audio_output_test.wav")

    # Attempt to generate a test WAV file using TTSModule
    tts_available = False
    try:
        from .tts_module import TTSModule # Assuming tts_module.py is in the same directory
        tts = TTSModule(language="en")
        if tts.model_path: # Check if TTS is configured
            print("Generating test audio file using TTSModule...")
            if tts.speak("This is a test of the audio output module.", test_wav_file):
                print(f"Test audio file generated: {test_wav_file}")
                tts_available = True
            else:
                print("Failed to generate test audio file with TTS.")
        else:
            print("TTS module not configured, cannot generate test WAV automatically.")
    except ImportError:
        print("TTSModule not found, cannot generate test WAV automatically.")
    except EnvironmentError as e:
        print(f"TTS environment error, cannot generate test WAV: {e}")
    except Exception as e:
        print(f"Unexpected error during TTS setup for audio output test: {e}")

    audio_output = AudioOutput()

    if tts_available and os.path.exists(test_wav_file):
        print(f"\n--- Playing test WAV file: {test_wav_file} ---")
        audio_output.play_wav_file(test_wav_file)
        print("Waiting for 3 seconds after WAV playback...")
        time.sleep(3) # Give some time for playback to finish if it runs in background
    else:
        print("Skipping WAV file playback test as test file is not available.")
        print("You can manually place a WAV file at 	hemed_text_is_not_recognized_by_the_user_facing_tool} and re-run.")

    # Test playing raw data (e.g., from Piper --output-raw)
    # This requires knowing the sample rate, channels, and width from the TTS model.
    # For Piper en_US-lessac-medium, it\'s typically 22050 Hz, 1 channel, 16-bit (2 bytes width)
    if tts_available:
        print("\n--- Playing raw audio data (generated by TTS) ---")
        tts_raw_test_text = "Testing raw audio playback."
        # Assuming TTSModule has speak_to_raw_audio method
        if hasattr(tts, 'speak_to_raw_audio'):
            raw_audio_data = tts.speak_to_raw_audio(tts_raw_test_text)
            if raw_audio_data:
                # Determine params from Piper model (example, may need to get from config)
                # Typically, Piper models are 16-bit mono. Sample rate varies.
                # en_US-lessac-medium is 22050 Hz.
                sample_rate_raw = 22050 # This should ideally come from model config
                channels_raw = 1
                sample_width_raw = 2 # 16-bit
                audio_output.play_audio_data(raw_audio_data, sample_rate_raw, channels_raw, sample_width_raw)
                print("Waiting for 3 seconds after raw audio playback...")
                time.sleep(3)
            else:
                print("Failed to generate raw audio data using TTS.")
        else:
            print("TTSModule does not have speak_to_raw_audio method. Skipping raw audio test.")
    else:
        print("Skipping raw audio playback test as TTS is not available.")

    print("AudioOutput module test finished.")

