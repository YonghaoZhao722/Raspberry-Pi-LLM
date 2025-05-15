# 多模态视觉语音交互助手部署与使用指南

## 1. 项目概述

本项目旨在创建一个基于 Ubuntu (或其他 Linux 发行版，如树莓派 OS) 的多模态视觉语音交互助手。它能够通过麦克风接收用户语音，利用 STT (语音转文本) 将其转换为文本；结合摄像头捕捉的视觉信息 (通过视觉识别模块处理)，将文本和视觉上下文发送给大语言模型 (LLM)；然后接收 LLM 的文本回复，并通过 TTS (文本转语音) 将其合成为语音，通过扬声器播放给用户。

核心技术栈：
*   **大语言模型 (LLM)**: Google Gemini API (gemini-2.0-flash)
*   **语音转文本 (STT)**: Vosk (支持离线中英文识别)
*   **文本转语音 (TTS)**: Piper (支持离线中英文合成，针对树莓派优化)
*   **视觉识别**: MediaPipe (用于物体识别等)
*   **编程语言**: Python

## 2. 硬件要求

*   一台 Linux 设备 (例如：运行树莓派 OS 的 Raspberry Pi 4 或更高版本，或装有 Ubuntu 的 PC/笔记本电脑)。
*   麦克风 (USB 麦克风或内置麦克风)。
*   扬声器或耳机。
*   摄像头 (USB 摄像头或内置摄像头)。
*   稳定的网络连接 (用于首次下载模型和访问 Gemini API)。

## 3. 环境搭建与依赖安装

### 3.1. 系统依赖 (以 Debian/Ubuntu/Raspberry Pi OS 为例)

打开终端，执行以下命令安装必要的系统库：

```bash
sudo apt-get update
sudo apt-get install -y build-essential portaudio19-dev python3-dev python3-pip ffmpeg libsm6 libxext6
# build-essential: 提供 gcc 等编译工具，解决 pyaudio 等库的编译问题。
# portaudio19-dev: PyAudio 的核心依赖。
# python3-dev: Python C 扩展编译所需。
# python3-pip: Python 包管理器。
# ffmpeg libsm6 libxext6: OpenCV 可能需要的库。
```

### 3.2. Python 环境与项目文件

1.  **获取项目文件**：
    您应该已经收到了项目的所有代码文件。将它们解压或放置到一个合适的目录，例如 `/home/your_user/multimodal_assistant`。

2.  **创建 Python 虚拟环境 (推荐)**：
    在项目根目录下 (例如 `/home/your_user/multimodal_assistant`) 打开终端：
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
    后续所有 Python 相关命令都应在此激活的虚拟环境中执行。

3.  **安装 Python 依赖**：
    项目根目录下有一个 `requirements.txt` 文件。执行以下命令安装：
    ```bash
    pip3 install -r requirements.txt
    ```
    如果 `pyaudio` 仍然安装失败，请确保 `portaudio19-dev` 和 `python3-dev` 已正确安装。

### 3.3. API 密钥配置

1.  **Gemini API 密钥**：
    *   您需要一个有效的 Google Gemini API 密钥。
    *   打开项目中的 `multimodal_assistant/config.py` 文件。
    *   找到 `GEMINI_API_KEY` 变量，将其值替换为您的实际 API 密钥字符串。例如：
        ```python
        GEMINI_API_KEY = "YOUR_ACTUAL_GEMINI_API_KEY"
        ```
    *   确保 `GEMINI_MODEL_NAME` 设置为 `"gemini-2.0-flash"` 或您希望使用的兼容模型。

### 3.4. 模型下载与配置

您需要为 STT (Vosk) 和 TTS (Piper) 下载预训练模型。

