#!/usr/bin/env python3
"""
AI 逆转裁判 - GUI 模块
使用 CustomTkinter 实现图形界面，同时保留控制台输出以便调试
"""

import sys
import threading
import customtkinter as ctk
from io import StringIO
from colorama import Fore, Style


class TeeOutput:
    """同时输出到控制台和GUI的类"""
    
    def __init__(self, console, text_widget):
        self.console = console
        self.text_widget = text_widget
        self.buffer = StringIO()
        
    def write(self, text):
        # 写入控制台
        self.console.write(text)
        self.console.flush()
        
        # 写入GUI（移除ANSI颜色代码）
        if self.text_widget:
            clean_text = self._strip_ansi(text)
            self.text_widget.after(0, self._append_text, clean_text)
    
    def flush(self):
        self.console.flush()
    
    def _strip_ansi(self, text):
        """移除ANSI颜色代码"""
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)
    
    def _append_text(self, text):
        """在GUI文本框中追加文本"""
        self.text_widget.configure(state='normal')
        self.text_widget.insert('end', text)
        self.text_widget.see('end')  # 自动滚动到底部
        self.text_widget.configure(state='disabled')


class AIAceAttorneyGUI:
    """AI 逆转裁判 GUI 主窗口"""
    
    def __init__(self):
        # 设置主题
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # 创建主窗口
        self.window = ctk.CTk()
        self.window.title("AI 逆转裁判 (AI Ace Attorney)")
        self.window.geometry("1000x700")
        
        # 创建界面元素
        self._create_widgets()
        
        # 重定向输出
        self._setup_output_redirect()
        
        # 模拟线程
        self.simulation_thread = None
        self.is_running = False
        
    def _create_widgets(self):
        """创建GUI组件"""
        # 标题
        title_label = ctk.CTkLabel(
            self.window,
            text="AI 逆转裁判",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)
        
        # 输出文本框框架
        output_frame = ctk.CTkFrame(self.window)
        output_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # 标签
        output_label = ctk.CTkLabel(
            output_frame,
            text="庭审过程：",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        output_label.pack(pady=5, anchor="w", padx=10)
        
        # 文本框
        self.output_text = ctk.CTkTextbox(
            output_frame,
            font=ctk.CTkFont(size=12),
            wrap="word"
        )
        self.output_text.pack(pady=5, padx=10, fill="both", expand=True)
        self.output_text.configure(state='disabled')
        
        # 按钮框架
        button_frame = ctk.CTkFrame(self.window)
        button_frame.pack(pady=10, padx=20, fill="x")
        
        # 开始按钮
        self.start_button = ctk.CTkButton(
            button_frame,
            text="开始庭审",
            command=self._start_simulation,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40
        )
        self.start_button.pack(side="left", padx=10, pady=10, expand=True, fill="x")
        
        # 清空按钮
        self.clear_button = ctk.CTkButton(
            button_frame,
            text="清空输出",
            command=self._clear_output,
            font=ctk.CTkFont(size=14),
            height=40
        )
        self.clear_button.pack(side="left", padx=10, pady=10, expand=True, fill="x")
        
        # 退出按钮
        self.exit_button = ctk.CTkButton(
            button_frame,
            text="退出",
            command=self._exit_app,
            font=ctk.CTkFont(size=14),
            height=40,
            fg_color="red",
            hover_color="darkred"
        )
        self.exit_button.pack(side="left", padx=10, pady=10, expand=True, fill="x")
        
        # 状态栏
        self.status_label = ctk.CTkLabel(
            self.window,
            text="就绪",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=5)
    
    def _setup_output_redirect(self):
        """设置输出重定向"""
        # 保存原始的 stdout 和 stderr
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        
        # 创建 Tee 对象
        self.tee_stdout = TeeOutput(self.original_stdout, self.output_text)
        self.tee_stderr = TeeOutput(self.original_stderr, self.output_text)
        
        # 重定向
        sys.stdout = self.tee_stdout
        sys.stderr = self.tee_stderr
    
    def _restore_output(self):
        """恢复输出"""
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr
    
    def _start_simulation(self):
        """启动模拟"""
        if self.is_running:
            print("庭审正在进行中，请等待完成...")
            return
        
        self.is_running = True
        self.start_button.configure(state="disabled")
        self.status_label.configure(text="庭审进行中...")
        
        # 在新线程中运行模拟
        self.simulation_thread = threading.Thread(target=self._run_simulation)
        self.simulation_thread.daemon = True
        self.simulation_thread.start()
    
    def _run_simulation(self):
        """运行法庭模拟"""
        try:
            from llm_client import LLMClient
            from court_simulation import CourtSimulation
            
            print(f"{'='*50}")
            print(f"AI 逆转裁判 (AI Ace Attorney)")
            print(f"{'='*50}\n")
            
            if LLMClient.test_connection():
                sim = CourtSimulation()
                sim.run()
            else:
                print("\n连接失败，请检查配置文件 config.py")
                print("提示：")
                print("  - 如果使用 Ollama，请确保服务已启动: ollama serve")
                print("  - 如果使用 SiliconFlow，请检查 API Key 是否正确")
        except Exception as e:
            print(f"错误: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            self.is_running = False
            self.window.after(0, self._simulation_complete)
    
    def _simulation_complete(self):
        """模拟完成后的处理"""
        self.start_button.configure(state="normal")
        self.status_label.configure(text="就绪")
    
    def _clear_output(self):
        """清空输出文本框"""
        self.output_text.configure(state='normal')
        self.output_text.delete('1.0', 'end')
        self.output_text.configure(state='disabled')
        self.status_label.configure(text="输出已清空")
        # 2秒后恢复状态为"就绪"
        self.window.after(2000, lambda: self.status_label.configure(text="就绪"))
    
    def _exit_app(self):
        """退出应用"""
        self._restore_output()
        self.window.quit()
        self.window.destroy()
    
    def run(self):
        """运行GUI"""
        print("AI 逆转裁判 GUI 已启动")
        print("提示：控制台输出将同时显示在此窗口和终端中")
        self.window.mainloop()


def main():
    """主函数"""
    app = AIAceAttorneyGUI()
    app.run()


if __name__ == "__main__":
    main()
