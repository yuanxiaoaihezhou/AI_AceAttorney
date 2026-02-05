"""
LLM Client Module
提供统一的大语言模型接口，支持多种提供商
"""

import requests
import logging
from typing import List, Dict
from colorama import Fore

from config import (
    LLM_PROVIDER,
    SILICONFLOW_API_KEY,
    SILICONFLOW_API_URL,
    SILICONFLOW_MODEL_NAME,
    OLLAMA_API_URL,
    OLLAMA_MODEL_NAME,
    DEFAULT_TEMPERATURE,
    JSON_TEMPERATURE,
    MAX_TOKENS,
    SHOW_API_LOGS,
    DEBUG_MODE
)

logger = logging.getLogger(__name__)


class LLMClient:
    """统一的 LLM 调用接口，支持多种提供商"""
    
    @staticmethod
    def chat(messages: List[Dict[str, str]], json_mode=False) -> str:
        """统一的 LLM 调用接口，支持多种提供商"""
        logger.debug(f"LLM 请求 - 提供商: {LLM_PROVIDER}, JSON模式: {json_mode}, 消息数: {len(messages)}")
        
        if LLM_PROVIDER == "siliconflow":
            return LLMClient._chat_siliconflow(messages, json_mode)
        elif LLM_PROVIDER == "ollama":
            return LLMClient._chat_ollama(messages, json_mode)
        else:
            error_msg = f"不支持的 LLM 提供商: {LLM_PROVIDER}。支持的提供商: 'siliconflow', 'ollama'"
            print(f"{Fore.RED}{error_msg}")
            logger.error(error_msg)
            raise ValueError(error_msg)

    @staticmethod
    def _chat_siliconflow(messages: List[Dict[str, str]], json_mode=False) -> str:
        """SiliconFlow API 调用"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {SILICONFLOW_API_KEY}"
        }

        payload = {
            "model": SILICONFLOW_MODEL_NAME,
            "messages": messages,
            "stream": False,
            "temperature": JSON_TEMPERATURE if json_mode else DEFAULT_TEMPERATURE,
            "max_tokens": MAX_TOKENS
        }

        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        try:
            if SHOW_API_LOGS:
                print(f"{Fore.CYAN}[API] 请求 SiliconFlow...")
            logger.debug(f"SiliconFlow 请求 - 模型: {SILICONFLOW_MODEL_NAME}, 温度: {payload['temperature']}")
            
            response = requests.post(SILICONFLOW_API_URL, headers=headers, json=payload, timeout=60)
            
            if response.status_code != 200:
                error_msg = f"API Error ({response.status_code}): {response.text}"
                print(f"{Fore.RED}{error_msg}")
                logger.error(error_msg)
                return ""
            
            result = response.json()['choices'][0]['message']['content']
            
            if SHOW_API_LOGS:
                print(f"{Fore.GREEN}[API] 响应成功")
            logger.debug(f"SiliconFlow 响应成功 - 长度: {len(result)} 字符")
            
            return result
        except Exception as e:
            error_msg = f"SiliconFlow 调用异常: {e}"
            print(f"{Fore.RED}{error_msg}")
            logger.error(error_msg, exc_info=DEBUG_MODE)
            return ""

    @staticmethod
    def _chat_ollama(messages: List[Dict[str, str]], json_mode=False) -> str:
        """Ollama 本地 API 调用"""
        # 创建消息列表的副本，避免修改原始列表
        messages_copy = messages.copy()
        
        payload = {
            "model": OLLAMA_MODEL_NAME,
            "messages": messages_copy,
            "stream": False,
            "options": {
                "temperature": JSON_TEMPERATURE if json_mode else DEFAULT_TEMPERATURE,
                "num_predict": MAX_TOKENS
            }
        }

        if json_mode:
            # Ollama 对 JSON 模式的支持
            system_msg = "请以严格的 JSON 格式回复，不要包含任何其他文本。"
            if messages_copy and messages_copy[0]["role"] == "system":
                messages_copy[0]["content"] += "\n" + system_msg
            else:
                messages_copy.insert(0, {"role": "system", "content": system_msg})

        try:
            if SHOW_API_LOGS:
                print(f"{Fore.CYAN}[API] 请求 Ollama 本地服务...")
            logger.debug(f"Ollama 请求 - 模型: {OLLAMA_MODEL_NAME}, 温度: {payload['options']['temperature']}")
            
            response = requests.post(OLLAMA_API_URL, json=payload, timeout=120)
            
            if response.status_code != 200:
                error_msg = f"Ollama API Error ({response.status_code}): {response.text}"
                print(f"{Fore.RED}{error_msg}")
                logger.error(error_msg)
                return ""
            
            result = response.json()['message']['content']
            
            if SHOW_API_LOGS:
                print(f"{Fore.GREEN}[API] 响应成功")
            logger.debug(f"Ollama 响应成功 - 长度: {len(result)} 字符")
            
            return result
        except requests.exceptions.ConnectionError:
            error_msg = "无法连接到 Ollama 服务，请确保 Ollama 已启动"
            print(f"{Fore.RED}{error_msg}")
            print(f"{Fore.YELLOW}提示: 使用 'ollama serve' 启动服务")
            logger.error(error_msg)
            return ""
        except Exception as e:
            error_msg = f"Ollama 调用异常: {e}"
            print(f"{Fore.RED}{error_msg}")
            logger.error(error_msg, exc_info=DEBUG_MODE)
            return ""

    @staticmethod
    def test_connection() -> bool:
        """测试 LLM 连接"""
        provider_name = "SiliconFlow" if LLM_PROVIDER == "siliconflow" else "Ollama"
        model_name = SILICONFLOW_MODEL_NAME if LLM_PROVIDER == "siliconflow" else OLLAMA_MODEL_NAME
        
        print(f"{Fore.CYAN}正在测试连接 [{provider_name}] 模型: {model_name}...")
        logger.info(f"测试 LLM 连接 - 提供商: {provider_name}, 模型: {model_name}")
        
        try:
            res = LLMClient.chat([{"role": "user", "content": "回复OK"}])
            if res:
                print(f"{Fore.GREEN}✅ 连接测试通过！")
                logger.info("LLM 连接测试通过")
                return True
            else:
                print(f"{Fore.RED}❌ 连接测试失败：未收到响应")
                logger.error("LLM 连接测试失败：未收到响应")
                return False
        except Exception as e:
            error_msg = f"连接测试失败: {e}"
            print(f"{Fore.RED}❌ {error_msg}")
            logger.error(error_msg, exc_info=DEBUG_MODE)
            return False