1.  **Vosk STT 模型 (离线)**：
    *   访问 [Vosk Model Page](https://alphacephei.com/vosk/models)。
    *   下载适用于**英文**的小型模型 (例如 `vosk-model-small-en-us-0.15`)。
    *   下载适用于**中文**的小型模型 (例如 `vosk-model-small-cn-0.22` 或更新版本)。
    *   解压下载的模型包。每个模型包解压后会得到一个文件夹 (例如 `vosk-model-small-en-us-0.15`)。
    *   将这些模型文件夹放置到您的项目可以访问的位置。例如，您可以将它们放在 `multimodal_assistant` 目录下，或者一个统一的 `models` 目录下。
    *   打开 `multimodal_assistant/config.py` 文件，修改 `VOSK_MODEL_PATH_EN` 和 `VOSK_MODEL_PATH_ZH` 指向您解压后的模型文件夹的**完整路径**。例如：
        ```python
        VOSK_MODEL_PATH_EN = "/home/your_user/multimodal_assistant/vosk-model-small-en-us-0.15"
        VOSK_MODEL_PATH_ZH = "/home/your_user/multimodal_assistant/vosk-model-small-cn-0.22"
        ```

2.  **Piper TTS 模型 (离线)**：
    *   访问 [Piper Samples Page](https://rhasspy.github.io/piper-samples/) (或其 GitHub 仓库的模型链接)。
    *   找到并下载适用于**英文**的语音模型。您需要 `.onnx` 模型文件和对应的 `.onnx.json` 配置文件。例如，`en_US-lessac-medium.onnx` 和 `en_US-lessac-medium.onnx.json`。
    *   找到并下载适用于**中文**的语音模型。例如，`zh_CN-huayan-medium.onnx` 和 `zh_CN-huayan-medium.onnx.json` (如果可用，或者选择其他合适的中文语音)。
    *   将这些 `.onnx` 和 `.onnx.json` 文件放置到您的项目可以访问的位置。
    *   打开 `multimodal_assistant/config.py` 文件，修改 `PIPER_MODEL_PATH_EN`, `PIPER_CONFIG_PATH_EN`, `PIPER_MODEL_PATH_ZH`, `PIPER_CONFIG_PATH_ZH` 指向这些文件的**完整路径**。例如:
        ```python
        PIPER_MODEL_PATH_EN = "/home/your_user/multimodal_assistant/models_piper/en_US-lessac-medium.onnx"
        PIPER_CONFIG_PATH_EN = "/home/your_user/multimodal_assistant/models_piper/en_US-lessac-medium.onnx.json"
        PIPER_MODEL_PATH_ZH = "/home/your_user/multimodal_assistant/models_piper/zh_CN-huayan-medium.onnx"
        PIPER_CONFIG_PATH_ZH = "/home/your_user/multimodal_assistant/models_piper/zh_CN-huayan-medium.onnx.json"
        ```
        **注意**: Piper 也可以通过模型名称自动下载模型，如果 `config.py` 中的路径设置为模型名称而不是文件路径，且 Piper 配置正确，它可能会尝试下载。但为确保可靠性，建议手动下载并配置完整路径。

## 4. 运行项目

1.  确保所有硬件 (麦克风、摄像头、扬声器) 已连接并被系统识别。
2.  确保您的网络连接正常 (Gemini API 需要)。
3.  打开终端，导航到项目根目录 (例如 `/home/your_user/multimodal_assistant`)。
4.  如果使用了虚拟环境，请激活它：`source venv/bin/activate`。
5.  运行主程序：
    ```bash
    python3 -m multimodal_assistant.main
    ```
    或者，如果直接在 `multimodal_assistant` 目录内：
    ```bash
    python3 main.py
    ```

6.  程序启动后，会进行模块初始化和模型检查。留意终端输出的任何错误或警告信息。
7.  如果一切顺利，助手会用默认语言向您问好，并开始监听您的语音指令。

## 5. 使用说明

*   **语音交互**：直接对麦克风说话。系统会检测您的语音结束，然后处理您的指令。
*   **切换语言**：
    *   说出 "switch to chinese" 或 "切换到中文" 来切换到中文模式。
    *   说出 "switch to english" 或 "切换到英文" 来切换到英文模式。
*   **视觉交互**：
    *   当您问及视觉相关的问题时，例如 "what do you see?", "describe the scene", "这是什么?"，系统会尝试捕捉摄像头画面并进行分析，将分析结果融入给 LLM 的提示中。
*   **退出程序**：
    *   说出 "exit", "quit", "stop listening", "再见" 或 "退出"。
    *   也可以在终端按 `Ctrl+C` 来中断程序。

## 6. 故障排除

*   **麦克风/摄像头不工作**：
    *   检查硬件连接。
    *   确保您的 Linux 系统已正确识别并配置了麦克风和摄像头。可以使用系统工具 (如 `arecord -l` 查看录音设备, `cheese` 或 `guvcview` 测试摄像头) 进行检查。
    *   在 `config.py` 中，`AUDIO_INPUT_DEVICE_INDEX` 和 `video_input.py` 中的 `camera_index` 可能需要根据您的设备进行调整。脚本中的测试代码会尝试列出可用设备，您可以参考其输出来修改配置。
*   **模型加载失败**：
    *   仔细检查 `config.py` 中配置的模型路径是否正确，并且指向了实际下载和解压的模型文件/文件夹。
    *   确保模型文件没有损坏。
*   **`pyaudio` 安装或运行时错误**：
    *   确保 `portaudio19-dev` (或类似包) 和 `python3-dev` 已安装。
    *   尝试重新安装 `pyaudio`: `pip3 uninstall pyaudio` 然后 `pip3 install pyaudio --no-cache-dir`。
*   **Piper 执行错误**：
    *   确保 `piper` 可执行文件已安装并且在系统的 `PATH` 环境变量中，或者 `tts_module.py` 中能找到它。您可以从 Piper 的 GitHub Releases 页面下载预编译的二进制文件。
*   **Gemini API 错误**：
    *   检查 API 密钥是否正确配置在 `config.py` 中。
    *   确保网络连接正常。
    *   检查您的 Gemini API 配额和权限。
*   **性能问题 (尤其在树莓派上)**：
    *   视觉处理和 LLM API 调用可能比较耗时。`config.py` 和 `video_input.py` 中的 `fps_limit` 可以适当调低以减少 CPU 占用。
    *   确保树莓派有足够的散热。

## 7. 代码结构

*   `main.py`: 主程序，集成所有模块并处理交互逻辑。
*   `config.py`: 配置文件，包含 API 密钥、模型路径、音频参数等。
*   `requirements.txt`: Python 依赖列表。
*   `audio_input.py`: 处理麦克风音频输入。
*   `stt_module.py`: 语音转文本模块 (Vosk)。
*   `llm_module.py`: 大语言模型交互模块 (Gemini)。
*   `tts_module.py`: 文本转语音模块 (Piper)。
*   `audio_output.py`: 处理扬声器音频输出。
*   `video_input.py`: 处理摄像头视频输入。
*   `vision_module.py`: 视觉处理模块 (MediaPipe)。

## 8. 未来扩展

*   更精细的唤醒词检测。
*   支持更多语言。
*   更复杂的视觉理解能力。
*   本地化 LLM 部署 (如果硬件允许)。
*   图形用户界面 (GUI)。

希望这份指南能帮助您成功部署和使用这个多模态交互助手！
