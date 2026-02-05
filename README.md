# AI 逆转裁判 (AI Ace Attorney)

一个基于大语言模型的《逆转裁判》风格法庭模拟系统。所有角色（包括律师、检察官、法官、证人）都由 AI 扮演，模拟真实的法庭辩论过程。

## 项目简介

本项目实现了一个完全由 AI 驱动的法庭模拟系统，模拟《逆转裁判》游戏中的法庭辩论过程。系统能够自动生成案件、证物和证人证词，并通过多个 AI 角色的互动完成完整的法庭审理流程。

### 核心特点

- **完全 AI 驱动**: 所有角色由 AI 自动扮演，无需人工干预
- **动态案件生成**: AI 自动设计案件、证物、证人证词
- **逼真的法庭辩论**: 模拟《逆转裁判》式的追问、指证、反驳流程
- **多 LLM 支持**: 支持 SiliconFlow 在线 API 和 Ollama 本地部署
- **模块化设计**: 代码结构清晰，易于维护和扩展

## 项目结构

```
AI_AceAttorney/
├── main.py                 # 程序入口，启动法庭模拟
├── llm_client.py          # LLM 客户端，统一的大语言模型接口
├── case_designer.py       # 案件设计者，生成案件剧情和证物
├── agents.py              # AI 角色定义（法官、律师、检察官、证人等）
├── investigation.py       # 调查阶段逻辑
├── court_simulation.py    # 法庭模拟核心逻辑
├── config.py              # 配置文件
├── config.example.py      # 配置文件示例
├── requirements.txt       # Python 依赖
├── README.md              # 项目说明文档（本文件）
└── Purpose.md             # 项目目标和设计理念
```

### 模块说明

#### `main.py` - 程序入口
- 程序的主入口点
- 初始化系统并启动法庭模拟
- 测试 LLM 连接

#### `llm_client.py` - LLM 客户端
- 提供统一的大语言模型调用接口
- 支持多种 LLM 提供商（SiliconFlow、Ollama）
- 处理 API 请求和响应
- 包含连接测试功能

#### `case_designer.py` - 案件设计者
- 使用 LLM 自动生成案件剧本
- 创建案件背景、证物、证人信息
- 设计可调查的地点和 NPC
- 确保证词中包含可被反驳的谎言

#### `agents.py` - AI 角色
定义法庭中的所有 AI 角色：
- `AIAgent`: 角色基类，处理对话历史
- `Judge`: 法官，控制庭审流程
- `Prosecutor`: 检察官，维护起诉立场
- `DefenseAttorney`: 辩护律师，寻找证词矛盾
- `Witness`: 证人（通常是真凶）
- `Detective`: 警探（可选角色）

#### `investigation.py` - 调查阶段
- 实现庭审前的调查阶段
- 展示可调查的地点和 NPC
- 收集证物和线索

#### `court_simulation.py` - 法庭模拟
- 法庭模拟的核心逻辑
- 协调各个角色的互动
- 控制庭审流程
- 判断证人崩溃和案件结束

#### `config.py` - 配置文件
包含所有可配置参数：
- LLM 提供商选择
- API 配置
- 庭审参数（回合数、崩溃阈值等）
- 调试选项

## 安装

### 1. 克隆仓库
```bash
git clone https://github.com/yuanxiaoaihezhou/AI_AceAttorney.git
cd AI_AceAttorney
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置 LLM

复制配置示例文件并编辑：
```bash
cp config.example.py config.py
```

#### 选项 A: 使用 Ollama (推荐用于本地部署)
```python
LLM_PROVIDER = "ollama"
OLLAMA_MODEL_NAME = "qwen2:7b"  # 或其他支持的模型
```

安装 Ollama:
1. 访问 [https://ollama.ai](https://ollama.ai) 下载并安装
2. 下载模型: `ollama pull qwen2:7b`
3. 启动服务: `ollama serve`

#### 选项 B: 使用 SiliconFlow
```python
LLM_PROVIDER = "siliconflow"
SILICONFLOW_API_KEY = "sk-your-api-key"  # 填入你的 API Key
```

## 运行

### 命令行版本

启动程序：
```bash
python main.py
```

### Web 演示版本（推荐用于展示）

启动 Web 服务器：

**Linux/Mac:**
```bash
./start_web.sh
```

**Windows:**
```
start_web.bat
```

**或手动启动:**
```bash
python web_app.py
```

然后在浏览器中访问：`http://localhost:5000`

**Web 版本特色：**
- 🎮 **玩家扮演律师**：通过 Web 界面亲自进行法庭辩论
- 📱 **移动端优化**：完美适配手机竖屏，随时随地游玩
- 🎨 **精美界面**：仿《逆转裁判》风格的现代化设计
- 💼 **投资者展示**：专业的演示界面，适合对外展示
- ⚡ **实时交互**：流畅的对话体验，AI 实时响应

**游戏操作：**
1. **威慑** - 追问证人，要求说明细节
2. **指证** - 选择证物指出证词中的矛盾
3. **案情** - 查看案件详情和证物清单

## 游戏流程

### 1. 案件生成阶段
AI 自动创建案件，包括：
- 案件标题和背景
- 受害者、被告、真凶
- 案发地点和时间
- 证物列表
- 可调查的地点和 NPC
- 证人证词（包含谎言）

