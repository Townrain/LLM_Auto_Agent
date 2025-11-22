// 对话管理
let conversations = [];
let currentConversationId = null;

// 初始化
function init() {
    setupEventListeners();
    createNewConversation(); // 创建默认对话
    renderConversations();
}

// 设置事件监听器
function setupEventListeners() {
    // 侧边栏切换
    const toggleBtn = document.getElementById('toggleSidebar');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', toggleSidebar);
    }

    // 新建对话按钮
    const newChatBtn = document.getElementById('newChatBtn');
    if (newChatBtn) {
        newChatBtn.addEventListener('click', createNewConversation);
    }

    // 输入框事件
    const userInput = document.getElementById('userInput');
    if (userInput) {
        userInput.addEventListener('input', autoResizeTextarea);
        userInput.addEventListener('keydown', handleKeyPress);
    }
}

// 侧边栏切换
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const toggleIcon = document.querySelector('.toggle-icon');
    
    if (sidebar) {
        sidebar.classList.toggle('collapsed');
        // 更新图标
        if (sidebar.classList.contains('collapsed')) {
            toggleIcon.textContent = '▶';
        } else {
            toggleIcon.textContent = '◀';
        }
    }
}

// 自动调整文本区域高度
function autoResizeTextarea() {
    const textarea = this;
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 150) + 'px';
}

// 处理键盘事件
function handleKeyPress(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
}

// 创建新对话
function createNewConversation() {
    const conversationId = 'conv_' + Date.now();
    const conversation = {
        id: conversationId,
        title: '新对话',
        createdAt: new Date(),
        messages: []
    };
    
    conversations.push(conversation);
    currentConversationId = conversationId;
    renderConversations();
    clearChatMessages();
    showWelcomeMessage();
}

// 删除对话
function deleteConversation(conversationId) {
    // 确保至少有一个对话
    if (conversations.length <= 1) {
        alert('必须至少保留一个对话！');
        return;
    }
    
    conversations = conversations.filter(conv => conv.id !== conversationId);
    
    // 如果删除的是当前对话，切换到第一个对话
    if (currentConversationId === conversationId) {
        currentConversationId = conversations[0].id;
        loadConversation(currentConversationId);
    }
    
    renderConversations();
}

// 切换对话
function switchConversation(conversationId) {
    currentConversationId = conversationId;
    loadConversation(conversationId);
    renderConversations();
}

// 加载对话
function loadConversation(conversationId) {
    const conversation = conversations.find(conv => conv.id === conversationId);
    if (!conversation) return;
    
    clearChatMessages();
    
    if (conversation.messages.length === 0) {
        showWelcomeMessage();
    } else {
        conversation.messages.forEach(msg => {
            addMessage(msg.text, msg.type);
        });
    }
}

// 渲染对话列表
function renderConversations() {
    const conversationList = document.getElementById('conversationList');
    if (!conversationList) return;
    
    conversationList.innerHTML = '';
    
    conversations.forEach(conversation => {
        const conversationItem = document.createElement('div');
        conversationItem.className = `conversation-item ${conversation.id === currentConversationId ? 'active' : ''}`;
        
        const titleSpan = document.createElement('span');
        titleSpan.className = 'conversation-title';
        titleSpan.textContent = conversation.title;
        
        const timeSpan = document.createElement('span');
        timeSpan.className = 'conversation-time';
        timeSpan.textContent = formatTime(conversation.createdAt);
        
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'delete-conversation-btn';
        deleteBtn.innerHTML = '×';
        deleteBtn.title = '删除对话';
        deleteBtn.onclick = (e) => {
            e.stopPropagation();
            deleteConversation(conversation.id);
        };
        
        conversationItem.appendChild(titleSpan);
        conversationItem.appendChild(timeSpan);
        conversationItem.appendChild(deleteBtn);
        
        conversationItem.addEventListener('click', () => {
            switchConversation(conversation.id);
        });
        
        conversationList.appendChild(conversationItem);
    });
}

// 格式化时间
function formatTime(date) {
    const now = new Date();
    const diff = now - new Date(date);
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);
    
    if (minutes < 1) return '刚刚';
    if (minutes < 60) return `${minutes}分钟前`;
    if (hours < 24) return `${hours}小时前`;
    return `${days}天前`;
}

// 清空聊天消息
function clearChatMessages() {
    const messagesDiv = document.getElementById('chatMessages');
    if (messagesDiv) {
        messagesDiv.innerHTML = '';
    }
}

// 显示欢迎消息
function showWelcomeMessage() {
    const messagesDiv = document.getElementById('chatMessages');
    if (!messagesDiv) return;
    
    const welcomeDiv = document.createElement('div');
    welcomeDiv.className = 'welcome-message';
    welcomeDiv.innerHTML = `
        <h2>👋 欢迎使用 LLM Auto Agent</h2>
        <p>我是你的智能助手，可以帮你完成各种任务</p>
        <div class="feature-cards">
            <div class="feature-card">
                <span class="feature-icon">🔍</span>
                <span>网络搜索</span>
            </div>
            <div class="feature-card">
                <span class="feature-icon">📝</span>
                <span>文件操作</span>
            </div>
            <div class="feature-card">
                <span class="feature-icon">💻</span>
                <span>代码执行</span>
            </div>
            <div class="feature-card">
                <span class="feature-icon">🗄️</span>
                <span>数据库查询</span>
            </div>
        </div>
    `;
    messagesDiv.appendChild(welcomeDiv);
}

// 发送消息
async function sendMessage() {
    const input = document.getElementById('userInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // 添加到当前对话
    const currentConversation = conversations.find(conv => conv.id === currentConversationId);
    if (currentConversation) {
        currentConversation.messages.push({
            text: message,
            type: 'user',
            timestamp: new Date()
        });
        
        // 更新对话标题（如果第一条消息）
        if (currentConversation.messages.length === 1) {
            currentConversation.title = message.substring(0, 20) + (message.length > 20 ? '...' : '');
            renderConversations();
        }
    }
    
    addMessage(message, 'user');
    input.value = '';
    input.style.height = 'auto';
    
    const sendBtn = document.getElementById('sendBtn');
    sendBtn.disabled = true;
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });
        
        const data = await response.json();
        
        // 添加助手回复到对话
        if (currentConversation) {
            currentConversation.messages.push({
                text: data.response,
                type: 'assistant',
                timestamp: new Date()
            });
        }
        
        addMessage(data.response, 'assistant');
    } catch (error) {
        const errorMsg = '抱歉，发生了错误：' + error.message;
        if (currentConversation) {
            currentConversation.messages.push({
                text: errorMsg,
                type: 'assistant',
                timestamp: new Date()
            });
        }
        addMessage(errorMsg, 'assistant');
    } finally {
        sendBtn.disabled = false;
    }
}

// 添加消息到界面
function addMessage(text, type) {
    const messagesDiv = document.getElementById('chatMessages');
    if (!messagesDiv) return;
    
    // 如果当前是欢迎消息，清除它
    const welcomeMsg = messagesDiv.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = type === 'user' ? '👤' : '🤖';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    content.textContent = text;
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);
    messagesDiv.appendChild(messageDiv);
    
    // 滚动到底部
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', init);