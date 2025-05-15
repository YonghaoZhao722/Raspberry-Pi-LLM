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

详细的系统架构和交互流程请参阅 [系统架构与交互流程设计](docs/system_architecture_and_interaction_flow.md)。

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
source venv/bin/activate  # Linux/Mac
# 或 .\venv\Scripts\activate  # Windows
pip3 install -r requirements.txt
```

### 4. 下载并配置必要的模型

#### 创建模型目录

```bash
mkdir -p models/vosk models/piper
```

#### 下载 Vosk 模型

```bash
# 下载英文模型
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip -d models/vosk/
mv models/vosk/vosk-model-small-en-us-0.15 models/vosk/vosk-model-small-en-us-0.15

# 下载中文模型
wget https://alphacephei.com/vosk/models/vosk-model-small-cn-0.22.zip
unzip vosk-model-small-cn-0.22.zip -d models/vosk/
mv models/vosk/vosk-model-small-cn-0.22 models/vosk/vosk-model-small-cn-0.22
```

#### 下载 Piper 模型

```bash
# 下载英文模型
wget https://github.com/rhasspy/piper/releases/download/v1.2.0/voice-en_US-lessac-medium.tar.gz
mkdir -p models/piper/en_US-lessac-medium
tar -xvzf voice-en_US-lessac-medium.tar.gz -C models/piper/en_US-lessac-medium
cp models/piper/en_US-lessac-medium/en_US-lessac-medium.onnx models/piper/
cp models/piper/en_US-lessac-medium/en_US-lessac-medium.onnx.json models/piper/

# 下载中文模型
wget https://github.com/rhasspy/piper/releases/download/v1.2.0/voice-zh_CN-huayan-medium.tar.gz
mkdir -p models/piper/zh_CN-huayan-medium
tar -xvzf voice-zh_CN-huayan-medium.tar.gz -C models/piper/zh_CN-huayan-medium
cp models/piper/zh_CN-huayan-medium/zh_CN-huayan-medium.onnx models/piper/
cp models/piper/zh_CN-huayan-medium/zh_CN-huayan-medium.onnx.json models/piper/
```

### 5. 配置 API 密钥

从 `src/config_example.py` 创建您的 `src/config.py` 文件：

```bash
cp src/config_example.py src/config.py
```

然后编辑 `src/config.py` 文件，设置您的 Gemini API 密钥：

```python
# 将此行替换为您的实际API密钥
GEMINI_API_KEY = "YOUR_ACTUAL_GEMINI_API_KEY"
```

您可以从 [Google AI Studio](https://ai.google.dev/) 获取 Gemini API 密钥。

### 6. 运行助手

```bash
python3 start.py
```

## 使用方法

- **开始交互**：运行程序后，助手会用默认语言问候您并开始监听
- **语音指令**：直接对麦克风说话，系统会自动检测语音结束并处理
- **切换语言**：说 "switch to chinese" 或 "切换到中文" 来切换语言
- **视觉相关指令**：说 "what do you see" 或 "这是什么" 等触发视觉分析
- **退出程序**：说 "exit"、"quit"、"再见" 或按 Ctrl+C

## 项目结构

```
├── start.py                  # 主入口点启动脚本
├── requirements.txt          # 依赖列表
├── models/                   # 模型目录
│   ├── vosk/                 # Vosk 语音识别模型目录
│   └── piper/                # Piper 语音合成模型目录
├── src/                      # 源代码目录
│   ├── __init__.py           # 包初始化文件
│   ├── main.py               # 主程序入口
│   ├── config_example.py     # 配置文件示例
│   ├── audio_input.py        # 音频输入模块
│   ├── audio_output.py       # 音频输出模块
│   ├── stt_module.py         # 语音转文本模块
│   ├── tts_module.py         # 文本转语音模块
│   ├── video_input.py        # 视频输入模块
│   ├── vision_module.py      # 视觉处理模块
│   └── llm_module.py         # 大语言模型交互模块
└── docs/                     # 文档目录
    ├── system_architecture_and_interaction_flow.md  # 系统架构文档
    ├── multimodal_assistant_deployment_guide.md     # 部署指南
    ├── tech_selection_summary.md                    # 技术选型总结
    └── todo.md                                      # 待办事项
```

## 故障排除

### 常见问题

1. **语音识别不工作**
   - 检查麦克风是否正确连接和配置
   - 验证 Vosk 模型是否已正确下载并设置正确路径

2. **语音合成不工作**
   - 检查扬声器是否正确连接和配置
   - 验证 Piper 模型是否已正确下载并设置正确路径

3. **视觉识别不工作**
   - 检查摄像头是否正确连接和配置
   - 尝试重新启动程序

4. **API 调用失败**
   - 检查网络连接
   - 验证 Gemini API 密钥是否正确

### 日志检查

如需更详细的调试信息，可以在 `src/config.py` 中将 `LOG_LEVEL` 设置为 "DEBUG"。

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎提交 Issues 和 Pull Requests 来帮助改进这个项目。

## 致谢

- [Vosk](https://alphacephei.com/vosk/) - 提供离线语音识别能力
- [Piper](https://github.com/rhasspy/piper) - 提供高质量的离线语音合成
- [MediaPipe](https://mediapipe.dev/) - 提供视觉识别能力
- [Google Gemini](https://ai.google.dev/) - 提供大语言模型能力
