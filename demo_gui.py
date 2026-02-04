#!/usr/bin/env python3
"""
GUI 功能演示脚本
展示 TeeOutput 和输出重定向的工作原理
可在无图形环境下运行，验证核心逻辑
"""

import sys
import time
import re
from colorama import Fore, Style, init

init(autoreset=True)


class MockGUITextWidget:
    """模拟 GUI 文本框，用于演示"""
    
    def __init__(self):
        self.content = []
    
    def append(self, text):
        """模拟追加文本到 GUI"""
        self.content.append(text)


class DemoTeeOutput:
    """演示版本的 TeeOutput"""
    
    def __init__(self, console, mock_gui):
        self.console = console
        self.mock_gui = mock_gui
        self.ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    
    def write(self, text):
        # 1. 写入控制台（保留颜色）
        self.console.write(text)
        self.console.flush()
        
        # 2. 写入 GUI（移除颜色代码）
        # 保留所有内容包括空白字符以保持格式
        clean_text = self.ansi_escape.sub('', text)
        if clean_text.strip():  # 跳过纯空白行以保持简洁
            self.mock_gui.append(clean_text)
    
    def flush(self):
        self.console.flush()


def demo_simulation():
    """模拟一个简短的法庭过程"""
    print(f"\n{Fore.CYAN}{'='*50}")
    print(f"{Fore.CYAN}AI 逆转裁判 - 演示模式")
    print(f"{Fore.CYAN}{'='*50}\n")
    
    print(f"{Fore.YELLOW}=== 案件信息 ===")
    print("标题: 神秘的办公室凶案")
    print("被告: 张三")
    print(f"{Fore.YELLOW}=================\n")
    
    time.sleep(1)
    
    print(f"{Fore.WHITE}--- 开庭 ---")
    print(f"{Fore.RED}法官: 开庭。证人请入庭并作证。\n")
    
    time.sleep(1)
    
    print(f"{Fore.CYAN}证人: 我在案发时刻一直在家里看电视。\n")
    
    time.sleep(1)
    
    print(f"{Fore.BLUE}律师: 【指证：通话记录】证人你说在家，但通话记录显示你当时在案发现场附近！\n")
    
    time.sleep(1)
    
    print(f"{Fore.RED}检察官: 异议！通话记录只能说明手机位置，不能证明证人在场！\n")
    
    time.sleep(1)
    
    print(f"{Fore.CYAN}证人: 啊...我、我记错了...其实我是出去买东西了...\n")
    
    time.sleep(1)
    
    print(f"{Fore.YELLOW}法官: 证人请如实作证！\n")
    
    print(f"{Fore.GREEN}=== 庭审继续中... ===\n")


def main():
    """主演示函数"""
    print("╔═══════════════════════════════════════════════════╗")
    print("║         AI 逆转裁判 - GUI 功能演示               ║")
    print("╚═══════════════════════════════════════════════════╝")
    
    print("\n本演示展示 GUI 模式的核心功能：")
    print("1. 同时输出到控制台和 GUI（模拟）")
    print("2. 自动移除 ANSI 颜色代码")
    print("3. 保留控制台的彩色输出")
    
    print("\n" + "="*50)
    print("开始演示...")
    print("="*50)
    
    # 保存原始 stdout
    original_stdout = sys.stdout
    
    # 创建模拟 GUI
    mock_gui = MockGUITextWidget()
    
    # 创建 Tee 输出
    tee = DemoTeeOutput(original_stdout, mock_gui)
    
    # 重定向输出
    sys.stdout = tee
    
    try:
        # 运行模拟
        demo_simulation()
    finally:
        # 恢复输出
        sys.stdout = original_stdout
    
    # 显示捕获的内容
    print("\n" + "="*50)
    print("GUI 捕获的内容（已移除颜色代码）：")
    print("="*50)
    print(f"\n共捕获 {len(mock_gui.content)} 条消息\n")
    
    for i, msg in enumerate(mock_gui.content[:10], 1):  # 只显示前10条
        print(f"{i}. {msg.strip()}")
    
    if len(mock_gui.content) > 10:
        print(f"... 还有 {len(mock_gui.content) - 10} 条消息")
    
    print("\n" + "="*50)
    print("演示完成！")
    print("="*50)
    
    print("\n说明：")
    print("- 上面的输出同时显示在控制台（有颜色）")
    print("- 并被捕获到 GUI 文本框（无颜色）")
    print("- 这就是 GUI 模式的工作原理！")
    print("\n运行实际程序请使用: python main.py")


if __name__ == "__main__":
    main()
