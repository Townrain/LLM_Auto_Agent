// 侧边栏收缩功能
const sidebar = document.getElementById('sidebar');
const toggleBtn = document.getElementById('toggleSidebar');

if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
    });
}

// 自动调整输入框高度
const userInput = document.getElementById('userInput');
if (userInput) {
    userInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 150) + 'px';
    });
}

// 发送消息
function sendMessage() {
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
    
    // 发送到后端
    fetch('/api/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {
        if (data.response) {
            addMessage('assistant', data.response);
        }
        if (data.error) {
            addMessage('assistant', '抱歉，发生了错误: ' + data.error);
        }
    })
    .catch(error => {
        addMessage('assistant', '抱歉，发生了错误: ' + error.message);
    })
    .finally(() => {
        sendBtn.disabled = false;
        input.focus();
    });
}

// 添加消息到聊天区域
function addMessage(role, content) {
    const chatMessages = document.getElementById('chatMessages');
    
    // 移除欢迎消息
    const welcomeMsg = chatMessages.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}-message`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = role === 'user' ? '👤' : '🤖';
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    messageContent.textContent = content;
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(messageContent);
    chatMessages.appendChild(messageDiv);
    
    // 滚动到底部
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// 键盘事件处理
function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// 更新设置
function updateSettings() {
    const settings = {
        model_name: document.getElementById('modelName').value,
        max_steps: parseInt(document.getElementById('maxSteps').value),
        refresh_prompt_interval: parseInt(document.getElementById('refreshInterval').value),
        enable_database: document.getElementById('enableDatabase').checked,
        show_system_messages: document.getElementById('showSystemMessages').checked
    };
    
    fetch('/api/settings', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(settings)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('设置已保存');
        }
    })
    .catch(error => {
        alert('保存设置失败: ' + error.message);
    });
}

// 上传文件
function uploadFile() {
    const fileInput = document.getElementById('fileUpload');
    const file = fileInput.files[0];
    
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    
    fetch('/api/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('文件上传成功');
            fileInput.value = '';
        }
    })
    .catch(error => {
        alert('文件上传失败: ' + error.message);
    });
}

// 页面加载完成后的初始化
document.addEventListener('DOMContentLoaded', () => {
    // 聚焦输入框
    const input = document.getElementById('userInput');
    if (input) {
        input.focus();
    }
});