### 2. 调查阶段
- 展示案件信息
- 列出可调查的地点
- 列出可询问的 NPC
- 自动收集证物

### 3. 庭审阶段
完整的法庭审理流程：
1. **证人作证**: 证人陈述初始证词（通常包含谎言）
2. **律师分析**: AI 律师分析证词，寻找矛盾
3. **律师行动**: 
   - 【威慑】: 没有明显矛盾时追问细节
   - 【指证】: 发现矛盾时提出证物反驳
4. **检察官反驳**: 检察官强行解释，保护证人
5. **证人回应**: 证人狡辩或在压力下崩溃
6. **法官裁决**: 评估情况，决定是否继续审理

### 4. 判决
当证人彻底崩溃或承认罪行时，法官宣判被告无罪。

## 配置参数

### LLM 配置
- `LLM_PROVIDER`: LLM 提供商（"ollama" 或 "siliconflow"）
- `OLLAMA_MODEL_NAME`: Ollama 模型名称（如 "qwen2:7b"）
- `SILICONFLOW_MODEL_NAME`: SiliconFlow 模型名称
- `SILICONFLOW_API_KEY`: SiliconFlow API 密钥

### 庭审配置
- `MAX_ROUNDS`: 最大庭审回合数，防止死循环（默认: 10）
- `WITNESS_BREAKDOWN_THRESHOLD`: 证人被指证多少次后崩溃（默认: 3）

### LLM 参数
- `DEFAULT_TEMPERATURE`: 生成文本的随机性，0.0-2.0（默认: 1.0）
- `JSON_TEMPERATURE`: 生成 JSON 时的温度（默认: 0.7）
- `MAX_TOKENS`: 最大生成 token 数（默认: 1024）

### 调试配置
- `DEBUG_MODE`: 调试模式，显示真凶等额外信息（默认: False）
- `SHOW_API_LOGS`: 显示 API 调用日志（默认: False）

## 角色系统详解

### 案件设计者 (CaseDesigner)
- 使用 LLM 生成完整的案件剧本
- 确保证人证词包含可被证物反驳的谎言
- 设计多层次的线索和证物
- 创建合理的案件背景

### 法官 (Judge)
- 控制庭审节奏
- 评估辩论情况
- 要求继续审理或做出判决
- 性格威严但优柔寡断

### 辩护律师 (DefenseAttorney)
- 分析证人证词
- 寻找证词与证物的矛盾
- 使用威慑或指证策略
- 热血、坚定的性格

### 检察官 (Prosecutor)
- 维护起诉立场
- 反驳律师的指控
- 强行解释证人的矛盾
- 自信、傲慢的态度

### 证人 (Witness)
- 通常是真凶
- 作伪证试图隐瞒真相
- 在压力下逐渐狡辩
- 被逼到绝境时崩溃

### 警探 (Detective)
- 协助调查工作
- 提供案件背景信息
- 分享调查发现
- 认真负责的性格

## 技术栈

- **Python 3.7+**: 主要编程语言
- **requests**: HTTP 请求库，用于 API 调用
- **colorama**: 终端彩色输出，增强用户体验
- **Ollama / SiliconFlow**: 大语言模型服务

## 扩展开发

### 添加新角色
继承 `AIAgent` 基类创建新角色：

```python
from agents import AIAgent

class NewRole(AIAgent):
    def __init__(self):
        super().__init__("角色名", """
        你是XXX角色。
        你的职责是...
        你的性格是...
        """)
```

### 自定义案件生成
修改 `case_designer.py` 中的 prompt 可以：
- 调整案件复杂度
- 增加证物数量
- 设计更隐蔽的谎言
- 添加更多地点和 NPC

### 调整 AI 行为
修改 `agents.py` 中各角色的 `role_prompt` 可以改变 AI 的性格和行为模式。

## 常见问题

### Q: 连接失败怎么办？
- **Ollama**: 确保服务已启动 (`ollama serve`)，检查模型是否已下载
- **SiliconFlow**: 检查 API Key 是否正确，确认网络连接

### Q: 案件生成失败？
- 检查 LLM 响应是否正常
- 尝试降低 `JSON_TEMPERATURE` 参数
- 开启 `DEBUG_MODE` 查看详细信息

### Q: 庭审总是超时？
- 增加 `MAX_ROUNDS` 参数
- 降低 `WITNESS_BREAKDOWN_THRESHOLD` 参数
- 使用更强大的 LLM 模型

### Q: 如何更换模型？
```bash
# Ollama
ollama pull qwen2.5:14b
# 然后在 config.py 中修改 OLLAMA_MODEL_NAME
```

## 未来计划

根据 `Purpose.md` 文件，未来计划：
- 实现完整的调查阶段（物品交互、NPC 对话）
- 添加更多角色类型
- 增强案件逻辑复杂度
- 实现证物管理系统
- 添加游戏存档功能
- 支持多证人和多回合庭审

## 贡献指南

欢迎提交 Issue 和 Pull Request！

贡献时请：
1. 遵循现有代码风格
2. 添加必要的注释和文档
3. 测试新功能
4. 更新相关文档

## License

MIT License

## 作者

yuanxiaoaihezhou

## 致谢

- 《逆转裁判》系列游戏提供灵感
- Ollama 和 SiliconFlow 提供 LLM 服务支持
