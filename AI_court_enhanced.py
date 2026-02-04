"""
AI 逆转裁判 - 增强版
包含庭审前调查阶段、更多角色、地点探索等功能
"""

import requests
import json
import time
import re
from typing import List, Dict, Any, Optional
from colorama import Fore, Style, init

# 导入配置文件
from config import (
    LLM_PROVIDER,
    SILICONFLOW_API_KEY,
    SILICONFLOW_API_URL,
    SILICONFLOW_MODEL_NAME,
    OLLAMA_API_URL,
    OLLAMA_MODEL_NAME,
    MAX_ROUNDS,
    WITNESS_BREAKDOWN_THRESHOLD,
    DEFAULT_TEMPERATURE,
    JSON_TEMPERATURE,
    MAX_TOKENS,
    DEBUG_MODE,
    SHOW_API_LOGS
)

# 初始化颜色输出
init(autoreset=True)


# --- 工具类：通用 LLM 接口 ---
class LLMClient:
    @staticmethod
    def chat(messages: List[Dict[str, str]], json_mode=False) -> str:
        """统一的 LLM 调用接口，支持多种提供商"""
        if LLM_PROVIDER == "siliconflow":
            return LLMClient._chat_siliconflow(messages, json_mode)
        elif LLM_PROVIDER == "ollama":
            return LLMClient._chat_ollama(messages, json_mode)
        else:
            print(f"{Fore.RED}不支持的 LLM 提供商: {LLM_PROVIDER}")
            return ""

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
            
            response = requests.post(SILICONFLOW_API_URL, headers=headers, json=payload, timeout=60)
            
            if response.status_code != 200:
                print(f"{Fore.RED}API Error ({response.status_code}): {response.text}")
                return ""
            
            result = response.json()['choices'][0]['message']['content']
            
            if SHOW_API_LOGS:
                print(f"{Fore.GREEN}[API] 响应成功")
            
            return result
        except Exception as e:
            print(f"{Fore.RED}SiliconFlow 调用异常: {e}")
            return ""

    @staticmethod
    def _chat_ollama(messages: List[Dict[str, str]], json_mode=False) -> str:
        """Ollama 本地 API 调用"""
        payload = {
            "model": OLLAMA_MODEL_NAME,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": JSON_TEMPERATURE if json_mode else DEFAULT_TEMPERATURE,
                "num_predict": MAX_TOKENS
            }
        }

        if json_mode:
            # Ollama 对 JSON 模式的支持
            system_msg = "请以严格的 JSON 格式回复，不要包含任何其他文本。"
            if messages and messages[0]["role"] == "system":
                messages[0]["content"] += "\n" + system_msg
            else:
                messages.insert(0, {"role": "system", "content": system_msg})

        try:
            if SHOW_API_LOGS:
                print(f"{Fore.CYAN}[API] 请求 Ollama 本地服务...")
            
            response = requests.post(OLLAMA_API_URL, json=payload, timeout=120)
            
            if response.status_code != 200:
                print(f"{Fore.RED}Ollama API Error ({response.status_code}): {response.text}")
                return ""
            
            result = response.json()['message']['content']
            
            if SHOW_API_LOGS:
                print(f"{Fore.GREEN}[API] 响应成功")
            
            return result
        except requests.exceptions.ConnectionError:
            print(f"{Fore.RED}无法连接到 Ollama 服务，请确保 Ollama 已启动")
            print(f"{Fore.YELLOW}提示: 使用 'ollama serve' 启动服务")
            return ""
        except Exception as e:
            print(f"{Fore.RED}Ollama 调用异常: {e}")
            return ""

    @staticmethod
    def test_connection() -> bool:
        """测试 LLM 连接"""
        provider_name = "SiliconFlow" if LLM_PROVIDER == "siliconflow" else "Ollama"
        model_name = SILICONFLOW_MODEL_NAME if LLM_PROVIDER == "siliconflow" else OLLAMA_MODEL_NAME
        
        print(f"{Fore.CYAN}正在测试连接 [{provider_name}] 模型: {model_name}...")
        
        try:
            res = LLMClient.chat([{"role": "user", "content": "回复OK"}])
            if res:
                print(f"{Fore.GREEN}✅ 连接测试通过！")
                return True
            else:
                print(f"{Fore.RED}❌ 连接测试失败：未收到响应")
                return False
        except Exception as e:
            print(f"{Fore.RED}❌ 连接测试失败: {e}")
            return False


