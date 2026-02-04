#!/usr/bin/env python3
"""
AI 逆转裁判 (AI Ace Attorney)
基于大语言模型的《逆转裁判》风格法庭模拟系统

主程序入口
作者: yuanxiaoaihezhou
"""

from colorama import Fore, init

from llm_client import LLMClient
from court_simulation import CourtSimulation

# 初始化颜色输出
init(autoreset=True)


def main():
    """主函数"""
    print(f"{Fore.CYAN}{'='*50}")
    print(f"{Fore.CYAN}AI 逆转裁判 (AI Ace Attorney)")
    print(f"{Fore.CYAN}{'='*50}\n")
    
    if LLMClient.test_connection():
        sim = CourtSimulation()
        sim.run()
    else:
        print(f"\n{Fore.RED}连接失败，请检查配置文件 config.py")
        print(f"{Fore.YELLOW}提示：")
        print(f"{Fore.YELLOW}  - 如果使用 Ollama，请确保服务已启动: ollama serve")
        print(f"{Fore.YELLOW}  - 如果使用 SiliconFlow，请检查 API Key 是否正确")


if __name__ == "__main__":
    main()
