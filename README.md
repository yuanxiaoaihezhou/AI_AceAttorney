# AI 逆转裁判 (AI Ace Attorney)

一个基于大语言模型的《逆转裁判》风格法庭模拟系统。所有角色（包括律师、检察官、法官、证人）都由 AI 扮演，模拟真实的法庭辩论过程。

## 功能特点

- **完全 AI 驱动**: 所有角色由 AI 自动扮演
- **动态案件生成**: AI 自动设计案件、证物、证人证词
- **逼真的法庭辩论**: 模拟《逆转裁判》式的追问、指证、反驳流程
- **多 LLM 支持**: 支持 SiliconFlow 在线 API 和 Ollama 本地部署

## 角色系统

- **案件设计者**: 负责生成案件剧情、证物、证人信息
- **法官**: 控制庭审流程，做出裁决
- **辩护律师**: 寻找证人证词中的矛盾，提出证物指证
- **检察官**: 维护起诉立场，反驳律师的指控
- **证人**: 通常是真凶，会说谎并试图隐瞒真相

## 安装

1. 克隆仓库
```bash
git clone https://github.com/yuanxiaoaihezhou/AI_AceAttorney.git
cd AI_AceAttorney
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置 LLM

编辑 `config.py` 文件：

**使用 Ollama (推荐用于本地部署)**:
```python
LLM_PROVIDER = "ollama"
OLLAMA_MODEL_NAME = "qwen2:7b"  # 或其他支持的模型
```

确保 Ollama 服务已启动：
```bash
ollama serve
```

**使用 SiliconFlow**:
```python
LLM_PROVIDER = "siliconflow"
SILICONFLOW_API_KEY = "sk-your-api-key"  # 填入你的 API Key
```

## 运行

```bash
python AI_court.py
```

## 配置说明

所有配置项都在 `config.py` 中：

- `LLM_PROVIDER`: LLM 提供商 ("ollama" 或 "siliconflow")
- `MAX_ROUNDS`: 最大庭审回合数
- `WITNESS_BREAKDOWN_THRESHOLD`: 证人被指证多少次后会崩溃
- `DEFAULT_TEMPERATURE`: 生成文本的随机性 (0.0-2.0)
- `DEBUG_MODE`: 调试模式开关

详细配置请参考 `config.py` 文件中的注释。

## 游戏流程

1. **案件生成**: AI 自动创建一个案件，包括受害者、嫌疑人、真凶、证物等
2. **开庭审理**: 
   - 证人作证（通常包含谎言）
   - 律师分析证词，寻找矛盾
   - 律师可以"威慑"追问或"指证"提出证物
   - 检察官反驳律师
   - 证人回应（狡辩或崩溃）
   - 法官裁决是否继续审理
3. **判决**: 当证人彻底崩溃或承认罪行时，法官宣判被告无罪

## 技术栈

- Python 3.7+
- requests: HTTP 请求库
- colorama: 终端彩色输出
- Ollama / SiliconFlow: LLM 服务

## 待完善功能

根据 Purpose.md，未来计划添加：
- 庭审前调查阶段（探索地点、收集线索、询问 NPC）
- 更多角色（警察、受害人、多个证人）
- 更复杂的案件逻辑
- 证物管理系统
- 游戏存档功能

## License

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