# --- 核心：案件设计者 ---
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
        直接输出JSON，不要markdown标记。
        """

        response = LLMClient.chat([{"role": "user", "content": prompt}], json_mode=True)
        clean_response = response.replace("```json", "").replace("```", "").strip()

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


# --- 调查阶段管理器 ---
class InvestigationPhase:
    """庭审前调查阶段"""
    
    def __init__(self, case_data: Dict[str, Any]):
        self.case_data = case_data
        self.collected_evidence = []
        self.interviewed_npcs = []
        
    def start(self):
        """开始调查阶段"""
        print(f"\n{Fore.YELLOW}=== 调查阶段 ===")
        print(f"{Fore.WHITE}案件发生后，作为辩护律师，你需要收集证据和线索。")
        print(f"{Fore.WHITE}被告 {self.case_data.get('suspect', '未知')} 被指控犯罪。")
        print(f"{Fore.WHITE}背景: {self.case_data.get('background', '未知')}")
        
        # 显示可调查的地点
        locations = self.case_data.get('locations', [])
        if locations:
            print(f"\n{Fore.CYAN}可调查的地点:")
            for i, loc in enumerate(locations, 1):
                print(f"{i}. {loc['name']} - {loc.get('description', '无描述')}")
        
        # 显示可询问的 NPC
        npcs = self.case_data.get('npcs', [])
        if npcs:
            print(f"\n{Fore.CYAN}可询问的人物:")
            for i, npc in enumerate(npcs, 1):
                print(f"{i}. {npc['name']} ({npc.get('role', '未知')}) - 在 {npc.get('location', '某处')}")
        
        print(f"\n{Fore.GREEN}提示: 调查阶段已简化，将自动收集所有证物。")
        print(f"{Fore.GREEN}按回车键继续进入庭审...")
        input()
        
        # 自动收集所有证物（简化版）
        self.collected_evidence = self.case_data.get('evidence_list', [])
        print(f"{Fore.GREEN}已收集 {len(self.collected_evidence)} 件证物！")


# --- 角色代理基类 ---
class AIAgent:
    """AI 角色代理基类"""
    
    def __init__(self, name: str, role_prompt: str):
        self.name = name
        self.history = [{"role": "system", "content": role_prompt}]

    def speak(self, context_msg: str) -> str:
        """让角色说话"""
        self.history.append({"role": "user", "content": context_msg})
        response = LLMClient.chat(self.history)
        self.history.append({"role": "assistant", "content": response})
        return response


# --- 具体角色类 ---
class Judge(AIAgent):
    """法官"""
    
    def __init__(self):
        super().__init__("法官", """
        你是由AI扮演的《逆转裁判》法官。

        职责：
        1. 只要证人还没有完全承认罪行，或者还没有彻底崩溃，你就必须要求继续审理。
        2. 不要轻易宣判无罪。只有当证人彻底无法解释矛盾，并承认自己说谎时，才考虑宣判。
        3. 你的性格是威严但有点优柔寡断，容易被双方律师的话语左右。

        重要：除非用户明确提示你"证人已崩溃"，否则请多让双方辩论几轮。
        """)


class Prosecutor(AIAgent):
    """检察官"""
    
    def __init__(self, evidence_list):
        evidence_str = "\n".join([f"- {e['name']}: {e['description']}" for e in evidence_list])
        super().__init__("检察官", f"""
        你是御剑怜侍检察官风格的AI。你的目标是认定嫌疑人有罪。
        你持有的证物信息：
        {evidence_str}

        规则：
        1. 即使律师指出了矛盾，你也要强行解释（例如："那只是记忆错误！" "那只是巧合！"）。
        2. 不要编造证物列表中不存在的细节。
        3. 每句话都要充满自信和傲慢。
        4. 开头必须用"异议！" (Objection!)。
        """)


class DefenseAttorney(AIAgent):
    """辩护律师"""
    
    def __init__(self, evidence_list):
        self.evidence = evidence_list
        evidence_str = "\n".join([f"- {e['name']}: {e['description']}" for e in self.evidence])

        super().__init__("律师", f"""
        你是成步堂龙一风格的律师。
        现有证物：
        {evidence_str}

        行动逻辑：
        1. 检查证人的话与证物是否有矛盾。
        2. 如果发现矛盾，请输出：【指证：证物名】+ 你的逻辑分析。
        3. 如果没有明显矛盾，请输出：【威慑】+ 追问细节。
        4. 你的语气要热血、坚定。
        """)


class Witness(AIAgent):
    """证人（通常是真凶）"""
    
    def __init__(self, name, profile, secret, initial_testimony):
        super().__init__(f"证人({name})", f"""
        你扮演法庭证人 {name}，同时你也是真凶。
        你的性格：{profile}
        你的秘密（真相）：{secret}

        规则：
        1. 无论如何都不能承认自己是凶手，直到最后关头。
        2. 如果律师指出了矛盾，你要编造一个新的谎言来掩盖。
        3. 只有当被追问得体无完肤（逻辑完全崩塌）时，你才会崩溃。
        4. 崩溃的表现是大喊大叫、说话结巴、语无伦次。
        """)
        self.initial_testimony = initial_testimony


class Detective(AIAgent):
    """警探（可选角色）"""
    
    def __init__(self, case_info: str):
        super().__init__("警探", f"""
        你是糸锋千寻风格的警探。你负责案件的初步调查。
        
        案件信息：
        {case_info}
        
        你的性格：
        - 认真负责，但有时过于刻板
        - 相信科学证据
        - 会协助律师，但不会越界
        """)


# --- 庭审模拟器 ---
class CourtSimulation:
    """法庭模拟系统"""
    
    def __init__(self):
        self.designer = CaseDesigner()

    def run(self):
        """运行完整的法庭模拟"""
        # 1. 生成案件
        case = self.designer.generate_case()

        print(f"\n{Fore.YELLOW}=== 案件信息 ===")
        print(f"标题: {case['case_title']}")
        print(f"背景: {case['background']}")
        print(f"被告: {case['suspect']}")
        print(f"受害者: {case.get('victim', '未知')}")
        
        if DEBUG_MODE:
            print(f"真凶: {case['true_killer']}")
            print(f"证物: {[e['name'] for e in case['evidence_list']]}")
        
        print(f"{Fore.YELLOW}=================\n")

        # 2. 调查阶段（简化版）
        investigation = InvestigationPhase(case)
        investigation.start()

        # 3. 庭审阶段
        self.run_trial(case, investigation.collected_evidence)

    def run_trial(self, case: Dict[str, Any], evidence_list: List[Dict[str, str]]):
        """运行庭审流程"""
        print(f"\n{Fore.WHITE}--- 开庭 ---")
        
        # 初始化角色
        judge = Judge()
        prosecutor = Prosecutor(evidence_list)
        lawyer = DefenseAttorney(evidence_list)
        witness = Witness(
            case['witness']['name'],
            case['witness']['personality'],
            case['witness']['secret'],
            case['witness']['initial_testimony']
        )

        print(f"{Fore.RED}法官:{Style.RESET_ALL} 开庭。证人 {case['witness']['name']}，请入庭并作证。")

        current_context = f"证人发言：{case['witness']['initial_testimony']}"
        print(f"{Fore.CYAN}证人:{Style.RESET_ALL} {case['witness']['initial_testimony']}")

        witness_breakdown_count = 0  # 记录证人被击破的次数

        for round_num in range(MAX_ROUNDS):
            print(f"\n{Fore.MAGENTA}=== 第 {round_num + 1} 回合 ===")

            # 1. 律师发言
            lawyer_msg = f"现在是你的回合。证人刚才说了：'{current_context}'。请找出矛盾！"
            lawyer_response = lawyer.speak(lawyer_msg)
            print(f"{Fore.BLUE}律师:{Style.RESET_ALL} {lawyer_response}")

            action_type = "威慑"
            presented_evidence = "无"
            if "【指证：" in lawyer_response:
                action_type = "指证"
                match = re.search(r"【指证：(.*?)】", lawyer_response)
                if match:
                    presented_evidence = match.group(1)

            # 2. 检察官反驳
            pros_msg = f"律师刚刚进行了{action_type}，并说了：{lawyer_response}。请帮证人解围，反驳律师！"
            pros_response = prosecutor.speak(pros_msg)
            print(f"{Fore.RED}检察官:{Style.RESET_ALL} {pros_response}")

            # 3. 证人反应
            if action_type == "指证":
                witness_breakdown_count += 1
                wit_msg = f"律师拿出了证据 {presented_evidence} 指出了你的矛盾！检察官虽然帮你说话，但这个证据很强。请试图狡辩，或者编造一个新的理由！(这是你第{witness_breakdown_count}次被拆穿)"

                if witness_breakdown_count >= WITNESS_BREAKDOWN_THRESHOLD:
                    wit_msg += " 你的逻辑已经无法自圆其说了，请表现出彻底崩溃！"
            else:
                wit_msg = f"律师在追问细节。请坚持你的说法，不要露馅。"

            witness_response = witness.speak(wit_msg)
            print(f"{Fore.CYAN}证人:{Style.RESET_ALL} {witness_response}")

            current_context = witness_response

            # 4. 法官裁决
            judge_context = f"本回合总结：律师指出矛盾。证人回答：{witness_response}"
            if witness_breakdown_count >= WITNESS_BREAKDOWN_THRESHOLD or ("我承认" in witness_response or "是我做的" in witness_response):
                judge_msg = f"{judge_context}。证人似乎已经承认或彻底崩溃了。请做出最后判决。"
            else:
                judge_msg = f"{judge_context}。证人还在狡辩。请要求律师继续追问，或者要求证人修正证词。不要宣判无罪。"

            judge_response = judge.speak(judge_msg)
            print(f"{Fore.YELLOW}法官:{Style.RESET_ALL} {judge_response}")

            if "无罪" in judge_response:
                print(f"\n{Fore.GREEN}=== 庭审结束，被告无罪释放！ ===")
                break

            time.sleep(1.5)

        else:
            print(f"\n{Fore.RED}=== 庭审超时，休庭 ===")


if __name__ == "__main__":
    print(f"{Fore.CYAN}{'='*50}")
    print(f"{Fore.CYAN}AI 逆转裁判 - 增强版")
    print(f"{Fore.CYAN}{'='*50}\n")
    
    if LLMClient.test_connection():
        sim = CourtSimulation()
        sim.run()
    else:
        print(f"\n{Fore.RED}连接失败，请检查配置文件 config.py")
        print(f"{Fore.YELLOW}提示：")
        print(f"{Fore.YELLOW}  - 如果使用 Ollama，请确保服务已启动: ollama serve")
        print(f"{Fore.YELLOW}  - 如果使用 SiliconFlow，请检查 API Key 是否正确")
