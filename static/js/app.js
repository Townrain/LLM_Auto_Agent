// LLM Auto Agent Web界面JavaScript

class LLMAutoAgentApp {
    constructor() {
        this.currentChatId = null;
        this.chats = this.loadChats();
        this.isProcessing = false;
        
        this.initializeEventListeners();
        this.renderChatHistory();
        this.checkAgentStatus();
    }

    // 初始化事件监听器
    initializeEventListeners() {
        // 发送消息
        const messageInput = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');
        
        messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        sendBtn.addEventListener('click', () => {
            this.sendMessage();
        });

        // 自动调整输入框高度
        messageInput.addEventListener('input', () => {
            this.autoResizeTextarea(messageInput);
        });

        // 模态框控制
        this.initializeModals();
        
        // 新对话按钮
        document.getElementById('newChatBtn').addEventListener('click', () => {
            this.createNewChat();
        });

        // 设置按钮
        document.getElementById('settingsBtn').addEventListener('click', () => {
            this.showSettingsModal();
        });

        // 导入按钮
        document.getElementById('importBtn').addEventListener('click', () => {
            this.showImportModal();
        });

        // 数据库设置切换
        document.getElementById('useDatabase').addEventListener('change', (e) => {
            this.toggleDatabaseSettings(e.target.checked);
        });
    }

