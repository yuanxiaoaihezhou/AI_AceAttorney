#!/usr/bin/env python3
"""
AI 逆转裁判 Web UI
基于 Flask 的 Web 界面，玩家扮演律师进行游戏
"""

import json
import uuid
import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS

from case_designer import CaseDesigner
from agents import Judge, Prosecutor, Witness
from investigation import InvestigationPhase
from llm_client import LLMClient
from config import WITNESS_BREAKDOWN_THRESHOLD, MAX_ROUNDS, DEBUG_MODE

# 配置日志
logging.basicConfig(
    level=logging.DEBUG if DEBUG_MODE else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', str(uuid.uuid4()))
CORS(app)

# 存储游戏状态
# 注意：当前使用内存存储，服务器重启后数据会丢失
# 生产环境建议使用 Redis 或数据库进行持久化存储
# TODO: 实现会话清理机制，移除超过 1 小时未活动的游戏会话
game_sessions = {}


class WebCourtGame:
    """Web 版法庭游戏控制器"""
    
    def __init__(self):
        self.case = None
        self.judge = None
        self.prosecutor = None
        self.witness = None
        self.evidence_list = []
        self.current_context = ""
        self.witness_breakdown_count = 0
        self.round_num = 0
        self.game_over = False
        self.game_result = None
        self.history = []
    
    def start_new_game(self):
        """开始新游戏"""
        logger.info("=== 开始新游戏 ===")
        designer = CaseDesigner()
        self.case = designer.generate_case()
        logger.debug(f"案件生成完成: {self.case['case_title']}")
        
        # 调查阶段收集证物
        investigation = InvestigationPhase(self.case)
        self.evidence_list = investigation.collected_evidence
        logger.debug(f"收集到 {len(self.evidence_list)} 个证物")
        
        # 初始化角色
        self.judge = Judge()
        self.prosecutor = Prosecutor(self.evidence_list)
        self.witness = Witness(
            self.case['witness']['name'],
            self.case['witness']['personality'],
            self.case['witness']['secret'],
            self.case['witness']['initial_testimony']
        )
        logger.debug(f"角色初始化完成 - 证人: {self.case['witness']['name']}")
        
        self.current_context = self.case['witness']['initial_testimony']
        self.witness_breakdown_count = 0
        self.round_num = 0
        self.game_over = False
        self.game_result = None
        
        # 添加开庭信息到历史
        self.history.append({
            'type': 'judge',
            'speaker': '法官',
            'text': f"开庭。证人 {self.case['witness']['name']}，请入庭并作证。"
        })
        
        self.history.append({
            'type': 'witness',
            'speaker': f"证人 {self.case['witness']['name']}",
            'text': self.current_context
        })
        
        logger.info("游戏初始化完成")
        return self.get_game_state()
    
    def player_action(self, action_type, evidence_name=None, question=None):
        """玩家行动（威慑或指证）"""
        if self.game_over:
            logger.warning("玩家尝试在游戏结束后行动")
            return {'error': '游戏已结束'}
        
        if self.round_num >= MAX_ROUNDS:
            logger.info("游戏超时")
            self.game_over = True
            self.game_result = 'timeout'
            return self.get_game_state()
        
        self.round_num += 1
        logger.info(f"=== 回合 {self.round_num} 开始 ===")
        
        # 玩家行动
        if action_type == 'press':
            lawyer_text = f"【威慑】{question if question else '请说清楚，这里有矛盾！'}"
            action_desc = "威慑"
            presented_evidence = "无"
            logger.debug(f"玩家威慑: {question}")
        elif action_type == 'present':
            lawyer_text = f"【指证：{evidence_name}】这个证物证明了证人说谎！"
            action_desc = "指证"
            presented_evidence = evidence_name
            logger.debug(f"玩家指证: {evidence_name}")
        else:
            logger.error(f"无效的行动类型: {action_type}")
            return {'error': '无效的行动类型'}
        
        self.history.append({
            'type': 'player',
            'speaker': '律师（您）',
            'text': lawyer_text
        })
        
        # 检察官反驳
        pros_msg = f"律师刚刚进行了{action_desc}，并说了：{lawyer_text}。请帮证人解围，反驳律师！"
        logger.debug("检察官开始反驳...")
        pros_response = self.prosecutor.speak(pros_msg)
        logger.debug(f"检察官回应: {pros_response[:100]}...")
        
        self.history.append({
            'type': 'prosecutor',
            'speaker': '检察官',
            'text': pros_response
        })
        
        # 证人反应
        if action_type == 'present':
            self.witness_breakdown_count += 1
            wit_msg = f"律师拿出了证据 {presented_evidence} 指出了你的矛盾！检察官虽然帮你说话，但这个证据很强。请试图狡辩，或者编造一个新的理由！(这是你第{self.witness_breakdown_count}次被拆穿)"
            
            if self.witness_breakdown_count >= WITNESS_BREAKDOWN_THRESHOLD:
                wit_msg += " 你的逻辑已经无法自圆其说了，请表现出彻底崩溃！"
            logger.debug(f"证人被指证次数: {self.witness_breakdown_count}")
        else:
            wit_msg = f"律师在追问细节。请坚持你的说法，不要露馅。"
        
        logger.debug("证人开始回应...")
        witness_response = self.witness.speak(wit_msg)
        logger.debug(f"证人回应: {witness_response[:100]}...")
        self.current_context = witness_response
        
        self.history.append({
            'type': 'witness',
            'speaker': f"证人 {self.case['witness']['name']}",
            'text': witness_response
        })
        
        # 法官裁决
        judge_context = f"本回合总结：律师指出矛盾。证人回答：{witness_response}"
        if self.witness_breakdown_count >= WITNESS_BREAKDOWN_THRESHOLD or ("我承认" in witness_response or "是我做的" in witness_response):
            judge_msg = f"{judge_context}。证人似乎已经承认或彻底崩溃了。请做出最后判决。"
        else:
            judge_msg = f"{judge_context}。证人还在狡辩。请要求律师继续追问，或者要求证人修正证词。不要宣判无罪。"
        
        logger.debug("法官开始裁决...")
        judge_response = self.judge.speak(judge_msg)
        logger.debug(f"法官裁决: {judge_response[:100]}...")
        
        self.history.append({
            'type': 'judge',
            'speaker': '法官',
            'text': judge_response
        })
        
        # 检查游戏是否结束
        if "无罪" in judge_response:
            logger.info("游戏结束 - 玩家胜利！")
            self.game_over = True
            self.game_result = 'win'
        
        logger.info(f"=== 回合 {self.round_num} 结束 ===")
        return self.get_game_state()
    
    def get_game_state(self):
        """获取当前游戏状态"""
        return {
            'case': {
                'title': self.case['case_title'],
                'background': self.case['background'],
                'suspect': self.case['suspect'],
                'victim': self.case.get('victim', '未知'),
                'witness_name': self.case['witness']['name']
            },
            'evidence': self.evidence_list,
            'history': self.history,
            'current_context': self.current_context,
            'round_num': self.round_num,
            'max_rounds': MAX_ROUNDS,
            'witness_breakdown_count': self.witness_breakdown_count,
            'breakdown_threshold': WITNESS_BREAKDOWN_THRESHOLD,
            'game_over': self.game_over,
            'game_result': self.game_result
        }


@app.route('/')
def index():
    """首页"""
    return render_template('index.html')


@app.route('/api/test_connection', methods=['GET'])
def test_connection():
    """测试 LLM 连接"""
    logger.info("测试 LLM 连接...")
    result = LLMClient.test_connection()
    logger.info(f"LLM 连接测试结果: {'成功' if result else '失败'}")
    return jsonify({'success': result})


@app.route('/api/new_game', methods=['POST'])
def new_game():
    """开始新游戏"""
    logger.info("收到新游戏请求")
    session_id = str(uuid.uuid4())
    game = WebCourtGame()
    
    try:
        state = game.start_new_game()
        game_sessions[session_id] = game
        logger.info(f"新游戏创建成功 - Session ID: {session_id}")
        logger.debug(f"当前活跃会话数: {len(game_sessions)}")
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'state': state
        })
    except Exception as e:
        logger.error(f"创建新游戏失败: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/action', methods=['POST'])
def player_action():
    """玩家行动"""
    data = request.json
    session_id = data.get('session_id')
    action_type = data.get('action_type')
    evidence_name = data.get('evidence_name')
    question = data.get('question')
    
    logger.info(f"收到玩家行动请求 - Session: {session_id}, 类型: {action_type}")
    if action_type == 'press':
        logger.debug(f"威慑内容: {question}")
    elif action_type == 'present':
        logger.debug(f"指证证物: {evidence_name}")
    
    if session_id not in game_sessions:
        logger.warning(f"无效的会话 ID: {session_id}")
        return jsonify({'success': False, 'error': '游戏会话不存在'}), 404
    
    game = game_sessions[session_id]
    
    try:
        state = game.player_action(action_type, evidence_name, question)
        logger.info(f"玩家行动处理完成 - 回合: {state.get('round_num', 0)}")
        return jsonify({
            'success': True,
            'state': state
        })
    except Exception as e:
        logger.error(f"处理玩家行动失败: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/game_state', methods=['GET'])
def get_game_state():
    """获取游戏状态"""
    session_id = request.args.get('session_id')
    logger.debug(f"获取游戏状态 - Session: {session_id}")
    
    if session_id not in game_sessions:
        logger.warning(f"无效的会话 ID: {session_id}")
        return jsonify({'success': False, 'error': '游戏会话不存在'}), 404
    
    game = game_sessions[session_id]
    return jsonify({
        'success': True,
        'state': game.get_game_state()
    })


def main():
    """启动 Web 服务器"""
    print("=" * 50)
    print("AI 逆转裁判 Web 版")
    print("=" * 50)
    print("\n正在启动服务器...")
    print("访问地址: http://localhost:5000")
    print("按 Ctrl+C 停止服务器\n")
    
    # 测试 LLM 连接
    logger.info("测试 LLM 连接状态...")
    if LLMClient.test_connection():
        print("✓ LLM 连接正常\n")
        logger.info("LLM 连接测试成功")
    else:
        print("✗ LLM 连接失败")
        print("提示：")
        print("  - 如果使用 Ollama，请确保服务已启动: ollama serve")
        print("  - 如果使用 SiliconFlow，请检查 API Key 是否正确")
        print("\n服务器将启动，但游戏功能将无法使用。\n")
        logger.warning("LLM 连接测试失败，但服务器将继续启动")
    
    # 从环境变量读取 debug 设置，默认为 False
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    if DEBUG_MODE:
        logger.info("调试模式已启用")
        print("⚙️ 调试模式: 已启用\n")
    
    logger.info("Flask 服务器启动中...")
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)


if __name__ == '__main__':
    main()
