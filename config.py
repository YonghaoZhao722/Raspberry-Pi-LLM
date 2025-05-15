import os

# Gemini API Configuration
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyDCH9kq_ZOYbiRF4aWf-Y-vcYO1_OqEK7E") # Default to user provided key
GEMINI_MODEL_NAME = os.environ.get("GEMINI_MODEL_NAME", "gemini-2.0-flash") # Default to user provided model

# Audio Configuration
AUDIO_INPUT_DEVICE_INDEX = None  # Or specify a device index, e.g., 1
AUDIO_SAMPLE_RATE = 16000
AUDIO_CHANNELS = 1
AUDIO_CHUNK_SIZE = 1024

# STT (Vosk) Configuration
VOSK_MODEL_PATH_EN = "vosk-model-small-en-us-0.15"  # Example model, will need to be downloaded
VOSK_MODEL_PATH_ZH = "vosk-model-small-cn-0.22"    # Example model, will need to be downloaded
# Ensure these paths are correct or provide absolute paths after downloading the models.
# We will add instructions to download these later.

# TTS (Piper) Configuration
PIPER_MODEL_PATH_EN = "en_US-lessac-medium.onnx" # Example model, will need to be downloaded
PIPER_CONFIG_PATH_EN = "en_US-lessac-medium.onnx.json"
PIPER_MODEL_PATH_ZH = "zh_CN-huayan-medium.onnx" # Example, if available, or use a suitable Chinese voice
PIPER_CONFIG_PATH_ZH = "zh_CN-huayan-medium.onnx.json"
# Ensure these paths are correct or provide absolute paths after downloading the models.
# We will add instructions to download these later.

# Vision (MediaPipe) Configuration
# MediaPipe models are usually handled internally by the library, but specific model paths can be added if needed.

# Logging Configuration
LOG_LEVEL = "INFO"

# Supported Languages
SUPPORTED_LANGUAGES = ["en", "zh"] # English and Chinese
DEFAULT_LANGUAGE = "en"

