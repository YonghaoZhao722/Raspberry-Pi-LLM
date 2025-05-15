#!/usr/bin/env python3
"""
树莓派多模态视觉语音交互助手启动脚本
"""
import os
import sys

# 将src目录添加到Python路径中
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

# 导入并运行主程序
from main import main

if __name__ == "__main__":
    main() 