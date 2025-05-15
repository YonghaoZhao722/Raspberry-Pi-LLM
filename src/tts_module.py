import os
import subprocess
import wave
from . import config

class TTSModule:
    def __init__(self, language=config.DEFAULT_LANGUAGE):
        self.language = language
        self.model_path, self.config_path = self._get_model_paths()
        self._check_piper_executable()

    def _check_piper_executable(self):
        # This assumes piper executable is in PATH or a known location.
        # For a real deployment, you might need to bundle it or ensure it's installed.
        try:
            subprocess.run(["piper", "--version"], capture_output=True, check=True)
            print("TTSModule: Piper executable found.")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Error: Piper executable not found or not working.")
            print("Please ensure Piper is installed and in your system PATH.")
            print("Download from: https://github.com/rhasspy/piper/releases")
            # Potentially, we could try to download/install it here if permissions allow.
            raise EnvironmentError("Piper TTS executable not found. Please install it.")

    def _get_model_paths(self):
        if self.language == "en":
            model = config.PIPER_MODEL_PATH_EN
            conf = config.PIPER_CONFIG_PATH_EN
        elif self.language == "zh":
            model = config.PIPER_MODEL_PATH_ZH
            conf = config.PIPER_CONFIG_PATH_ZH
        else:
            print(f"Warning: Language {self.language} not supported by TTS, defaulting to English.")
            self.language = "en"
            model = config.PIPER_MODEL_PATH_EN
            conf = config.PIPER_CONFIG_PATH_EN
        
        # These paths might be relative to a data directory or absolute.
        # For now, assume they are findable by piper if placed in a piper data dir or specified fully.
        # We will need to ensure these models are downloaded.
        if not (os.path.exists(model) and os.path.exists(conf)):
            print(f"Warning: Piper model/config for {self.language} not found at specified paths:")
            print(f"Model: {model}")
            print(f"Config: {conf}")
            print("Please download Piper voices and update paths in config.py or ensure piper can find them.")
            print("Voices can be downloaded from: https://rhasspy.github.io/piper-samples/")
            # This is a soft warning for now; piper might auto-download if configured.
        return model, conf

    def set_language(self, language_code):
        if language_code not in config.SUPPORTED_LANGUAGES:
            print(f"Warning: Language {language_code} not in supported list: {config.SUPPORTED_LANGUAGES}. Using default.")
            language_code = config.DEFAULT_LANGUAGE
        
        if self.language != language_code:
            print(f"TTSModule: Changing language from {self.language} to {language_code}")
            self.language = language_code
            self.model_path, self.config_path = self._get_model_paths()

    def speak(self, text: str, output_file_path: str = "output.wav") -> bool:
        """
        Synthesizes speech from text and saves it to a WAV file.

        Args:
            text: The text to synthesize.
            output_file_path: Path to save the output WAV file.

        Returns:
            True if synthesis was successful, False otherwise.
        """
        if not self.model_path or not self.config_path:
            print("TTS Error: Model or config path not set.")
            return False
        
        # Check if model files actually exist before calling piper
        # Piper can auto-download models if they are specified by name (e.g., en_US-lessac-medium)
        # but if full paths are given, they must exist.
        # For simplicity, we assume paths in config.py are either full paths to downloaded models
        # or names that piper can resolve and download.

        command = [
            "piper",
            "--model", self.model_path,
            # Piper might infer config from model, but explicit is safer if paths are full
            # "--config", self.config_path, # Usually not needed if .json is alongside .onnx
            "--output_file", output_file_path
        ]
        
        # For multi-speaker models, add: --speaker <id>
        # Example: if self.language == "en" and "some_multi_speaker_model" in self.model_path:
        #    command.extend(["--speaker", "0"]) 

        try:
            print(f"TTSModule: Synthesizing 	hemed_text_is_not_recognized_by_the_user_facing_tool} to {output_file_path} using model {self.model_path}")
            process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate(input=text.encode("utf-8"))

            if process.returncode != 0:
                print(f"Error during Piper TTS synthesis: {stderr.decode(\'utf-8\', errors=\'ignore
of_the_text_is_not_recognized_by_the_user_facing_tool)}")
                if "Failed to load model" in stderr.decode(\'utf-8\', errors=\'ignore\'):
                    print(f"Please ensure the model file 	hemed_text_is_not_recognized_by_the_user_facing_tool} and its .json config are correctly placed or downloadable by Piper.")
                return False
            
            print(f"TTSModule: Speech successfully synthesized to {output_file_path}")
            return True
        except FileNotFoundError:
            print("Error: Piper executable not found. Please install Piper and add it to PATH.")
            return False
        except Exception as e:
            print(f"An unexpected error occurred during TTS: {e}")
            return False

    def speak_to_raw_audio(self, text: str) -> bytes | None:
        """
        Synthesizes speech from text and returns raw audio data.

        Args:
            text: The text to synthesize.

        Returns:
            Raw audio data as bytes, or None if synthesis failed.
            The audio is typically 16-bit mono PCM at the voice's sample rate.
        """
        if not self.model_path:
            print("TTS Error: Model path not set.")
            return None

        command = [
            "piper",
            "--model", self.model_path,
            "--output-raw" # Output raw audio to stdout
        ]

        try:
            print(f"TTSModule: Synthesizing 	hemed_text_is_not_recognized_by_the_user_facing_tool} to raw audio using model {self.model_path}")
            process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            raw_audio, stderr = process.communicate(input=text.encode("utf-8"))

            if process.returncode != 0:
                print(f"Error during Piper TTS raw synthesis: {stderr.decode(\'utf-8\', errors=\'ignore\')}")
                return None
            
            print(f"TTSModule: Speech successfully synthesized to raw audio data (length: {len(raw_audio)} bytes).")
            return raw_audio
        except FileNotFoundError:
            print("Error: Piper executable not found. Please install Piper and add it to PATH.")
            return None
        except Exception as e:
            print(f"An unexpected error occurred during TTS raw audio synthesis: {e}")
            return None

if __name__ == '__main__':
    print("Testing TTSModule...")
    # This test requires Piper to be installed and models downloaded/configured.
    # Ensure piper executable is in PATH.
    # Ensure model paths in config.py are correct (e.g., pointing to downloaded .onnx and .onnx.json files)
    # or are model names piper can auto-download (e.g., "en_US-lessac-medium")

    # Create a dummy output directory if it doesn't exist
    if not os.path.exists("test_audio_output"):
        os.makedirs("test_audio_output")

    try:
        tts_en = TTSModule(language="en")
        if tts_en.model_path: # Check if model path was resolved
            print("\n--- English TTS Test ---")
            english_text = "Hello, this is a test of the Piper text to speech system in English."
            output_path_en = "test_audio_output/test_en.wav"
            if tts_en.speak(english_text, output_path_en):
                print(f"English speech saved to {output_path_en}")
                # You can try playing this file with an audio player
            else:
                print("English TTS failed.")
            
            # Test raw audio output
            # raw_audio_en = tts_en.speak_to_raw_audio(english_text)
            # if raw_audio_en:
            #     print(f"Received {len(raw_audio_en)} bytes of raw English audio.")
            #     # To play this, you'd need to know the sample rate, channels, and bit depth from the model's config
            #     # e.g., using PyAudio. For now, just confirm it runs.
            # else:
            #     print("English TTS to raw audio failed.")
        else:
            print("Skipping English TTS test as model path is not configured.")

        tts_zh = TTSModule(language="zh")
        if tts_zh.model_path:
            print("\n--- Chinese TTS Test ---")
            chinese_text = "你好，这是一个中文派珀文本转语音系统的测试。"
            output_path_zh = "test_audio_output/test_zh.wav"
            if tts_zh.speak(chinese_text, output_path_zh):
                print(f"Chinese speech saved to {output_path_zh}")
            else:
                print("Chinese TTS failed.")
        else:
            print("Skipping Chinese TTS test as model path is not configured.")

    except EnvironmentError as e:
        print(f"TTS Module test failed due to environment error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during TTS module test: {e}")

    print("\nTTSModule test finished.")

