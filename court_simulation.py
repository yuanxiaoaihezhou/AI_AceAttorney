"""
Court Simulation Module
法庭模拟的核心逻辑
"""

import time
import re
from typing import Dict, Any, List
from colorama import Fore, Style

from case_designer import CaseDesigner
from investigation import InvestigationPhase
from agents import Judge, Prosecutor, DefenseAttorney, Witness
from config import (
    MAX_ROUNDS,
    WITNESS_BREAKDOWN_THRESHOLD,
    DEBUG_MODE
)


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
