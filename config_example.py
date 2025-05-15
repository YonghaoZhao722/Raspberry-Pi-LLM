import os

# Gemini API Configuration
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")  # 设置您的Gemini API密钥
GEMINI_MODEL_NAME = os.environ.get("GEMINI_MODEL_NAME", "gemini-2.0-flash")  # 可选模型: gemini-2.0-flash, gemini-1.0-pro等

# Audio Configuration
AUDIO_INPUT_DEVICE_INDEX = None  # 使用默认麦克风，或指定设备索引，例如1
AUDIO_SAMPLE_RATE = 16000
AUDIO_CHANNELS = 1
AUDIO_CHUNK_SIZE = 1024

# STT (Vosk) Configuration
VOSK_MODEL_PATH_EN = "models/vosk/vosk-model-small-en-us-0.15"  # 英文语音识别模型路径
VOSK_MODEL_PATH_ZH = "models/vosk/vosk-model-small-cn-0.22"     # 中文语音识别模型路径
# 这些路径应指向已下载的Vosk模型位置，请参考README中的下载说明

# TTS (Piper) Configuration
PIPER_MODEL_PATH_EN = "models/piper/en_US-lessac-medium.onnx"      # 英文语音合成模型路径
PIPER_CONFIG_PATH_EN = "models/piper/en_US-lessac-medium.onnx.json"
PIPER_MODEL_PATH_ZH = "models/piper/zh_CN-huayan-medium.onnx"      # 中文语音合成模型路径
PIPER_CONFIG_PATH_ZH = "models/piper/zh_CN-huayan-medium.onnx.json"
# 这些路径应指向已下载的Piper模型位置，请参考README中的下载说明

# Vision (MediaPipe) Configuration
# MediaPipe模型通常由库内部处理，无需额外配置

# Logging Configuration
LOG_LEVEL = "INFO"  # 可选: DEBUG, INFO, WARNING, ERROR, CRITICAL

# Supported Languages
SUPPORTED_LANGUAGES = ["en", "zh"]  # 支持英文和中文
DEFAULT_LANGUAGE = "en"  # 默认语言：英文 