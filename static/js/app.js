// LLM Auto Agent Web 界面 JavaScript

class LLMAgentApp {
    constructor() {
        this.currentSession = 'default';
        this.chats = JSON.parse(localStorage.getItem('llm_agent_chats')) || [
            { id: 'default', title: '新对话', timestamp: new Date().toISOString() }
        ];
        this.settings = JSON.parse(localStorage.getItem('llm_agent_settings')) || {
            apiKey: '',
            useDatabase: false,
            database: {
                host: 'localhost',
                port: 3306,
                user: 'root',
                password: '',
                name: 'llm_agent'
            }
        };
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadChatHistory();
        this.updateUI();
    }

    bindEvents() {
        // 发送消息
        const sendBtn = document.getElementById('sendBtn');
        const userInput = document.getElementById('userInput');
        
        if (sendBtn) {
            sendBtn.addEventListener('click', () => this.sendMessage());
        }
        
        if (userInput) {
            userInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }

        // 新对话
        const newChatBtn = document.getElementById('newChatBtn');
        if (newChatBtn) {
            newChatBtn.addEventListener('click', () => this.createNewChat());
        }

        // 设置按钮
        const settingsBtn = document.getElementById('settingsBtn');
        if (settingsBtn) {
            settingsBtn.addEventListener('click', () => this.showSettings());
        }

        // 导入按钮
        const importBtn = document.getElementById('importBtn');
        if (importBtn) {
            importBtn.addEventListener('click', () => this.showImportModal());
        }

        // 模态框关闭
        const closeSettings = document.getElementById('closeSettings');
        const closeImport = document.getElementById('closeImport');
        const closeCommand = document.getElementById('closeCommand');
        
        if (closeSettings) {
            closeSettings.addEventListener('click', () => this.hideAllModals());
        }
        if (closeImport) {
            closeImport.addEventListener('click', () => this.hideAllModals());
        }
        if (closeCommand) {
            closeCommand.addEventListener('click', () => this.hideAllModals());
        }

        // 设置保存
        const settingsForm = document.getElementById('settingsForm');
        if (settingsForm) {
            settingsForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.saveSettings();
            });
        }

        // 取消按钮
        const cancelSettings = document.getElementById('cancelSettings');
        const cancelImport = document.getElementById('cancelImport');
        const cancelCommand = document.getElementById('cancelCommand');
        
        if (cancelSettings) {
            cancelSettings.addEventListener('click', () => this.hideAllModals());
        }
        if (cancelImport) {
            cancelImport.addEventListener('click', () => this.hideAllModals());
        }
        if (cancelCommand) {
            cancelCommand.addEventListener('click', () => this.hideAllModals());
        }

        // 文件上传
        const fileInput = document.getElementById('fileInput');
        if (fileInput) {
            fileInput.addEventListener('change', (e) => this.handleFileUpload(e));
        }

        // 数据库开关
        const useDatabase = document.getElementById('useDatabase');
        if (useDatabase) {
            useDatabase.addEventListener('change', (e) => {
                const dbSettings = document.getElementById('databaseSettings');
                if (dbSettings) {
                    dbSettings.style.display = e.target.checked ? 'block' : 'none';
                }
            });
        }

        // 点击模态框外部关闭
        window.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.hideAllModals();
            }
        });

        // 命令确认
        const confirmCommand = document.getElementById('confirmCommand');
        if (confirmCommand) {
            confirmCommand.addEventListener('click', () => this.executeConfirmedCommand());
        }
    }

    sendMessage() {
        const input = document.getElementById('userInput');
        const message = input ? input.value.trim() : '';
        
        if (!message) return;

        // 添加用户消息到界面
        this.addMessage('user', message);
        
        // 清空输入框
        if (input) {
            input.value = '';
        }
        
        // 显示加载状态
        const loadingId = this.showLoading();

        // 发送到后端
        fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                session_id: this.currentSession
            })
        })
        .then(response => response.json())
        .then(data => {
            this.hideLoading(loadingId);
            
            if (data.success) {
                // 显示 AI 回复
                this.addMessage('assistant', data.response);
                
                // 更新对话标题（如果是第一条消息）
                this.updateChatTitle(message);
            } else {
                this.showError(data.error || '处理消息时出错');
            }
        })
        .catch(error => {
            this.hideLoading(loadingId);
            this.showError('网络错误: ' + error.message);
        });
    }

    addMessage(role, content) {
        const chatContainer = document.getElementById('chatMessages');
        if (!chatContainer) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}-message`;
        
        const avatar = role === 'user' ? '👤' : '🤖';
        const messageClass = role === 'user' ? 'user-message-content' : 'assistant-message-content';
        
        messageDiv.innerHTML = `
            <div class="message-avatar">${avatar}</div>
            <div class="${messageClass}">${this.formatMessage(content)}</div>
        `;
        
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
        
        // 保存到本地存储
        this.saveMessageToHistory(role, content);
    }

    formatMessage(content) {
        // 简单的 Markdown 格式化
        let formatted = content
            .replace(/\\n/g, '<br>')
            .replace(/\\`\\`\\`([\\s\\S]*?)\\`\\`\\`/g, '<pre><code>$1</code></pre>')
            .replace(/\\`([^`]+)\\`/g, '<code>$1</code>')
            .replace(/\\*\\*([^*]+)\\*\\*/g, '<strong>$1</strong>')
            .replace(/\\*([^*]+)\\*/g, '<em>$1</em>');
        
        return formatted;
    }

    showLoading() {
        const chatContainer = document.getElementById('chatMessages');
        if (!chatContainer) return null;
        
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message assistant-message';
        loadingDiv.id = 'loading-message';
        
        loadingDiv.innerHTML = `
            <div class="message-avatar">🤖</div>
            <div class="assistant-message-content">
                <div class="loading-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        
        chatContainer.appendChild(loadingDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
        
        return 'loading-message';
    }

    hideLoading(loadingId) {
        if (!loadingId) return;
        const loadingElement = document.getElementById(loadingId);
        if (loadingElement) {
            loadingElement.remove();
        }
    }

    showError(message) {
        const chatContainer = document.getElementById('chatMessages');
        if (!chatContainer) return;
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'message system-message';
        
        errorDiv.innerHTML = `
            <div class="message-avatar">⚠️</div>
            <div class="system-message-content">
                <strong>错误:</strong> ${message}
            </div>
        `;
        
        chatContainer.appendChild(errorDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    createNewChat() {
        const chatId = 'chat_' + Date.now();
        const newChat = {
            id: chatId,
            title: '新对话',
            timestamp: new Date().toISOString(),
            messages: []
        };
        
        this.chats.unshift(newChat);
        this.currentSession = chatId;
        
        this.saveChats();
        this.loadChatHistory();
        this.clearChatContainer();
        
        // 更新当前对话标题
        const currentChatTitle = document.querySelector('.current-chat-title');
        if (currentChatTitle) {
            currentChatTitle.textContent = '新对话';
        }
    }

    loadChatHistory() {
        const chatList = document.getElementById('chatList');
        if (!chatList) return;
        
        chatList.innerHTML = '';
        
        // 添加清空所有对话按钮
        const clearAllItem = document.createElement('div');
        clearAllItem.className = 'chat-item clear-all';
        clearAllItem.innerHTML = `
            <span class="chat-icon">🗑️</span>
            <span class="chat-title">清空所有对话</span>
        `;
        clearAllItem.addEventListener('click', () => this.clearAllChats());
        chatList.appendChild(clearAllItem);
        
        this.chats.forEach(chat => {
            const chatItem = document.createElement('div');
            chatItem.className = `chat-item ${chat.id === this.currentSession ? 'active' : ''}`;
            chatItem.innerHTML = `
                <span class="chat-title">${chat.title}</span>
                <button class="delete-chat-btn" onclick="app.deleteChat('${chat.id}')">🗑️</button>
            `;
            
            chatItem.addEventListener('click', (e) => {
                if (!e.target.classList.contains('delete-chat-btn')) {
                    this.switchChat(chat.id);
                }
            });
            
            chatList.appendChild(chatItem);
        });
    }

    switchChat(chatId) {
        this.currentSession = chatId;
        this.loadChatHistory();
        this.clearChatContainer();
        
        // 加载对话消息
        const chat = this.chats.find(c => c.id === chatId);
        if (chat && chat.messages) {
            chat.messages.forEach(msg => {
                this.addMessage(msg.role, msg.content);
            });
        }
        
        // 更新当前对话标题
        const currentChatTitle = document.querySelector('.current-chat-title');
        if (currentChatTitle && chat) {
            currentChatTitle.textContent = chat.title;
        }
    }

    deleteChat(chatId) {
        if (this.chats.length <= 1) {
            alert('至少需要保留一个对话');
            return;
        }
        
        if (confirm('确定要删除这个对话吗？')) {
            this.chats = this.chats.filter(chat => chat.id !== chatId);
            
            if (this.currentSession === chatId) {
                this.currentSession = this.chats[0].id;
            }
            
            this.saveChats();
            this.loadChatHistory();
            
            if (this.currentSession === chatId) {
                this.switchChat(this.currentSession);
            }
        }
    }

    clearAllChats() {
        if (confirm('确定要清空所有对话吗？此操作不可撤销。')) {
            this.chats = [
                { id: 'default', title: '新对话', timestamp: new Date().toISOString(), messages: [] }
            ];
            this.currentSession = 'default';
            
            this.saveChats();
            this.loadChatHistory();
            this.clearChatContainer();
            
            const currentChatTitle = document.querySelector('.current-chat-title');
            if (currentChatTitle) {
                currentChatTitle.textContent = '新对话';
            }
        }
    }

    clearChatContainer() {
        const chatContainer = document.getElementById('chatMessages');
        if (chatContainer) {
            chatContainer.innerHTML = '';
        }
    }

    updateChatTitle(firstMessage) {
        const currentChat = this.chats.find(chat => chat.id === this.currentSession);
        if (currentChat && currentChat.title === '新对话') {
            // 使用第一条消息的前20个字符作为标题
            const title = firstMessage.length > 20 ? firstMessage.substring(0, 20) + '...' : firstMessage;
            currentChat.title = title;
            this.saveChats();
            this.loadChatHistory();
            
            const currentChatTitle = document.querySelector('.current-chat-title');
            if (currentChatTitle) {
                currentChatTitle.textContent = title;
            }
        }
    }

    saveMessageToHistory(role, content) {
        const currentChat = this.chats.find(chat => chat.id === this.currentSession);
        if (currentChat) {
            if (!currentChat.messages) {
                currentChat.messages = [];
            }
            currentChat.messages.push({
                role: role,
                content: content,
                timestamp: new Date().toISOString()
            });
            this.saveChats();
        }
    }

    saveChats() {
        localStorage.setItem('llm_agent_chats', JSON.stringify(this.chats));
    }

    showSettings() {
        const settingsModal = document.getElementById('settingsModal');
        if (!settingsModal) return;
        
        // 填充设置表单
        const apiKey = document.getElementById('apiKey');
        const useDatabase = document.getElementById('useDatabase');
        const dbHost = document.getElementById('dbHost');
        const dbPort = document.getElementById('dbPort');
        const dbUser = document.getElementById('dbUser');
        const dbPassword = document.getElementById('dbPassword');
        const dbName = document.getElementById('dbName');
        const databaseSettings = document.getElementById('databaseSettings');
        
        if (apiKey) apiKey.value = this.settings.apiKey || '';
        if (useDatabase) useDatabase.checked = this.settings.useDatabase || false;
        
        if (this.settings.database) {
            if (dbHost) dbHost.value = this.settings.database.host || 'localhost';
            if (dbPort) dbPort.value = this.settings.database.port || 3306;
            if (dbUser) dbUser.value = this.settings.database.user || 'root';
            if (dbPassword) dbPassword.value = this.settings.database.password || '';
            if (dbName) dbName.value = this.settings.database.name || 'llm_agent';
        }
        
        if (databaseSettings) {
            databaseSettings.style.display = this.settings.useDatabase ? 'block' : 'none';
        }
        
        settingsModal.style.display = 'block';
    }

    saveSettings() {
        const apiKey = document.getElementById('apiKey');
        const useDatabase = document.getElementById('useDatabase');
        const dbHost = document.getElementById('dbHost');
        const dbPort = document.getElementById('dbPort');
        const dbUser = document.getElementById('dbUser');
        const dbPassword = document.getElementById('dbPassword');
        const dbName = document.getElementById('dbName');
        
        const newSettings = {
            apiKey: apiKey ? apiKey.value : '',
            useDatabase: useDatabase ? useDatabase.checked : false,
            database: {
                host: dbHost ? dbHost.value : 'localhost',
                port: dbPort ? parseInt(dbPort.value) || 3306 : 3306,
                user: dbUser ? dbUser.value : 'root',
                password: dbPassword ? dbPassword.value : '',
                name: dbName ? dbName.value : 'llm_agent'
            }
        };
        
        // 保存到本地存储
        this.settings = newSettings;
        localStorage.setItem('llm_agent_settings', JSON.stringify(newSettings));
        
        // 发送到后端
        fetch('/api/settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(newSettings)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('设置已保存');
                this.hideAllModals();
            } else {
                alert('保存设置失败: ' + data.error);
            }
        })
        .catch(error => {
            alert('保存设置失败: ' + error.message);
        });
    }

    showImportModal() {
        const importModal = document.getElementById('importModal');
        if (importModal) {
            importModal.style.display = 'block';
        }
    }

    handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        const formData = new FormData();
        formData.append('file', file);
        
        fetch('/api/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('文件上传成功: ' + data.message);
                event.target.value = ''; // 清空文件输入
                this.hideAllModals();
            } else {
                alert('文件上传失败: ' + data.error);
            }
        })
        .catch(error => {
            alert('文件上传失败: ' + error.message);
        });
    }

    hideAllModals() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.style.display = 'none';
        });
    }

    executeConfirmedCommand() {
        // 这里处理确认执行的命令
        this.hideAllModals();
    }

    updateUI() {
        // 更新界面状态
        const userInput = document.getElementById('userInput');
        if (userInput) {
            userInput.focus();
        }
    }
}

// 初始化应用
let app;
document.addEventListener('DOMContentLoaded', function() {
    app = new LLMAgentApp();
});

// 全局函数供 HTML 调用
function deleteChat(chatId) {
    if (app) {
        app.deleteChat(chatId);
    }
}

// 命令确认函数
function confirmCommand(command) {
    return confirm(`即将执行系统命令: ${command}\n\n确定要执行吗？`);
}