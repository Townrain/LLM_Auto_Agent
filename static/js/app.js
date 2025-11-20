// LLM Auto Agent Web 界面 JavaScript

class LLMAutoAgentWeb {
    constructor() {
        this.currentSession = {
            user_id: null,
            session_id: null,
            conversation_id: null,
            api_key: null,
            use_database: false
        };
        
        this.initializeEventListeners();
        this.loadFromLocalStorage();
    }

    initializeEventListeners() {
        // 模态框控制
        document.getElementById('settingsBtn').addEventListener('click', () => this.showModal('settingsModal'));
        document.getElementById('closeSettings').addEventListener('click', () => this.hideModal('settingsModal'));
        document.getElementById('cancelSettings').addEventListener('click', () => this.hideModal('settingsModal'));
        
        document.getElementById('importBtn').addEventListener('click', () => this.showModal('importModal'));
        document.getElementById('closeImport').addEventListener('click', () => this.hideModal('importModal'));
        document.getElementById('cancelImport').addEventListener('click', () => this.hideModal('importModal'));
        
        document.getElementById('cancelCommand').addEventListener('click', () => this.hideModal('commandModal'));
        
        // 表单提交
        document.getElementById('settingsForm').addEventListener('submit', (e) => this.handleSettingsSubmit(e));
        document.getElementById('importForm').addEventListener('submit', (e) => this.handleImportSubmit(e));
        
        // 聊天相关
        document.getElementById('sendBtn').addEventListener('click', () => this.sendMessage());
        document.getElementById('messageInput').addEventListener('keydown', (e) => this.handleInputKeydown(e));
        
        // 新对话
        document.getElementById('newChatBtn').addEventListener('click', () => this.createNewConversation());
        
        // 历史记录
        document.getElementById('historyBtn').addEventListener('click', () => this.loadConversationHistory());
        
        // 数据库设置切换
        document.getElementById('useDatabase').addEventListener('change', (e) => {
            document.getElementById('databaseSettings').style.display = e.target.checked ? 'block' : 'none';
        });
        
        // 移动端菜单
        document.getElementById('menuBtn').addEventListener('click', () => {
            document.getElementById('sidebar').classList.toggle('open');
        });
        
        // 命令确认
        document.getElementById('confirmCommand').addEventListener('click', () => this.confirmSystemCommand());
    }

    showModal(modalId) {
        document.getElementById(modalId).style.display = 'flex';
    }

    hideModal(modalId) {
        document.getElementById(modalId).style.display = 'none';
    }

    async handleSettingsSubmit(e) {
        e.preventDefault();
        
        const apiKey = document.getElementById('apiKey').value;
        const useDatabase = document.getElementById('useDatabase').checked;
        
        if (!apiKey) {
            this.showError('请输入API Key');
            return;
        }
        
        let dbConfig = null;
        if (useDatabase) {
            dbConfig = {
                host: document.getElementById('dbHost').value || 'localhost',
                port: parseInt(document.getElementById('dbPort').value) || 3306,
                user: document.getElementById('dbUser').value || 'root',
                password: document.getElementById('dbPassword').value || '',
                database: document.getElementById('dbName').value || 'llm_agent'
            };
        }
        
        try {
            this.showLoading(true);
            
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
            
            const data = await response.json();
            
            if (data.success) {
                this.currentSession = {
                    user_id: data.user_id,
                    session_id: data.session_id,
                    conversation_id: data.conversation_id,
                    api_key: apiKey,
                    use_database: useDatabase
                };
                
                this.saveToLocalStorage();
                this.enableChatInterface();
                this.hideModal('settingsModal');
                this.showSuccess('Agent初始化成功！');
                
                // 清空聊天区域，只保留欢迎消息
                this.clearChatMessages();
                
            } else {
                this.showError(data.error || '初始化失败');
            }
            
        } catch (error) {
            console.error('初始化失败:', error);
            this.showError('网络错误，请检查连接');
        } finally {
            this.showLoading(false);
        }
    }

