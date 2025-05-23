# 技术选型总结

经过调研和评估，针对您的多模态视觉语音交互助手项目，我们确定了以下技术方案，优先考虑了响应速度、树莓派兼容性以及中英文支持：

*   **大语言模型 (LLM)**：Google Gemini 2.0 Flash (通过 API 调用)。您已提供 API 密钥。
*   **文本转语音 (TTS)**：Piper。这是一款本地运行的 TTS 系统，速度快，支持中英文，并且针对树莓派进行了优化。
*   **语音转文本 (STT)**：Vosk。这是一款轻量级的本地 STT 引擎，支持多种语言（包括中文和英文），在树莓派等嵌入式设备上表现良好，响应速度快，并且可以离线运行。
*   **视觉识别**：MediaPipe。这是一个由 Google 开发的跨平台框架，提供了多种预训练的视觉模型（如物体检测、人脸检测等），在树莓派等边缘设备上有较好的性能表现，能够满足物体识别和根据指令分析图像内容的需求。

这些选择旨在平衡云端大模型的强大能力与本地处理的快速响应和离线可用性。
