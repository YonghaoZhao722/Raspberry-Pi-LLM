# 系统架构与交互流程设计

## 1. 系统架构

本系统旨在构建一个基于树莓派的多模态视觉语音交互助手，其核心架构包含以下模块：

*   **输入模块**：
    *   **音频输入**：通过麦克风实时捕获用户语音。
    *   **视频输入**：通过摄像头实时捕获环境视觉信息。

*   **语音转文本 (STT) 模块 - Vosk**：
    *   接收原始音频流。
    *   将用户语音实时转换为文本格式（支持中文和英文）。
    *   输出转录文本给核心逻辑模块。

*   **视觉处理模块 - MediaPipe**：
    *   接收原始视频流。
    *   根据核心逻辑模块的指令，执行相应的视觉任务，例如：
        *   **实时物体识别**：持续检测和识别视野中的常见物体。
        *   **指令驱动的图像分析**：当用户发出与视觉相关的指令时（例如“这是什么？”），对当前帧或特定区域进行详细分析。
    *   输出结构化的视觉信息（如物体标签、位置、描述性特征）给核心逻辑模块。

*   **核心逻辑与编排模块 (Python)**：
    *   作为系统的中枢，协调各个模块的工作。
    *   接收来自 STT 模块的文本输入和来自视觉处理模块的视觉信息。
    *   **意图识别与上下文融合**：分析用户输入的文本，结合当前的视觉上下文（如果相关），判断用户意图。
    *   **多模态提示构建**：根据用户意图，将文本信息和必要的视觉信息整合成一个结构化的提示 (prompt) 发送给大语言模型。
    *   **API 交互管理**：负责与 Gemini API 的通信，发送请求并接收响应。
    *   **响应处理**：接收大语言模型的文本响应，并将其传递给 TTS 模块。
    *   **状态管理**：维护对话状态和必要的上下文信息。

*   **大语言模型 (LLM) 模块 - Google Gemini API**：
    *   接收来自核心逻辑模块的（可能包含视觉信息的）文本提示。
    *   理解用户意图，结合提供的上下文（包括视觉描述），生成自然语言回复。
    *   返回文本格式的响应给核心逻辑模块。

*   **文本转语音 (TTS) 模块 - Piper**：
    *   接收来自核心逻辑模块的文本响应。
    *   将文本实时转换为自然流畅的语音（支持中文和英文，音色可选）。
    *   输出音频流给音频输出模块。

*   **输出模块**：
    *   **音频输出**：通过扬声器播放由 TTS 模块生成的语音。

## 2. 交互流程

以下描述了用户与系统进行一次典型交互的流程：

1.  **用户发起交互**：用户通过语音向设备发出指令或提问（例如：“帮我看看桌子上有什么？”或“今天天气怎么样？”）。

2.  **数据采集**：
    *   麦克风捕获用户的语音信号。
    *   摄像头持续捕获用户面前的视觉场景。

3.  **语音转文本**：
    *   STT 模块 (Vosk) 实时处理音频流，将用户的语音转换为文本。例如，将“帮我看看桌子上有什么？”转换为文本字符串。

4.  **视觉信息处理 (按需)**：
    *   **被动感知**：视觉处理模块 (MediaPipe) 可能在后台持续进行基本的场景理解，如识别视野中的主要物体。
    *   **主动分析**：如果用户的指令明确涉及视觉内容（如“桌子上有什么？”），核心逻辑模块会指示视觉处理模块对当前摄像头画面中的相关区域（例如，通过物体检测定位“桌子”）进行更详细的分析，提取物体列表、空间关系等信息。

5.  **意图理解与多模态信息融合**：
    *   核心逻辑模块接收到 STT 转录的文本和（如果相关的）视觉分析结果。
    *   模块分析文本意图。例如，识别出用户希望了解“桌子上的物体”。
    *   如果指令涉及视觉，模块会将文本指令与视觉模块提供的物体列表（例如：“检测到物体：杯子、书本、键盘”）融合成一个更丰富的上下文。

6.  **构建并发送 LLM 请求**：
    *   核心逻辑模块根据融合后的信息构建一个发送给 Gemini API 的提示。例如：“用户正在看一张桌子，上面有[杯子、书本、键盘]。用户问：‘帮我看看桌子上有什么？’请根据这些信息回答。”
    *   对于非视觉问题（如“今天天气怎么样？”），则直接发送文本请求。

7.  **LLM 处理与响应生成**：
    *   Gemini API 接收并处理该提示，理解用户的请求和提供的上下文。
    *   生成一个自然语言的文本回答。例如：“您的桌子上有杯子、书本和键盘。”或“正在查询天气信息...”。

8.  **文本转语音**：
    *   核心逻辑模块将从 Gemini API 收到的文本响应传递给 TTS 模块 (Piper)。
    *   TTS 模块将文本转换为语音。

9.  **语音输出**：
    *   生成的语音通过扬声器播放给用户。

10. **循环与待命**：系统完成本次交互，返回待命状态，准备接收用户的下一次语音指令。

## 3. 关键考虑因素

*   **响应速度**：所有本地模块（Vosk, MediaPipe, Piper）的选择都优先考虑了在树莓派上的运行效率，以确保快速响应。API 调用（Gemini）的网络延迟是主要外部因素。
*   **资源管理**：在树莓派有限的计算资源下，需要优化各模块的资源占用，避免冲突和性能瓶颈。
*   **多语言支持**：STT 和 TTS 模块均需可靠支持中文和英文的识别与合成。
*   **模块化与可扩展性**：采用模块化设计，方便未来功能升级或技术栈调整。
*   **错误处理与鲁棒性**：设计完善的错误处理机制，例如网络请求失败、语音识别不清、视觉识别无结果等情况。
