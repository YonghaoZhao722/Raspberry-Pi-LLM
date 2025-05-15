# 树莓派多模态视觉语音交互助手

这是一个基于树莓派的多模态视觉语音交互助手项目，能够通过麦克风接收用户语音指令，结合摄像头捕获的视觉信息，调用大语言模型进行处理，并通过语音输出回应用户。该项目旨在创建一个能够部署在带有摄像头、音响和麦克风的 Linux 设备（尤其是树莓派）上的智能交互助手/机器人。

## 功能特点

- **多模态交互**：同时支持语音和视觉输入，提供更自然的人机交互体验
- **离线语音处理**：使用 Vosk 进行本地语音识别，Piper 进行本地语音合成
- **视觉识别**：通过 MediaPipe 实现物体识别和场景分析
- **大语言模型集成**：使用 Google Gemini API 提供智能对话能力
- **多语言支持**：支持中文和英文的语音识别和合成
- **树莓派优化**：针对树莓派等资源受限设备进行了性能优化

## 系统架构

![系统架构](https://raw.githubusercontent.com/YonghaoZhao722/Raspberry-Pi-LLM/main/docs/images/system_architecture.png)

系统由以下核心模块组成：

1. **音频输入模块**：通过麦克风捕获用户语音
2. **语音转文本 (STT) 模块**：使用 Vosk 将语音转换为文本
3. **视频输入模块**：通过摄像头捕获环境视觉信息
4. **视觉处理模块**：使用 MediaPipe 进行物体识别和场景分析
5. **核心逻辑与编排模块**：协调各模块工作，管理对话状态
6. **大语言模型 (LLM) 模块**：通过 Gemini API 处理用户请求并生成回复
7. **文本转语音 (TTS) 模块**：使用 Piper 将文本转换为语音
8. **音频输出模块**：通过扬声器播放合成的语音

## 技术栈

- **大语言模型**：Google Gemini API (gemini-2.0-flash)
- **语音转文本**：Vosk (支持离线中英文识别)
- **文本转语音**：Piper (支持离线中英文合成，针对树莓派优化)
- **视觉识别**：MediaPipe (用于物体识别等)
- **编程语言**：Python

## 硬件要求

- 树莓派 4B 或更高版本（推荐至少 4GB RAM）
- USB 麦克风或兼容的音频输入设备
- USB 摄像头或树莓派官方摄像头模块
- 扬声器或耳机（通过 3.5mm 音频接口或 USB）
- 稳定的网络连接（用于 Gemini API 调用）

## 快速开始

### 1. 安装系统依赖

```bash
sudo apt-get update
sudo apt-get install -y build-essential portaudio19-dev python3-dev python3-pip ffmpeg libsm6 libxext6
```

### 2. 克隆仓库

```bash
git clone https://github.com/YonghaoZhao722/Raspberry-Pi-LLM.git
cd Raspberry-Pi-LLM
```

### 3. 创建虚拟环境并安装依赖

```bash
python3 -m venv venv
source venv/bin/activate
pip3 install -r multimodal_assistant/requirements.txt
```

### 4. 配置 API 密钥和模型

编辑 `multimodal_assistant/config.py` 文件，设置您的 Gemini API 密钥和模型路径：

```python
# Gemini API Configuration
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
GEMINI_MODEL_NAME = "gemini-2.0-flash"

# 设置 Vosk 和 Piper 模型路径
VOSK_MODEL_PATH_EN = "/path/to/vosk-model-small-en-us-0.15"
VOSK_MODEL_PATH_ZH = "/path/to/vosk-model-small-cn-0.22"
PIPER_MODEL_PATH_EN = "/path/to/en_US-lessac-medium.onnx"
PIPER_CONFIG_PATH_EN = "/path/to/en_US-lessac-medium.onnx.json"
PIPER_MODEL_PATH_ZH = "/path/to/zh_CN-huayan-medium.onnx"
PIPER_CONFIG_PATH_ZH = "/path/to/zh_CN-huayan-medium.onnx.json"
```

### 5. 下载必要的模型

- Vosk 模型：从 [Vosk Models](https://alphacephei.com/vosk/models) 下载
- Piper 模型：从 [Piper Samples](https://rhasspy.github.io/piper-samples/) 下载

### 6. 运行助手

```bash
python3 -m multimodal_assistant.main
```

## 使用方法

- **开始交互**：运行程序后，助手会用默认语言问候您并开始监听
- **语音指令**：直接对麦克风说话，系统会自动检测语音结束并处理
- **切换语言**：说 "switch to chinese" 或 "切换到中文" 来切换语言
- **视觉相关指令**：说 "what do you see" 或 "这是什么" 等触发视觉分析
- **退出程序**：说 "exit"、"quit"、"再见" 或按 Ctrl+C

## 项目结构

```
multimodal_assistant/
├── main.py              # 主程序入口
├── config.py            # 配置文件
├── requirements.txt     # 依赖列表
├── audio_input.py       # 音频输入模块
├── stt_module.py        # 语音转文本模块
├── video_input.py       # 视频输入模块
├── vision_module.py     # 视觉处理模块
├── llm_module.py        # 大语言模型交互模块
├── tts_module.py        # 文本转语音模块
└── audio_output.py      # 音频输出模块
```

## 故障排除

常见问题及解决方案请参考 [部署指南](docs/multimodal_assistant_deployment_guide.md)。

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎提交 Issues 和 Pull Requests 来帮助改进这个项目。

## 致谢

- [Vosk](https://alphacephei.com/vosk/) - 提供离线语音识别能力
- [Piper](https://github.com/rhasspy/piper) - 提供高质量的离线语音合成
- [MediaPipe](https://mediapipe.dev/) - 提供视觉识别能力
- [Google Gemini](https://ai.google.dev/) - 提供大语言模型能力
