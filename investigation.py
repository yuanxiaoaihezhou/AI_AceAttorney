"""
Investigation Phase Module
处理庭审前的调查阶段
"""

from typing import Dict, Any, List
from colorama import Fore


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
        print(f"{Fore.GREEN}按回车键开始庭审...")
        input()
        
        # 自动收集所有证物（简化版）
        self.collected_evidence = self.case_data.get('evidence_list', [])
        print(f"{Fore.GREEN}已收集 {len(self.collected_evidence)} 件证物！")
