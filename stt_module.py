import vosk
import json
import os
from . import config
from .audio_input import AudioInput # Assuming audio_input.py is in the same directory

class STTModule:
    def __init__(self, language=config.DEFAULT_LANGUAGE):
        self.language = language
        self.model_path = self._get_model_path()
        self.model = None
        self.recognizer = None
        self._load_model()

    def _get_model_path(self):
        if self.language == "en":
            return config.VOSK_MODEL_PATH_EN
        elif self.language == "zh":
            return config.VOSK_MODEL_PATH_ZH
        else:
            print(f"Warning: Language 	hemed_text_is_not_recognized_by_the_user_facing_tool} not supported by STT, defaulting to English.")
            self.language = "en"
            return config.VOSK_MODEL_PATH_EN

    def _load_model(self):
        if not os.path.exists(self.model_path):
            print(f"Error: Vosk model path not found: {self.model_path}")
            print("Please download the Vosk models and place them in the correct directory or update config.py.")
            print(f"For {self.language}, expected at: {self.model_path}")
            # Instructions to download models (example for English small model)
            # For English: vosk-model-small-en-us-0.15
            # For Chinese: vosk-model-small-cn-0.22 (or other appropriate Chinese model)
            # Download from: https://alphacephei.com/vosk/models
            # And extract to a directory, then update VOSK_MODEL_PATH_EN/ZH in config.py
            return
        try:
            self.model = vosk.Model(self.model_path)
            # The recognizer is created per audio stream or when sample rate is known.
            # We will create it when recognize_stream is called, or use a default sample rate.
            print(f"STTModule: Vosk model for {self.language} loaded successfully from {self.model_path}.")
        except Exception as e:
            print(f"Error loading Vosk model for {self.language} from {self.model_path}: {e}")
            self.model = None

    def set_language(self, language_code):
        if language_code not in config.SUPPORTED_LANGUAGES:
            print(f"Warning: Language {language_code} not in supported list: {config.SUPPORTED_LANGUAGES}. Using default.")
            language_code = config.DEFAULT_LANGUAGE
        
        if self.language != language_code:
            print(f"STTModule: Changing language from {self.language} to {language_code}")
            self.language = language_code
            self.model_path = self._get_model_path()
            self._load_model() # Reload model for the new language
            self.recognizer = None # Recognizer needs to be recreated

    def recognize_chunk(self, audio_chunk, sample_rate=config.AUDIO_SAMPLE_RATE) -> tuple[str, bool]:
        """
        Recognizes speech from a single audio chunk.

        Args:
            audio_chunk: Bytes, the audio data chunk.
            sample_rate: The sample rate of the audio chunk.

        Returns:
            A tuple (text, is_final) where text is the recognized text (partial or final)
            and is_final is a boolean indicating if this is the final result for the utterance.
        """
        if not self.model:
            # print("STT Error: Vosk model not loaded.")
            return "", False

        if not self.recognizer or self.recognizer.AcceptWaveform(b"") == -1: # Check if recognizer needs reinitialization
            # Create recognizer if not exists or if sample rate changed (though sample rate is fixed here)
            self.recognizer = vosk.KaldiRecognizer(self.model, sample_rate)
            # For partial results: self.recognizer.SetWords(True)

        if self.recognizer.AcceptWaveform(audio_chunk):
            result = json.loads(self.recognizer.Result())
            return result.get("text", ""), True
        else:
            partial_result = json.loads(self.recognizer.PartialResult())
            return partial_result.get("partial", ""), False

    def get_final_recognition(self) -> str:
        """Call this after the last chunk to get the final result."""
        if not self.recognizer:
            return ""
        result = json.loads(self.recognizer.FinalResult())
        self.recognizer = None # Reset recognizer for next utterance
        return result.get("text", "")

    def recognize_audio_file(self, file_path, sample_rate=config.AUDIO_SAMPLE_RATE) -> str:
        if not self.model:
            print("STT Error: Vosk model not loaded.")
            return ""
        if not os.path.exists(file_path):
            print(f"STT Error: Audio file not found: {file_path}")
            return ""
        
        recognizer = vosk.KaldiRecognizer(self.model, sample_rate)
        # recognizer.SetWords(True) # If you want word timestamps

        try:
            with open(file_path, "rb") as wf:
                while True:
                    data = wf.read(config.AUDIO_CHUNK_SIZE) # Read in chunks
                    if len(data) == 0:
                        break
                    if recognizer.AcceptWaveform(data):
                        pass # Processed full utterance segment
                        # print(json.loads(recognizer.Result())["text"])
                    else:
                        pass # Processing partial result
                        # print(json.loads(recognizer.PartialResult())["partial"])
                
                final_result = json.loads(recognizer.FinalResult())
                return final_result.get("text", "")
        except Exception as e:
            print(f"Error during file recognition: {e}")
            return ""

