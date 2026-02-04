# 快速开始指南

## 安装

### 1. 克隆项目
```bash
git clone https://github.com/yuanxiaoaihezhou/AI_AceAttorney.git
cd AI_AceAttorney
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

如果在 Linux 上缺少 tkinter，运行：
```bash
sudo apt-get install python3-tk
```

### 3. 配置 LLM
复制配置文件：
```bash
cp config.example.py config.py
```

编辑 `config.py`，选择 LLM 提供商：

#### 使用 Ollama（本地）
```python
LLM_PROVIDER = "ollama"
OLLAMA_MODEL_NAME = "qwen2:7b"
```

安装 Ollama：
```bash
# 访问 https://ollama.ai 下载安装
ollama pull qwen2:7b
ollama serve
```

#### 使用 SiliconFlow（在线）
```python
LLM_PROVIDER = "siliconflow"
SILICONFLOW_API_KEY = "sk-your-api-key-here"
```

## 运行

### GUI 模式（推荐）
```bash
python main.py
```

这将打开一个图形界面窗口：
- 点击"开始庭审"按钮启动模拟
- 在文本框中查看实时庭审过程
- 控制台也会同步显示输出（便于调试）

### 控制台模式
```bash
python main.py --console
```

直接在终端查看彩色输出。

### 查看帮助
```bash
python main.py --help
```

### 运行演示
体验 GUI 功能（无需 LLM）：
```bash
python demo_gui.py
```

## GUI 界面说明

```
┌─────────────────────────────────────┐
│         AI 逆转裁判                 │
├─────────────────────────────────────┤
│  庭审过程：                         │
│  ┌─────────────────────────────┐   │
│  │                             │   │
│  │  [实时显示]                 │   │
│  │  - 案件信息                 │   │
│  │  - 调查阶段                 │   │
│  │  - 庭审对话                 │   │
│  │  - 判决结果                 │   │
│  │                             │   │
│  └─────────────────────────────┘   │
│                                     │
│  [开始庭审] [清空输出] [退出]      │
│                                     │
│  状态：就绪                         │
└─────────────────────────────────────┘
```

## 功能特性

### 双重输出 🎯
- GUI 窗口：友好的图形界面
- 控制台：调试信息和日志

### 完整流程 📋
1. **案件生成**：AI 自动创建案件、证物、证人
2. **调查阶段**：展示案件信息和可调查内容
3. **庭审阶段**：AI 角色互动，完整的法庭辩论
4. **判决结果**：证人崩溃，案件告破

### AI 角色 🎭
- 法官：控制庭审流程
- 辩护律师：寻找证词矛盾
- 检察官：维护起诉立场
- 证人：作伪证，试图隐瞒真相

## 常见问题

### Q: GUI 无法启动？
**A:** 确保已安装依赖：
```bash
pip install customtkinter
# Linux 用户
sudo apt-get install python3-tk
```

或使用控制台模式：
```bash
python main.py --console
```

### Q: 连接失败？
**A:** 
- **Ollama**: 确保服务已启动 `ollama serve`
- **SiliconFlow**: 检查 API Key 是否正确

### Q: 如何调试？
**A:** 在 `config.py` 中开启调试模式：
```python
DEBUG_MODE = True
SHOW_API_LOGS = True
```

调试信息会同时显示在 GUI 和控制台中。

## 下一步

- 阅读 [README.md](README.md) 了解完整功能
- 查看 [GUI_README.md](GUI_README.md) 了解 GUI 详情
- 运行 `python demo_gui.py` 体验演示

## 需要帮助？

- 查看项目文档
- 提交 Issue 到 GitHub
- 检查配置文件和日志

祝你使用愉快！🎉
