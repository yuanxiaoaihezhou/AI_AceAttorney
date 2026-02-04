"""
AI 逆转裁判 - 配置文件
包含所有可配置的参数，方便用户自定义
"""

# --- LLM 提供商配置 ---
# 支持的提供商: "siliconflow", "ollama"
LLM_PROVIDER = "ollama"

# --- SiliconFlow (硅基流动) 配置 ---
SILICONFLOW_API_KEY = "your-api-key-here"  # 请填入你的 SiliconFlow API Key
SILICONFLOW_API_URL = "https://api.siliconflow.cn/v1/chat/completions"
SILICONFLOW_MODEL_NAME = "deepseek-ai/DeepSeek-V3"

# --- Ollama 本地部署配置 ---
OLLAMA_API_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL_NAME = "qwen2:7b"  # 可选: qwen2:7b, qwen2:4b, qwen2.5:7b 等

# --- 庭审配置 ---
MAX_ROUNDS = 10  # 限制最大回合数，防止死循环
WITNESS_BREAKDOWN_THRESHOLD = 3  # 证人被指证多少次后会崩溃

# --- LLM 参数配置 ---
DEFAULT_TEMPERATURE = 1.0  # 默认温度，控制随机性 (0.0-2.0)
JSON_TEMPERATURE = 0.7  # 生成 JSON 时的温度
MAX_TOKENS = 1024  # 最大生成 token 数

# --- 调试配置 ---
DEBUG_MODE = False  # 开启后会显示更多调试信息
SHOW_API_LOGS = False  # 是否显示 API 调用日志
