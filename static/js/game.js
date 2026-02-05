/**
 * AI 逆转裁判 - 游戏逻辑
 */

let sessionId = null;
let gameState = null;
let selectedMode = 'fixed'; // 默认为固定选项模式

// HTML 转义函数，防止 XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

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
document.getElementById('start-btn').addEventListener('click', function() {
    // 显示模式选择屏幕
    showScreen('mode-screen');
});

// 返回开始屏幕
document.getElementById('back-to-start-btn').addEventListener('click', function() {
    showScreen('start-screen');
});

// 选择固定选项模式
document.getElementById('mode-fixed-btn').addEventListener('click', async function() {
    selectedMode = 'fixed';
    await startNewGame();
});

// 选择自由发言模式
document.getElementById('mode-free-btn').addEventListener('click', async function() {
    selectedMode = 'free';
    await startNewGame();
});

// 开始新游戏的实际逻辑
async function startNewGame() {
    // 禁用所有模式按钮
    document.getElementById('mode-fixed-btn').disabled = true;
    document.getElementById('mode-free-btn').disabled = true;
    document.getElementById('back-to-start-btn').disabled = true;
    
    // 显示加载提示
    const titleElement = document.querySelector('.game-title');
    const originalHtml = titleElement ? titleElement.textContent : '选择游戏模式';
    if (titleElement) {
        titleElement.textContent = '正在生成案件...';
    }
    
    try {
        const response = await fetch('/api/new_game', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                game_mode: selectedMode
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            sessionId = data.session_id;
            gameState = data.state;
            initializeGame();
            showScreen('game-screen');
        } else {
            alert('生成案件失败: ' + (data.error || '未知错误'));
            const titleElement = document.querySelector('.game-title');
            if (titleElement) {
                titleElement.textContent = originalHtml;
            }
            document.getElementById('mode-fixed-btn').disabled = false;
            document.getElementById('mode-free-btn').disabled = false;
            document.getElementById('back-to-start-btn').disabled = false;
        }
    } catch (error) {
        alert('网络错误: ' + error.message);
        const titleElement = document.querySelector('.game-title');
        if (titleElement) {
            titleElement.textContent = originalHtml;
        }
        document.getElementById('mode-fixed-btn').disabled = false;
        document.getElementById('mode-free-btn').disabled = false;
        document.getElementById('back-to-start-btn').disabled = false;
    }
}

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
    
    // 创建 speaker 元素
    const speakerDiv = document.createElement('div');
    speakerDiv.className = 'dialogue-speaker';
    speakerDiv.textContent = `${getSpeakerIcon(type)} ${speaker}`;
    
    // 创建 text 元素
    const textDiv = document.createElement('div');
    textDiv.className = 'dialogue-text';
    textDiv.textContent = text;
    
    box.appendChild(speakerDiv);
    box.appendChild(textDiv);
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
        const emptyMsg = document.createElement('p');
        emptyMsg.style.textAlign = 'center';
        emptyMsg.style.color = '#999';
        emptyMsg.textContent = '暂无证物';
        list.appendChild(emptyMsg);
        return;
    }
    
    gameState.evidence.forEach(evidence => {
        const item = document.createElement('div');
        item.className = 'evidence-item';
        item.onclick = () => presentEvidence(evidence.name);
        
        const nameDiv = document.createElement('div');
        nameDiv.className = 'evidence-name';
        nameDiv.textContent = evidence.name;
        
        const descDiv = document.createElement('div');
        descDiv.className = 'evidence-desc';
        descDiv.textContent = evidence.description;
        
        item.appendChild(nameDiv);
        item.appendChild(descDiv);
        list.appendChild(item);
    });
}

// 显示威慑对话框
function showPressDialog() {
    if (gameState.game_over) {
        alert('游戏已结束');
        return;
    }
    
    const modal = document.getElementById('press-modal');
    const fixedOptions = document.querySelector('.press-options');
    const customSection = document.querySelector('.custom-input-section');
    
    // 根据游戏模式显示不同的选项
    if (gameState.game_mode === 'free') {
        // 自由发言模式：隐藏固定选项，只显示自定义输入
        fixedOptions.style.display = 'none';
        customSection.style.marginTop = '0';
        const customLabel = customSection.querySelector('p');
        if (customLabel) {
            customLabel.textContent = '输入你想说的话：';
        }
    } else {
        // 固定选项模式：显示3个固定选项和自定义输入
        fixedOptions.style.display = 'block';
        customSection.style.marginTop = '1rem';
        const customLabel = customSection.querySelector('p');
        if (customLabel) {
            customLabel.textContent = '或者输入自定义内容：';
        }
    }
    
    modal.classList.add('show');
}

