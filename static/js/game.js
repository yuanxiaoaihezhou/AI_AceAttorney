/**
 * AI 逆转裁判 - 游戏逻辑
 */

let sessionId = null;
let gameState = null;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    checkConnection();
});

// 检查连接
async function checkConnection() {
    try {
        const response = await fetch('/api/test_connection');
        const data = await response.json();
        
        if (data.success) {
            showScreen('start-screen');
            document.getElementById('connection-status').innerHTML = 
                '<span style="color: #27ae60;">✓ AI 系统连接正常</span>';
        } else {
            showConnectionError();
        }
    } catch (error) {
        showConnectionError();
    }
}

function showConnectionError() {
    document.getElementById('loading-screen').innerHTML = `
        <div class="loading-content">
            <div class="logo">⚠️</div>
            <h1>连接失败</h1>
            <p>无法连接到 AI 系统</p>
            <p style="font-size: 0.9rem; opacity: 0.7; margin-top: 1rem;">
                请检查 LLM 配置是否正确<br>
                如果使用 Ollama，请确保服务已启动
            </p>
            <button class="btn btn-primary" onclick="location.reload()" style="margin-top: 2rem;">
                重试
            </button>
        </div>
    `;
}

// 显示指定屏幕
function showScreen(screenId) {
    document.querySelectorAll('.screen, .loading-screen').forEach(el => {
        el.style.display = 'none';
    });
    document.getElementById(screenId).style.display = 'flex';
}

// 开始新游戏
document.getElementById('start-btn').addEventListener('click', async function() {
    this.disabled = true;
    this.innerHTML = '正在生成案件...';
    
    try {
        const response = await fetch('/api/new_game', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            sessionId = data.session_id;
            gameState = data.state;
            initializeGame();
            showScreen('game-screen');
        } else {
            alert('生成案件失败: ' + (data.error || '未知错误'));
            this.disabled = false;
            this.innerHTML = '开始新案件';
        }
    } catch (error) {
        alert('网络错误: ' + error.message);
        this.disabled = false;
        this.innerHTML = '开始新案件';
    }
});

// 初始化游戏界面
function initializeGame() {
    // 更新案件标题
    document.getElementById('case-title').textContent = gameState.case.title;
    
    // 清空对话容器
    document.getElementById('dialogue-container').innerHTML = '';
    
    // 显示历史对话
    gameState.history.forEach(entry => {
        addDialogue(entry.speaker, entry.text, entry.type);
    });
    
    // 更新状态
    updateGameStatus();
    
    // 加载证物
    loadEvidence();
    
    // 滚动到底部
    scrollToBottom();
}

// 添加对话
function addDialogue(speaker, text, type) {
    const container = document.getElementById('dialogue-container');
    const box = document.createElement('div');
    box.className = `dialogue-box ${type}`;
    
    box.innerHTML = `
        <div class="dialogue-speaker">${getSpeakerIcon(type)} ${speaker}</div>
        <div class="dialogue-text">${text}</div>
    `;
    
    container.appendChild(box);
}

// 获取角色图标
function getSpeakerIcon(type) {
    const icons = {
        'judge': '⚖️',
        'witness': '👤',
        'player': '💼',
        'prosecutor': '🔨'
    };
    return icons[type] || '💬';
}

// 更新游戏状态
function updateGameStatus() {
    document.getElementById('round-counter').textContent = 
        `回合: ${gameState.round_num}/${gameState.max_rounds}`;
    
    // 更新压力表
    const pressure = Math.min(gameState.witness_breakdown_count, 5);
    const stars = '★'.repeat(pressure) + '☆'.repeat(5 - pressure);
    document.getElementById('pressure-meter').textContent = `压力: ${stars}`;
}

// 加载证物
function loadEvidence() {
    const list = document.getElementById('evidence-list');
    list.innerHTML = '';
    
    if (!gameState.evidence || gameState.evidence.length === 0) {
        list.innerHTML = '<p style="text-align: center; color: #999;">暂无证物</p>';
        return;
    }
    
    gameState.evidence.forEach(evidence => {
        const item = document.createElement('div');
        item.className = 'evidence-item';
        item.onclick = () => presentEvidence(evidence.name);
        
        item.innerHTML = `
            <div class="evidence-name">${evidence.name}</div>
            <div class="evidence-desc">${evidence.description}</div>
        `;
        
        list.appendChild(item);
    });
}

// 显示威慑对话框
function showPressDialog() {
    if (gameState.game_over) {
        alert('游戏已结束');
        return;
    }
    
    document.getElementById('press-modal').classList.add('show');
}

function closePressDialog() {
    document.getElementById('press-modal').classList.remove('show');
}

// 执行威慑
async function performPress(question) {
    closePressDialog();
    await performAction('press', null, question);
}