    // 初始化模态框
    initializeModals() {
        // 设置模态框
        const settingsModal = document.getElementById('settingsModal');
        const settingsForm = document.getElementById('settingsForm');
        
        document.getElementById('closeSettings').addEventListener('click', () => {
            settingsModal.style.display = 'none';
        });
        
        document.getElementById('cancelSettings').addEventListener('click', () => {
            settingsModal.style.display = 'none';
        });
        
        settingsForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveSettings();
        });

        // 导入模态框
        const importModal = document.getElementById('importModal');
        const fileInput = document.getElementById('fileInput');
        const uploadArea = document.getElementById('uploadArea');
        
        document.getElementById('closeImport').addEventListener('click', () => {
            importModal.style.display = 'none';
        });
        
        document.getElementById('cancelImport').addEventListener('click', () => {
            importModal.style.display = 'none';
        });
        
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.uploadKnowledgeFile(e.target.files[0]);
            }
        });

        // 拖放上传
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            if (e.dataTransfer.files.length > 0) {
                this.uploadKnowledgeFile(e.dataTransfer.files[0]);
            }
        });

        // 命令确认模态框
        const commandModal = document.getElementById('commandModal');
        
        document.getElementById('closeCommand').addEventListener('click', () => {
            commandModal.style.display = 'none';
        });
        
        document.getElementById('cancelCommand').addEventListener('click', () => {
            commandModal.style.display = 'none';
        });
        
        document.getElementById('confirmCommand').addEventListener('click', () => {
            this.confirmCommandExecution();
        });

        // 点击模态框外部关闭
        window.addEventListener('click', (e) => {
            if (e.target === settingsModal) {
                settingsModal.style.display = 'none';
            }
            if (e.target === importModal) {
                importModal.style.display = 'none';
            }
            if (e.target === commandModal) {
                commandModal.style.display = 'none';
            }
        });
    }

    // 自动调整文本区域高度
    autoResizeTextarea(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }

    // 发送消息
    async sendMessage() {
        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();
        
        if (!message || this.isProcessing) {
            return;
        }

        // 检查Agent是否初始化
        const status = await this.checkAgentStatus();
        if (!status.initialized) {
            this.showError('请先配置API Key');
            this.showSettingsModal();
            return;
        }

        this.isProcessing = true;
        messageInput.value = '';
        this.autoResizeTextarea(messageInput);
        
        // 添加用户消息
        this.addMessage('user', message);
        
        // 显示加载指示器
        this.showLoading(true);
        
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // 这里可以处理流式响应或轮询结果
                this.addMessage('assistant', result.message || '请求已接收，正在处理...');
                
                // 模拟等待结果（实际应用中应该使用WebSocket或轮询）
                setTimeout(() => {
                    this.showLoading(false);
                    this.addMessage('assistant', '这是AI的回复。在实际应用中，这里会显示真实的AI响应。');
                    this.isProcessing = false;
                }, 2000);
            } else {
                this.showError(result.error || '发送消息失败');
                this.isProcessing = false;
                this.showLoading(false);
            }
        } catch (error) {
            this.showError('网络错误: ' + error.message);
            this.isProcessing = false;
            this.showLoading(false);
        }
    }

    // 添加消息到聊天界面
    addMessage(type, content) {
        const chatMessages = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        
        const avatar = type === 'user' ? '👤' : '🤖';
        
        messageDiv.innerHTML = `
            <div class="message-avatar">${avatar}</div>
            <div class="message-content">${this.formatMessage(content)}</div>
        `;
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // 保存到当前对话
        if (this.currentChatId) {
            const chat = this.chats.find(c => c.id === this.currentChatId);
            if (chat) {
                chat.messages.push({ type, content, timestamp: new Date().toISOString() });
                this.saveChats();
            }
        }
    }

    // 格式化消息内容
    formatMessage(content) {
        // 简单的Markdown格式化
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>');
    }

    // 显示设置模态框
    showSettingsModal() {
        const modal = document.getElementById('settingsModal');
        modal.style.display = 'block';
        
        // 加载当前设置
        this.loadCurrentSettings();
    }

    // 加载当前设置
    loadCurrentSettings() {
        // 这里可以从localStorage加载保存的设置
        const savedSettings = localStorage.getItem('llm_agent_settings');
        if (savedSettings) {
            const settings = JSON.parse(savedSettings);
            document.getElementById('apiKey').value = settings.apiKey || '';
            document.getElementById('useDatabase').checked = settings.useDatabase || false;
            
            if (settings.dbConfig) {
                document.getElementById('dbHost').value = settings.dbConfig.host || 'localhost';
                document.getElementById('dbPort').value = settings.dbConfig.port || 3306;
                document.getElementById('dbUser').value = settings.dbConfig.user || 'root';
                document.getElementById('dbPassword').value = settings.dbConfig.password || '';
                document.getElementById('dbName').value = settings.dbConfig.database || 'llm_agent';
            }
            
            this.toggleDatabaseSettings(settings.useDatabase || false);
        }
    }

    // 保存设置
    async saveSettings() {
        const apiKey = document.getElementById('apiKey').value.trim();
        const useDatabase = document.getElementById('useDatabase').checked;
        
        if (!apiKey) {
            this.showError('请输入API Key');
            return;
        }

        const dbConfig = useDatabase ? {
            host: document.getElementById('dbHost').value,
            port: parseInt(document.getElementById('dbPort').value),
            user: document.getElementById('dbUser').value,
            password: document.getElementById('dbPassword').value,
            database: document.getElementById('dbName').value
        } : {};

        try {
            const response = await fetch('/api/initialize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    api_key: apiKey,
                    use_database: useDatabase,
                    db_config: dbConfig
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // 保存设置到localStorage
                const settings = { apiKey, useDatabase, dbConfig };
                localStorage.setItem('llm_agent_settings', JSON.stringify(settings));
                
                this.showSuccess('设置保存成功');
                document.getElementById('settingsModal').style.display = 'none';
            } else {
                this.showError(result.message || '初始化失败');
            }
        } catch (error) {
            this.showError('保存设置失败: ' + error.message);
        }
    }

    // 切换数据库设置显示
    toggleDatabaseSettings(show) {
        const dbSettings = document.getElementById('databaseSettings');
        dbSettings.style.display = show ? 'block' : 'none';
    }

    // 显示导入模态框
    showImportModal() {
        const modal = document.getElementById('importModal');
        modal.style.display = 'block';
    }

    // 上传知识库文件
    async uploadKnowledgeFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        const uploadProgress = document.getElementById('uploadProgress');
        const uploadArea = document.getElementById('uploadArea');
        
        uploadArea.style.display = 'none';
        uploadProgress.style.display = 'block';
        
        try {
            const response = await fetch('/api/upload_knowledge', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showSuccess(result.message);
                document.getElementById('importModal').style.display = 'none';
            } else {
                this.showError(result.error || '上传失败');
            }
        } catch (error) {
            this.showError('上传失败: ' + error.message);
        } finally {
            uploadArea.style.display = 'block';
            uploadProgress.style.display = 'none';
        }
    }

    // 显示命令确认模态框
    showCommandConfirmation(command) {
        const modal = document.getElementById('commandModal');
        const commandDisplay = document.getElementById('commandDisplay');
        
        commandDisplay.textContent = command;
        modal.style.display = 'block';
        
        // 存储当前命令用于确认
        this.pendingCommand = command;
    }

    // 确认命令执行
    async confirmCommandExecution() {
        if (!this.pendingCommand) return;
        
        try {
            const response = await fetch('/api/confirm_command', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    command: this.pendingCommand,
                    confirmed: true
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showSuccess(result.message);
            } else {
                this.showError(result.error || '命令执行失败');
            }
        } catch (error) {
            this.showError('命令执行失败: ' + error.message);
        } finally {
            document.getElementById('commandModal').style.display = 'none';
            this.pendingCommand = null;
        }
    }

    // 创建新对话
    createNewChat() {
        const chatId = 'chat_' + Date.now();
        const newChat = {
            id: chatId,
            title: '新对话',
            messages: [],
            createdAt: new Date().toISOString()
        };
        
        this.chats.unshift(newChat);
        this.currentChatId = chatId;
        this.saveChats();
        this.renderChatHistory();
        this.clearChatMessages();
        
        // 添加欢迎消息
        this.addMessage('system', '开始新的对话。您可以向我提问或请求帮助处理各种任务。');
    }

    // 清空聊天消息
    clearChatMessages() {
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.innerHTML = '';
    }

    // 渲染对话历史
    renderChatHistory() {
        const chatHistory = document.getElementById('chatHistory');
        chatHistory.innerHTML = '';
        
        this.chats.forEach(chat => {
            const chatItem = document.createElement('div');
            chatItem.className = `chat-item ${chat.id === this.currentChatId ? 'active' : ''}`;
            chatItem.textContent = chat.title;
            chatItem.addEventListener('click', () => {
                this.switchToChat(chat.id);
            });
            chatHistory.appendChild(chatItem);
        });
    }

    // 切换到指定对话
    switchToChat(chatId) {
        this.currentChatId = chatId;
        const chat = this.chats.find(c => c.id === chatId);
        
        if (chat) {
            this.clearChatMessages();
            chat.messages.forEach(msg => {
                this.addMessage(msg.type, msg.content);
            });
            this.renderChatHistory();
        }
    }

    // 加载对话历史
    loadChats() {
        const saved = localStorage.getItem('llm_agent_chats');
        if (saved) {
            return JSON.parse(saved);
        }
        
        // 默认创建一个对话
        return [{
            id: 'default_chat',
            title: '默认对话',
            messages: [],
            createdAt: new Date().toISOString()
        }];
    }

    // 保存对话历史
    saveChats() {
        localStorage.setItem('llm_agent_chats', JSON.stringify(this.chats));
    }

    // 检查Agent状态
    async checkAgentStatus() {
        try {
            const response = await fetch('/api/check_status');
            return await response.json();
        } catch (error) {
            return { initialized: false };
        }
    }

    // 显示加载指示器
    showLoading(show) {
        const loadingIndicator = document.getElementById('loadingIndicator');
        loadingIndicator.style.display = show ? 'block' : 'none';
    }

    // 显示成功消息
    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    // 显示错误消息
    showError(message) {
        this.showNotification(message, 'error');
    }

    // 显示通知
    showNotification(message, type) {
        // 简单的通知实现
        alert(`${type === 'success' ? '✅' : '❌'} ${message}`);
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    new LLMAutoAgentApp();
});