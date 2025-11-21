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
                body: JSON.stringify({ 
                    message: message,
                    conversation_id: this.currentChatId 
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // 处理AI的响应
                this.handleAIResponse(result.result);
            } else {
                this.showError(result.message || '发送消息失败');
                this.addMessage('assistant', `抱歉，处理您的请求时出现了问题：${result.message}`);
            }
        } catch (error) {
            this.showError('网络错误: ' + error.message);
            this.addMessage('assistant', '抱歉，网络连接出现问题，请稍后重试。');
        } finally {
            this.isProcessing = false;
            this.showLoading(false);
        }
    }

    // 处理AI响应
    handleAIResponse(result) {
        if (!result) {
            this.addMessage('assistant', '抱歉，没有收到有效的响应。');
            return;
        }

        // 根据响应类型处理
        if (typeof result === 'string') {
            this.addMessage('assistant', result);
        } else if (result.response) {
            // 显示最终回答
            this.addMessage('assistant', result.response);
            
            // 如果有思考过程，可以显示
            if (result.thoughts) {
                this.addMessage('system', `思考过程：${result.thoughts}`);
            }
            
            // 如果有工具调用结果
            if (result.tool_results) {
                result.tool_results.forEach(toolResult => {
                    this.addMessage('system', `工具执行：${toolResult}`);
                });
            }
        } else if (result.final_answer) {
            this.addMessage('assistant', result.final_answer);
        } else {
            // 尝试显示任何可用的文本内容
            const textResponse = JSON.stringify(result, null, 2);
            this.addMessage('assistant', textResponse);
        }
    }

    // 添加消息到聊天界面
    addMessage(type, content) {
        const chatMessages = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;
        
        const avatar = type === 'user' ? '👤' : (type === 'system' ? '⚙️' : '🤖');
        
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
        if (typeof content !== 'string') {
            content = String(content);
        }
        
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
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showSuccess(result.message);
                document.getElementById('importModal').style.display = 'none';
            } else {
                this.showError(result.message || '上传失败');
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
                this.showError(result.message || '命令执行失败');
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

    // 删除对话
    deleteChat(chatId, event) {
        event.stopPropagation(); // 阻止事件冒泡
        
        if (this.chats.length <= 1) {
            this.showError('至少需要保留一个对话');
            return;
        }
        
        if (confirm('确定要删除这个对话吗？此操作无法撤销。')) {
            // 删除对话
            this.chats = this.chats.filter(chat => chat.id !== chatId);
            
            // 如果删除的是当前对话，切换到第一个对话
            if (this.currentChatId === chatId) {
                this.currentChatId = this.chats[0]?.id || null;
                this.switchToChat(this.currentChatId);
            }
            
            this.saveChats();
            this.renderChatHistory();
            this.showSuccess('对话已删除');
        }
    }

    // 清空所有对话
    clearAllChats() {
        if (confirm('确定要清空所有对话吗？此操作无法撤销。')) {
            this.chats = [{
                id: 'default_chat',
                title: '默认对话',
                messages: [],
                createdAt: new Date().toISOString()
            }];
            this.currentChatId = 'default_chat';
            this.saveChats();
            this.renderChatHistory();
            this.clearChatMessages();
            this.showSuccess('所有对话已清空');
        }
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
        
        // 添加清空所有按钮
        if (this.chats.length > 1) {
            const clearAllBtn = document.createElement('div');
            clearAllBtn.className = 'chat-item clear-all';
            clearAllBtn.innerHTML = '🗑️ 清空所有对话';
            clearAllBtn.addEventListener('click', () => {
                this.clearAllChats();
            });
            chatHistory.appendChild(clearAllBtn);
        }
        
        this.chats.forEach(chat => {
            const chatItem = document.createElement('div');
            chatItem.className = `chat-item ${chat.id === this.currentChatId ? 'active' : ''}`;
            
            // 创建对话标题和删除按钮
            chatItem.innerHTML = `
                <div class="chat-item-content">
                    <span class="chat-title">${chat.title}</span>
                    <button class="delete-chat-btn" onclick="app.deleteChat('${chat.id}', event)">🗑️</button>
                </div>
            `;
            
            chatItem.addEventListener('click', (e) => {
                // 如果点击的是删除按钮，不切换对话
                if (!e.target.classList.contains('delete-chat-btn')) {
                    this.switchToChat(chat.id);
                }
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
            const response = await fetch('/api/health');
            const result = await response.json();
            return { 
                initialized: result.agent_initialized || false,
                status: result.status || 'unknown'
            };
        } catch (error) {
            return { initialized: false, status: 'error' };
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

// 全局应用实例
let app;

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    app = new LLMAutoAgentApp();
});