// 打开证物面板
function openEvidencePanel() {
    if (gameState.game_over) {
        alert('游戏已结束');
        return;
    }
    
    document.getElementById('evidence-panel').style.display = 'block';
}

function closeEvidencePanel() {
    document.getElementById('evidence-panel').style.display = 'none';
}

// 提出证物
async function presentEvidence(evidenceName) {
    closeEvidencePanel();
    await performAction('present', evidenceName);
}

// 执行行动
async function performAction(actionType, evidenceName = null, question = null) {
    // 禁用所有按钮
    disableActions();
    
    try {
        const response = await fetch('/api/action', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: sessionId,
                action_type: actionType,
                evidence_name: evidenceName,
                question: question
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            gameState = data.state;
            
            // 获取新的对话（跳过已显示的）
            const currentCount = document.querySelectorAll('.dialogue-box').length;
            const newDialogues = gameState.history.slice(currentCount);
            
            // 逐个显示新对话
            for (let i = 0; i < newDialogues.length; i++) {
                await sleep(500); // 延迟显示
                const entry = newDialogues[i];
                addDialogue(entry.speaker, entry.text, entry.type);
                scrollToBottom();
            }
            
            // 更新状态
            updateGameStatus();
            
            // 检查游戏是否结束
            if (gameState.game_over) {
                await sleep(1000);
                showGameResult();
            } else {
                enableActions();
            }
        } else {
            alert('操作失败: ' + (data.error || '未知错误'));
            enableActions();
        }
    } catch (error) {
        alert('网络错误: ' + error.message);
        enableActions();
    }
}

// 显示游戏结果
function showGameResult() {
    const modal = document.getElementById('result-modal');
    const content = document.getElementById('result-content');
    
    let resultHtml = '';
    
    if (gameState.game_result === 'win') {
        resultHtml = `
            <div class="result-icon">🎉</div>
            <div class="result-title result-win">胜诉！</div>
            <div class="result-message">
                恭喜！您成功揭露了真相，<br>
                被告被宣判无罪！
            </div>
        `;
    } else if (gameState.game_result === 'timeout') {
        resultHtml = `
            <div class="result-icon">⏰</div>
            <div class="result-title result-lose">休庭</div>
            <div class="result-message">
                审理超时，案件需要重新审理。<br>
                下次加油！
            </div>
        `;
    } else {
        resultHtml = `
            <div class="result-icon">❌</div>
            <div class="result-title result-lose">败诉</div>
            <div class="result-message">
                很遗憾，未能找到足够的证据。
            </div>
        `;
    }
    
    content.innerHTML = resultHtml;
    modal.classList.add('show');
}

// 显示案情信息
function showCaseInfo() {
    const modal = document.getElementById('case-modal');
    const content = document.getElementById('case-info-content');
    
    content.innerHTML = `
        <div class="case-detail">
            <h3>案件名称</h3>
            <p>${gameState.case.title}</p>
        </div>
        <div class="case-detail">
            <h3>案件背景</h3>
            <p>${gameState.case.background}</p>
        </div>
        <div class="case-detail">
            <h3>被告</h3>
            <p>${gameState.case.suspect}</p>
        </div>
        <div class="case-detail">
            <h3>受害者</h3>
            <p>${gameState.case.victim}</p>
        </div>
        <div class="case-detail">
            <h3>证人</h3>
            <p>${gameState.case.witness_name}</p>
        </div>
        <div class="case-detail">
            <h3>证物清单</h3>
            ${gameState.evidence.map(e => `
                <div style="margin-bottom: 0.75rem; padding: 0.5rem; background: #f5f5f5; border-radius: 6px;">
                    <strong>${e.name}</strong><br>
                    <span style="font-size: 0.9rem; color: #666;">${e.description}</span>
                </div>
            `).join('')}
        </div>
    `;
    
    modal.classList.add('show');
}

function closeCaseInfo() {
    document.getElementById('case-modal').classList.remove('show');
}

// 禁用/启用操作按钮
function disableActions() {
    document.querySelectorAll('.btn-action').forEach(btn => {
        btn.disabled = true;
        btn.style.opacity = '0.5';
    });
}

function enableActions() {
    document.querySelectorAll('.btn-action').forEach(btn => {
        btn.disabled = false;
        btn.style.opacity = '1';
    });
}

// 滚动到底部
function scrollToBottom() {
    const container = document.getElementById('dialogue-container');
    setTimeout(() => {
        container.scrollTop = container.scrollHeight;
    }, 100);
}

// 延迟函数
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// 点击模态框外部关闭
document.querySelectorAll('.modal').forEach(modal => {
    modal.addEventListener('click', function(e) {
        if (e.target === this) {
            this.classList.remove('show');
        }
    });
});