if __name__ == '__main__':
    print("Testing STTModule...")
    # This test requires Vosk models to be downloaded and paths configured in config.py
    # It also requires a microphone for live testing.

    # First, ensure models are present (this is a placeholder check, manual download is needed)
    if not (os.path.exists(config.VOSK_MODEL_PATH_EN) and os.path.exists(config.VOSK_MODEL_PATH_ZH)):
        print("Vosk models not found. Please download them from https://alphacephei.com/vosk/models")
        print(f"Expected English model at: {config.VOSK_MODEL_PATH_EN}")
        print(f"Expected Chinese model at: {config.VOSK_MODEL_PATH_ZH}")
        print("Skipping STT module test.")
    else:
        stt_en = STTModule(language="en")
        stt_zh = STTModule(language="zh")

        if stt_en.model:
            print("\n--- English STT Test (Live Audio) ---")
            audio_input_en = AudioInput(sample_rate=config.AUDIO_SAMPLE_RATE)
            audio_input_en.start_listening()
            if audio_input_en.running:
                print("Speak in English for 5 seconds...")
                full_transcript_en = ""
                for _ in range(int(5 * config.AUDIO_SAMPLE_RATE / config.AUDIO_CHUNK_SIZE)):
                    chunk = audio_input_en.get_audio_chunk(timeout=0.2)
                    if chunk:
                        text, is_final = stt_en.recognize_chunk(chunk)
                        if text:
                            print(f"Partial/Final EN: {text}", end=\'\r\', flush=True)
                        if is_final and text:
                            full_transcript_en += text + " "
                            print(f"Final Segment EN: {text}") # Newline after final segment
                final_text_en = stt_en.get_final_recognition()
                if final_text_en:
                     full_transcript_en += final_text_en
                print(f"\nFull English Transcript (Live): {full_transcript_en.strip()}")
                audio_input_en.stop_listening()
            else:
                print("Failed to start audio input for English STT test.")
        else:
            print("English STT model not loaded. Skipping English live test.")

        # Chinese STT Test (Conceptual - requires Chinese model and mic input)
        if stt_zh.model:
            print("\n--- Chinese STT Test (Live Audio) ---")
            audio_input_zh = AudioInput(sample_rate=config.AUDIO_SAMPLE_RATE)
            audio_input_zh.start_listening()
            if audio_input_zh.running:
                print("请用中文说几句话 (Speak in Chinese for 5 seconds)...")
                full_transcript_zh = ""
                for _ in range(int(5 * config.AUDIO_SAMPLE_RATE / config.AUDIO_CHUNK_SIZE)):
                    chunk = audio_input_zh.get_audio_chunk(timeout=0.2)
                    if chunk:
                        text, is_final = stt_zh.recognize_chunk(chunk)
                        if text:
                            print(f"Partial/Final ZH: {text}", end=\'\r\', flush=True)
                        if is_final and text:
                            full_transcript_zh += text + " " # Add space for sentence separation
                            print(f"Final Segment ZH: {text}")
                final_text_zh = stt_zh.get_final_recognition()
                if final_text_zh:
                    full_transcript_zh += final_text_zh
                print(f"\nFull Chinese Transcript (Live): {full_transcript_zh.strip()}")
                audio_input_zh.stop_listening()
            else:
                print("Failed to start audio input for Chinese STT test.")
        else:
            print("Chinese STT model not loaded. Skipping Chinese live test.")

    print("\nSTTModule test finished.")

