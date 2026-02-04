import requests
import json
import time
import re
from typing import List, Dict, Any, Optional
from colorama import Fore, Style, init

# 初始化颜色输出
init(autoreset=True)

# --- 配置部分 ---
LLM_PROVIDER = "siliconflow"

# SiliconFlow (硅基流动) 配置
SILICONFLOW_API_KEY = "sk-xxxx"  # 请确保填入你的 Key
SILICONFLOW_API_URL = "https://api.siliconflow.cn/v1/chat/completions"
SILICONFLOW_MODEL_NAME = "deepseek-ai/DeepSeek-V3"

MAX_ROUNDS = 10  # 限制最大回合数，防止死循环


# --- 工具类：通用 LLM 接口 (保持不变) ---
class LLMClient:
    @staticmethod
    def chat(messages: List[Dict[str, str]], json_mode=False) -> str:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {SILICONFLOW_API_KEY}"
        }

        # 针对角色扮演优化了 temperature
        payload = {
            "model": SILICONFLOW_MODEL_NAME,
            "messages": messages,
            "stream": False,
            "temperature": 1.0,  # 稍微提高创造性
            "max_tokens": 1024
        }

        if json_mode:
            payload["response_format"] = {"type": "json_object"}
            payload["temperature"] = 0.7  # 生成 JSON 时降低随机性

        try:
            response = requests.post(SILICONFLOW_API_URL, headers=headers, json=payload)
            if response.status_code != 200:
                print(f"{Fore.RED}API Error ({response.status_code}): {response.text}")
                return ""
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            print(f"{Fore.RED}LLM调用异常: {e}")
            return ""

    @staticmethod
    def test_connection() -> bool:
        print(f"{Fore.CYAN}正在测试连接 [siliconflow]...")
        try:
            res = LLMClient.chat([{"role": "user", "content": "回复OK"}])
            if res:
                print(f"{Fore.GREEN}✅ 测试通过！")
                return True
            return False
        except:
            return False


# --- 核心：案件设计者 (优化 Prompt) ---
class CaseDesigner:
    def generate_case(self) -> Dict[str, Any]:
        print(f"{Fore.CYAN}正在构思案件剧本... (使用 {SILICONFLOW_MODEL_NAME})")

        prompt = """
        你是一位悬疑小说家。请设计一个《逆转裁判》风格的法庭案件。

        要求：
        1. 证人必须是真凶。
        2. 证人的"初始证词"必须包含一个明显的谎言，这个谎言与"证物列表"中的某一项直接矛盾（例如时间、地点、物品状态）。
        3. 请确保真凶的名字和死者的名字不要搞混。

        请以严格的 JSON 格式输出：
        {
            "case_title": "案件标题",
            "background": "简短背景（死者、时间、死因）",
            "true_killer": "真凶名字",
            "suspect": "被告（无辜者）名字",
            "evidence_list": [
                {"name": "证物名", "description": "证物详细描述（这是律师破案的关键，请写具体点，例如'上面印着xx时间'）"}
            ],
            "witness": {
                "name": "真凶名字",
                "personality": "性格（如：傲慢、胆小、阴险）",
                "secret": "作案手法简述",
                "initial_testimony": "一段简短的证词（必须包含一个能被证物直接反驳的谎言）"
            }
        }
        直接输出JSON，不要markdown标记。
        """

        response = LLMClient.chat([{"role": "user", "content": prompt}], json_mode=True)
        clean_response = response.replace("```json", "").replace("```", "").strip()

        try:
            return json.loads(clean_response)
        except:
            print(f"{Fore.RED}生成失败，重试中...")
            return self.generate_case()


# --- 角色代理 (优化 Prompt) ---

class AIAgent:
    def __init__(self, name: str, role_prompt: str):
        self.name = name
        self.history = [{"role": "system", "content": role_prompt}]

    def speak(self, context_msg: str) -> str:
        self.history.append({"role": "user", "content": context_msg})
        response = LLMClient.chat(self.history)
        self.history.append({"role": "assistant", "content": response})
        return response


class Judge(AIAgent):
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
    def __init__(self, evidence_list):
        evidence_str = "\n".join([f"- {e['name']}: {e['description']}" for e in evidence_list])
        super().__init__("检察官", f"""
        你是亚内检察官风格的AI。你的目标是认定嫌疑人有罪。
        你持有的证物信息：
        {evidence_str}

        规则：
        1. 即使律师指出了矛盾，你也要强行解释（例如："那只是记忆错误！" "那只是巧合！"）。
        2. 不要编造证物列表中不存在的细节。
        3. 每句话都要充满自信和傲慢。
        4. 开头必须用"异议！" (Objection!)。
        """)


class DefenseAttorney(AIAgent):
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


# --- 庭审模拟器 (优化流程控制) ---
class CourtSimulation:
    def __init__(self):
        self.designer = CaseDesigner()

    def run(self):
        case = self.designer.generate_case()

        print(f"\n{Fore.YELLOW}=== 案件信息 ===")
        print(f"标题: {case['case_title']}")
        print(f"背景: {case['background']}")
        print(f"被告: {case['suspect']}")
        print(f"真凶: {case['true_killer']}")
        print(f"证物: {[e['name'] for e in case['evidence_list']]}")
        print(f"{Fore.YELLOW}=================\n")

        input("按回车键开始庭审...")

        judge = Judge()
        prosecutor = Prosecutor(case['evidence_list'])
        lawyer = DefenseAttorney(case['evidence_list'])
        witness = Witness(
            case['witness']['name'],
            case['witness']['personality'],
            case['witness']['secret'],
            case['witness']['initial_testimony']
        )

        print(f"\n{Fore.WHITE}--- 开庭 ---")
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

            # 3. 证人反应 (增加逻辑判断)
            if action_type == "指证":
                witness_breakdown_count += 1
                wit_msg = f"律师拿出了证据 {presented_evidence} 指出了你的矛盾！检察官虽然帮你说话，但这个证据很强。请试图狡辩，或者编造一个新的理由！(这是你第{witness_breakdown_count}次被拆穿)"

                # 如果被连续指证3次，强制崩溃
                if witness_breakdown_count >= 3:
                    wit_msg += " 你的逻辑已经无法自圆其说了，请表现出彻底崩溃！"
            else:
                wit_msg = f"律师在追问细节。请坚持你的说法，不要露馅。"

            witness_response = witness.speak(wit_msg)
            print(f"{Fore.CYAN}证人:{Style.RESET_ALL} {witness_response}")

            # 更新下一轮的上下文（只保留证人最新的话，让律师针对这句话攻击）
            current_context = witness_response

            # 4. 法官裁决
            # 只有当律师指证成功，且证人表现出明显崩溃词汇时，法官才判决
            judge_context = f"本回合总结：律师指出矛盾。证人回答：{witness_response}"
            if witness_breakdown_count >= 3 or ("我承认" in witness_response or "是我做的" in witness_response):
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
    if LLMClient.test_connection():
        sim = CourtSimulation()
        sim.run()
    else:
        print("连接失败，请检查 API Key")