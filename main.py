#!/usr/bin/env python3
"""
AI 逆转裁判 (AI Ace Attorney)
基于大语言模型的《逆转裁判》风格法庭模拟系统

主程序入口
作者: yuanxiaoaihezhou
"""

import sys
from colorama import Fore, init

from llm_client import LLMClient
from court_simulation import CourtSimulation

# 初始化颜色输出
init(autoreset=True)


def run_console_mode():
    """控制台模式"""
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


def run_gui_mode():
    """GUI模式"""
    try:
        from gui import AIAceAttorneyGUI
        app = AIAceAttorneyGUI()
        app.run()
    except ImportError as e:
        print(f"{Fore.RED}错误：无法启动GUI模式")
        print(f"{Fore.YELLOW}请安装依赖：pip install customtkinter")
        print(f"{Fore.YELLOW}详细错误：{str(e)}")
        print(f"\n{Fore.CYAN}回退到控制台模式...")
        run_console_mode()


def main():
    """主函数"""
    # 检查命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == "--console" or sys.argv[1] == "-c":
            print(f"{Fore.CYAN}使用控制台模式\n")
            run_console_mode()
        elif sys.argv[1] == "--gui" or sys.argv[1] == "-g":
            print(f"{Fore.CYAN}使用GUI模式\n")
            run_gui_mode()
        elif sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print(f"{Fore.CYAN}AI 逆转裁判 (AI Ace Attorney)")
            print(f"\n使用方法：")
            print(f"  python main.py           # 默认使用GUI模式")
            print(f"  python main.py --gui     # 使用GUI模式")
            print(f"  python main.py --console # 使用控制台模式")
            print(f"  python main.py --help    # 显示帮助信息")
        else:
            print(f"{Fore.RED}未知参数：{sys.argv[1]}")
            print(f"{Fore.YELLOW}使用 --help 查看帮助信息")
    else:
        # 默认使用GUI模式
        run_gui_mode()


if __name__ == "__main__":
    main()
