"""
AI 逆转裁判 - 配置示例
这是一个示例配置文件，展示了如何配置不同的 LLM 提供商
"""

# ======================================
# 示例 1: 使用 Ollama 本地部署 (推荐)
# ======================================
"""
LLM_PROVIDER = "ollama"

# Ollama 配置
OLLAMA_API_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL_NAME = "qwen2:7b"  # 可选: qwen2:4b, qwen2:7b, qwen2.5:7b 等

# 使用步骤:
# 1. 安装 Ollama: https://ollama.ai
# 2. 下载模型: ollama pull qwen2:7b
# 3. 启动服务: ollama serve
# 4. 运行程序: python AI_court.py
"""

# ======================================
# 示例 2: 使用 SiliconFlow 在线 API
# ======================================
"""
LLM_PROVIDER = "siliconflow"

# SiliconFlow 配置
SILICONFLOW_API_KEY = "sk-your-api-key-here"  # 替换为你的 API Key
SILICONFLOW_API_URL = "https://api.siliconflow.cn/v1/chat/completions"
SILICONFLOW_MODEL_NAME = "deepseek-ai/DeepSeek-V3"

# 使用步骤:
# 1. 注册 SiliconFlow: https://cloud.siliconflow.cn
# 2. 获取 API Key
# 3. 填入上面的 SILICONFLOW_API_KEY
# 4. 运行程序: python AI_court.py
"""

# ======================================
# 其他配置参数
# ======================================

# 庭审配置
MAX_ROUNDS = 10  # 最大回合数
WITNESS_BREAKDOWN_THRESHOLD = 3  # 证人被指证多少次后会崩溃

# LLM 参数
DEFAULT_TEMPERATURE = 1.0  # 生成文本的随机性 (0.0-2.0)
JSON_TEMPERATURE = 0.7  # 生成 JSON 时的温度
MAX_TOKENS = 1024  # 最大生成 token 数

# 调试配置
DEBUG_MODE = False  # 开启后显示调试信息（包括真凶名字）
SHOW_API_LOGS = False  # 显示 API 调用日志
