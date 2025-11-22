// 侧边栏收缩功能
const sidebar = document.getElementById('sidebar');
const toggleBtn = document.getElementById('toggleSidebar');

toggleBtn.addEventListener('click', () => {
    sidebar.classList.toggle('collapsed');
});

// 自动调整输入框高度
const userInput = document.getElementById('userInput');
userInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 150) + 'px';
});

// 发送消息
async function sendMessage() {
    const input = document.getElementById('userInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // 添加用户消息到界面
    addMessage('user', message);
    
    // 清空输入框并重置高度
    input.value = '';
    input.style.height = 'auto';
    
    // 禁用发送按钮
    const sendBtn = document.getElementById('sendBtn');
    sendBtn.disabled = true;
    sendBtn.style.opacity = '0.6';
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });
        
        const data = await response.json();
        
        if (data.response) {
            addMessage('assistant', data.response);
        } else if (data.error) {
            addMessage('assistant', '错误: ' + data.error);
        }
    } catch (error) {
        addMessage('assistant', '发送消息时出错: ' + error.message);
    } finally {
        // 重新启用发送按钮
        sendBtn.disabled = false;
        sendBtn.style.opacity = '1';
    }
}

// 添加消息到聊天界面
function addMessage(role, content) {
    const chatMessages = document.getElementById('chatMessages');
    
    // 移除欢迎消息
    const welcomeMessage = chatMessages.querySelector('.welcome-message');
    if (welcomeMessage) {
        welcomeMessage.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}-message`;
    
    const avatar = role === 'user' ? '👤' : '🤖';
    const roleName = role === 'user' ? '你' : 'AI 助手';
    
    messageDiv.innerHTML = `
        <div class="message-header">
            <div class="message-avatar">${avatar}</div>
            <span class="message-role">${roleName}</span>
        </div>
        <div class="message-content">${escapeHtml(content)}</div>
    `;
    
    chatMessages.appendChild(messageDiv);
    
    // 滚动到底部
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// HTML 转义
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML.replace(/\n/g, '<br>');
}

// 键盘事件处理
function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// 更新设置
async function updateSettings() {
    const settings = {
        model_name: document.getElementById('modelName').value,
        max_steps: parseInt(document.getElementById('maxSteps').value),
        refresh_prompt_interval: parseInt(document.getElementById('refreshInterval').value),
        enable_database: document.getElementById('enableDatabase').checked,
        show_system_messages: document.getElementById('showSystemMessages').checked
    };
    
    try {
        const response = await fetch('/api/settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(settings)
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            alert('设置已更新！');
        } else {
            alert('更新设置失败: ' + data.message);
        }
    } catch (error) {
        alert('更新设置时出错: ' + error.message);
    }
}

// 上传文件
async function uploadFile() {
    const fileInput = document.getElementById('fileUpload');
    const file = fileInput.files[0];
    
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            alert('文件上传成功！');
            fileInput.value = '';
        } else {
            alert('上传失败: ' + data.message);
        }
    } catch (error) {
        alert('上传文件时出错: ' + error.message);
    }
}

// 页面加载完成后的初始化
document.addEventListener('DOMContentLoaded', () => {
    // 聚焦输入框
    document.getElementById('userInput').focus();
    
    // 加载设置
    loadSettings();
});

// 加载设置
async function loadSettings() {
    try {
        const response = await fetch('/api/settings');
        const data = await response.json();
        
        if (data.settings) {
            document.getElementById('modelName').value = data.settings.model_name || 'deepseek-chat';
            document.getElementById('maxSteps').value = data.settings.max_steps || 10;
            document.getElementById('refreshInterval').value = data.settings.refresh_prompt_interval || 3;
            document.getElementById('enableDatabase').checked = data.settings.enable_database || false;
            document.getElementById('showSystemMessages').checked = data.settings.show_system_messages || false;
        }
    } catch (error) {
        console.error('加载设置失败:', error);
    }
}