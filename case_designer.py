"""
Case Designer Module
负责生成逆转裁判风格的案件
"""

import json
from typing import Dict, Any
from colorama import Fore

from llm_client import LLMClient
from config import (
    LLM_PROVIDER,
    SILICONFLOW_MODEL_NAME,
    OLLAMA_MODEL_NAME,
    DEBUG_MODE
)


class CaseDesigner:
    """案件设计者 - 负责生成逆转裁判风格的案件"""
    
    def generate_case(self) -> Dict[str, Any]:
        """生成一个完整的案件"""
        model_name = SILICONFLOW_MODEL_NAME if LLM_PROVIDER == "siliconflow" else OLLAMA_MODEL_NAME
        print(f"{Fore.CYAN}正在构思案件剧本... (使用 {model_name})")

        prompt = """
        你是一位悬疑小说家。请设计一个《逆转裁判》风格的法庭案件。

        要求：
        1. 证人必须是真凶。
        2. 证人的"初始证词"必须包含一个明显的谎言，这个谎言与"证物列表"中的某一项直接矛盾（例如时间、地点、物品状态）。
        3. 请确保真凶的名字和死者的名字不要搞混。
        4. 案件应该有足够的深度和复杂性，包含多个证物和线索。
        5. 需要设计可供调查的地点和NPC。

        请以严格的 JSON 格式输出：
        {
            "case_title": "案件标题",
            "background": "简短背景（死者、时间、死因）",
            "true_killer": "真凶名字",
            "suspect": "被告（无辜者）名字",
            "victim": "死者名字",
            "crime_scene": "案发地点详细描述",
            "time_of_crime": "案发时间",
            "evidence_list": [
                {"name": "证物名", "description": "证物详细描述", "location": "在哪里可以找到"}
            ],
            "locations": [
                {"name": "地点名", "description": "地点描述", "available_items": ["可调查的物品"]}
            ],
            "npcs": [
                {"name": "NPC名字", "role": "角色", "location": "所在地点", "knows": "掌握的信息"}
            ],
            "witness": {
                "name": "真凶名字",
                "personality": "性格",
                "secret": "作案手法简述",
                "initial_testimony": "一段简短的证词（必须包含一个能被证物直接反驳的谎言）",
                "motive": "作案动机"
            }
        }
        直接输出JSON, 不要markdown标记。
        """

        response = LLMClient.chat([{"role": "user", "content": prompt}], json_mode=True)
        
        # 清理响应，移除可能的 markdown 标记（有些模型可能不遵守指令）
        clean_response = response.replace("```json", "").replace("```", "").strip()
        
        # 验证响应是否为有效的 JSON
        if not clean_response:
            print(f"{Fore.RED}收到空响应，重试中...")
            return self.generate_case()

        try:
            case_data = json.loads(clean_response)
            
            # 验证必要字段
            required_fields = ["case_title", "background", "true_killer", "suspect", "evidence_list", "witness"]
            for field in required_fields:
                if field not in case_data:
                    print(f"{Fore.YELLOW}警告: 缺少必要字段 {field}，重新生成...")
                    return self.generate_case()
            
            if DEBUG_MODE:
                print(f"{Fore.GREEN}案件生成成功")
                
            return case_data
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}JSON 解析失败: {e}")
            print(f"{Fore.YELLOW}重试中...")
            return self.generate_case()
        except Exception as e:
            print(f"{Fore.RED}生成失败: {e}")
            print(f"{Fore.YELLOW}重试中...")
            return self.generate_case()