    async handleImportSubmit(e) {
        e.preventDefault();
        
        const fileInput = document.getElementById('knowledgeFile');
        const file = fileInput.files[0];
        
        if (!file) {
            this.showError('请选择文件');
            return;
        }
        
        if (!this.currentSession.session_id) {
            this.showError('请先配置API Key');
            return;
        }
        
        const formData = new FormData();
        formData.append('file', file);
        formData.append('session_id', this.currentSession.session_id);
        
        try {
            this.showLoading(true);
            
            const response = await fetch('/api/import_knowledge', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showSuccess(data.message);
                this.hideModal('importModal');
                fileInput.value = '';
            } else {
                this.showError(data.error || '导入失败');
            }
            
        } catch (error) {
            console.error('导入失败:', error);
            this.showError('网络错误，请检查连接');
        } finally {
            this.showLoading(false);
        }
    }

    async sendMessage() {
        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();
        
        if (!message) return;
        
        if (!this.currentSession.user_id) {
            this.showError('请先配置API Key');
            return;
        }
        
        // 添加用户消息到界面
        this.addMessageToChat('user', message);
        
        // 清空输入框
        messageInput.value = '';
        this.adjustTextareaHeight(messageInput);
        
        // 禁用输入
        this.setChatInputEnabled(false);
        
        try {
            this.showLoading(true);
            
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    user_id: this.currentSession.user_id,
                    session_id: this.currentSession.session_id,
                    conversation_id: this.currentSession.conversation_id
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.addMessageToChat('assistant', data.response);
                
                // 显示推理步骤（如果有）
                if (data.reasoning_steps && data.reasoning_steps.length > 0) {
                    this.displayReasoningSteps(data.reasoning_steps);
                }
                
                // 显示工具使用情况（如果有）
                if (data.tools_used && data.tools_used.length > 0) {
                    this.displayToolsUsed(data.tools_used);
                }
                
            } else {
                this.addMessageToChat('assistant', `错误: ${data.error}`);
            }
            
        } catch (error) {
            console.error('发送消息失败:', error);
            this.addMessageToChat('assistant', '网络错误，请检查连接');
        } finally {
            this.showLoading(false);
            this.setChatInputEnabled(true);
            messageInput.focus();
        }
    }

    handleInputKeydown(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            this.sendMessage();
        }
        
        // 自动调整文本区域高度
        if (e.key === 'Enter' && e.shiftKey) {
            setTimeout(() => {
                this.adjustTextareaHeight(e.target);
            }, 0);
        }
    }

    adjustTextareaHeight(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }

    addMessageToChat(role, content) {
        const chatMessages = document.getElementById('chatMessages');
        
        // 移除欢迎消息（如果是第一条用户消息）
        const welcomeMessage = chatMessages.querySelector('.welcome-message');
        if (welcomeMessage && role === 'user') {
            welcomeMessage.remove();
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = role === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = content;
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(contentDiv);
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    displayReasoningSteps(steps) {
        const chatMessages = document.getElementById('chatMessages');
        
        const reasoningDiv = document.createElement('div');
        reasoningDiv.className = 'message assistant';
        reasoningDiv.style.opacity = '0.8';
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = '<i class="fas fa-brain"></i>';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.innerHTML = '<strong>推理过程:</strong><br>' + steps.join('<br>');
        
        reasoningDiv.appendChild(avatar);
        reasoningDiv.appendChild(contentDiv);
        
        chatMessages.appendChild(reasoningDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    displayToolsUsed(tools) {
        const chatMessages = document.getElementById('chatMessages');
        
        const toolsDiv = document.createElement('div');
        toolsDiv.className = 'message assistant';
        toolsDiv.style.opacity = '0.6';
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = '<i class="fas fa-tools"></i>';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.innerHTML = '<strong>使用的工具:</strong><br>' + tools.join(', ');
        
        toolsDiv.appendChild(avatar);
        toolsDiv.appendChild(contentDiv);
        
        chatMessages.appendChild(toolsDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    async createNewConversation() {
        if (!this.currentSession.session_id) {
            this.showError('请先配置API Key');
            return;
        }
        
        try {
            const response = await fetch('/api/new_conversation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: this.currentSession.session_id
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.currentSession.conversation_id = data.conversation_id;
                this.saveToLocalStorage();
                this.clearChatMessages();
                this.showSuccess('新对话已创建');
            } else {
                this.showError(data.error || '创建失败');
            }
            
        } catch (error) {
            console.error('创建新对话失败:', error);
            this.showError('网络错误，请检查连接');
        }
    }

    async loadConversationHistory() {
        if (!this.currentSession.session_id) {
            this.showError('请先配置API Key');
            return;
        }
        
        try {
            const response = await fetch(`/api/history?session_id=${this.currentSession.session_id}`);
            const data = await response.json();
            
            if (data.conversations) {
                this.displayConversationList(data.conversations);
            } else {
                this.showError('暂无历史记录');
            }
            
        } catch (error) {
            console.error('加载历史记录失败:', error);
            this.showError('网络错误，请检查连接');
        }
    }

    displayConversationList(conversations) {
        const conversationList = document.getElementById('conversationList');
        conversationList.innerHTML = '';
        
        conversations.forEach(conv => {
            const item = document.createElement('div');
            item.className = 'conversation-item';
            item.textContent = `对话 ${conv.conversation_id.slice(-8)}`;
            item.title = new Date(conv.last_activity).toLocaleString();
            
            item.addEventListener('click', () => {
                this.loadConversation(conv.conversation_id);
            });
            
            conversationList.appendChild(item);
        });
    }

    async loadConversation(conversationId) {
        try {
            const response = await fetch(`/api/history?session_id=${this.currentSession.session_id}&conversation_id=${conversationId}`);
            const data = await response.json();
            
            if (data.messages) {
                this.currentSession.conversation_id = conversationId;
                this.saveToLocalStorage();
                this.displayConversation(data.messages);
                this.showSuccess('对话已加载');
            }
            
        } catch (error) {
            console.error('加载对话失败:', error);
            this.showError('网络错误，请检查连接');
        }
    }

    displayConversation(messages) {
        this.clearChatMessages();
        
        messages.forEach(msg => {
            this.addMessageToChat(msg.role, msg.content);
        });
    }

    clearChatMessages() {
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.innerHTML = '';
        
        // 重新添加欢迎消息
        const welcomeDiv = document.createElement('div');
        welcomeDiv.className = 'message welcome-message';
        welcomeDiv.innerHTML = `
            <div class="message-content">
                <h3>欢迎使用 LLM Auto Agent!</h3>
                <p>开始新的对话...</p>
            </div>
        `;
        chatMessages.appendChild(welcomeDiv);
    }

    enableChatInterface() {
        document.getElementById('messageInput').disabled = false;
        document.getElementById('sendBtn').disabled = false;
    }

    setChatInputEnabled(enabled) {
        document.getElementById('messageInput').disabled = !enabled;
        document.getElementById('sendBtn').disabled = !enabled;
    }

    showLoading(show) {
        document.getElementById('loading').style.display = show ? 'flex' : 'none';
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showNotification(message, type) {
        // 简单的通知实现
        alert(`${type === 'error' ? '错误' : '成功'}: ${message}`);
    }

    requestCommandConfirmation(command) {
        return new Promise((resolve) => {
            document.getElementById('commandText').textContent = `命令: ${command}`;
            
            const confirmHandler = () => {
                this.hideModal('commandModal');
                resolve(true);
            };
            
            const cancelHandler = () => {
                this.hideModal('commandModal');
                resolve(false);
            };
            
            document.getElementById('confirmCommand').onclick = confirmHandler;
            document.getElementById('cancelCommand').onclick = cancelHandler;
            
            this.showModal('commandModal');
        });
    }

    async confirmSystemCommand() {
        // 这里可以添加系统命令确认逻辑
        // 目前只是演示
        this.hideModal('commandModal');
        this.showSuccess('命令已确认执行');
    }

    saveToLocalStorage() {
        localStorage.setItem('llm_auto_agent_session', JSON.stringify(this.currentSession));
    }

    loadFromLocalStorage() {
        const saved = localStorage.getItem('llm_auto_agent_session');
        if (saved) {
            try {
                this.currentSession = JSON.parse(saved);
                if (this.currentSession.user_id) {
                    this.enableChatInterface();
                }
            } catch (e) {
                console.error('加载保存的会话失败:', e);
            }
        }
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    new LLMAutoAgentWeb();
});