function closePressDialog() {
    document.getElementById('press-modal').classList.remove('show');
}

// 执行威慑
async function performPress(question) {
    closePressDialog();
    await performAction('press', null, question);
}

// 执行自定义威慑
async function performCustomPress() {
    const input = document.getElementById('custom-press-input');
    const customText = input.value.trim();
    
    if (!customText) {
        alert('请输入内容！');
        return;
    }
    
    closePressDialog();
    input.value = ''; // 清空输入框
    await performAction('press', null, customText);
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
    
    // 清空内容
    content.innerHTML = '';
    
    // 创建案件名称部分
    const titleSection = document.createElement('div');
    titleSection.className = 'case-detail';
    const titleH3 = document.createElement('h3');
    titleH3.textContent = '案件名称';
    const titleP = document.createElement('p');
    titleP.textContent = gameState.case.title;
    titleSection.appendChild(titleH3);
    titleSection.appendChild(titleP);
    content.appendChild(titleSection);
    
    // 创建案件背景部分
    const bgSection = document.createElement('div');
    bgSection.className = 'case-detail';
    const bgH3 = document.createElement('h3');
    bgH3.textContent = '案件背景';
    const bgP = document.createElement('p');
    bgP.textContent = gameState.case.background;
    bgSection.appendChild(bgH3);
    bgSection.appendChild(bgP);
    content.appendChild(bgSection);
    
    // 创建被告部分
    const suspectSection = document.createElement('div');
    suspectSection.className = 'case-detail';
    const suspectH3 = document.createElement('h3');
    suspectH3.textContent = '被告';
    const suspectP = document.createElement('p');
    suspectP.textContent = gameState.case.suspect;
    suspectSection.appendChild(suspectH3);
    suspectSection.appendChild(suspectP);
    content.appendChild(suspectSection);
    
    // 创建受害者部分
    const victimSection = document.createElement('div');
    victimSection.className = 'case-detail';
    const victimH3 = document.createElement('h3');
    victimH3.textContent = '受害者';
    const victimP = document.createElement('p');
    victimP.textContent = gameState.case.victim;
    victimSection.appendChild(victimH3);
    victimSection.appendChild(victimP);
    content.appendChild(victimSection);
    
    // 创建证人部分
    const witnessSection = document.createElement('div');
    witnessSection.className = 'case-detail';
    const witnessH3 = document.createElement('h3');
    witnessH3.textContent = '证人';
    const witnessP = document.createElement('p');
    witnessP.textContent = gameState.case.witness_name;
    witnessSection.appendChild(witnessH3);
    witnessSection.appendChild(witnessP);
    content.appendChild(witnessSection);
    
    // 创建证物清单部分
    const evidenceSection = document.createElement('div');
    evidenceSection.className = 'case-detail';
    const evidenceH3 = document.createElement('h3');
    evidenceH3.textContent = '证物清单';
    evidenceSection.appendChild(evidenceH3);
    
    gameState.evidence.forEach(e => {
        const evidenceItem = document.createElement('div');
        evidenceItem.style.marginBottom = '0.75rem';
        evidenceItem.style.padding = '0.5rem';
        evidenceItem.style.background = '#f5f5f5';
        evidenceItem.style.borderRadius = '6px';
        
        const evidenceName = document.createElement('strong');
        evidenceName.textContent = e.name;
        evidenceItem.appendChild(evidenceName);
        evidenceItem.appendChild(document.createElement('br'));
        
        const evidenceDesc = document.createElement('span');
        evidenceDesc.style.fontSize = '0.9rem';
        evidenceDesc.style.color = '#666';
        evidenceDesc.textContent = e.description;
        evidenceItem.appendChild(evidenceDesc);
        
        evidenceSection.appendChild(evidenceItem);
    });
    
    content.appendChild(evidenceSection);
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
