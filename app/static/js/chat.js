class ChatApp {
    constructor() {
        this.messageHistory = [];
        this.currentEventSource = null;
        this.isStreaming = false;
        this.currentAiMessageElement = null;
        
        this.initializeEventListeners();
    }
    
    initializeEventListeners() {
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');
        
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !this.isStreaming) {
                this.sendMessage();
            }
        });
        
        sendButton.addEventListener('click', () => {
            if (!this.isStreaming) {
                this.sendMessage();
            }
        });
    }
    
    async sendMessage() {
        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();
        
        if (!message || this.isStreaming) return;
        
        messageInput.value = '';
        messageInput.disabled = true;
        document.getElementById('sendButton').disabled = true;
        this.isStreaming = true;
        
        // Добавляем сообщение пользователя в историю
        this.messageHistory.push({ role: 'user', content: message });
        
        // Отображаем сообщение пользователя
        this.addMessage('user', message);
        
        // Создаем новый элемент для ответа AI
        this.currentAiMessageElement = this.addMessage('assistant', '');
        this.currentAiMessageElement.innerHTML = '<span class="typing-indicator">AI печатает...</span>';
        
        try {
            // Останавливаем предыдущий стрим, если он есть
            if (this.currentEventSource) {
                this.currentEventSource.close();
            }
            
            const response = await fetch('/api/chat/stream', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    messages: this.messageHistory,
                    model: 'gpt-3.5-turbo',
                    max_tokens: 1000,
                    temperature: 0.7
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            this.currentEventSource = this.createEventSource(response.body);
            this.fullResponse = '';
            
        } catch (error) {
            console.error('Error:', error);
            this.addMessage('assistant', `Ошибка: ${error.message}`);
            this.resetInput();
        }
    }
    
    createEventSource(readableStream) {
        const reader = readableStream.getReader();
        const decoder = new TextDecoder();
        
        const processStream = async () => {
            try {
                while (true) {
                    const { done, value } = await reader.read();
                    
                    if (done) {
                        // Сохраняем полный ответ в историю
                        if (this.fullResponse) {
                            this.messageHistory.push({ role: 'assistant', content: this.fullResponse });
                        }
                        this.resetInput();
                        break;
                    }
                    
                    const chunk = decoder.decode(value);
                    const lines = chunk.split('\n\n');
                    
                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            try {
                                const data = JSON.parse(line.substring(6));
                                
                                if (data.is_final) {
                                    continue;
                                }
                                
                                this.fullResponse += data.content;
                                
                                // Обновляем отображение текущего сообщения AI
                                if (this.currentAiMessageElement) {
                                    this.currentAiMessageElement.innerHTML = '';
                                    const responseSpan = document.createElement('span');
                                    responseSpan.textContent = this.fullResponse;
                                    this.currentAiMessageElement.appendChild(responseSpan);
                                }
                                
                                // Автопрокрутка
                                this.scrollToBottom();
                                
                            } catch (e) {
                                console.warn('Failed to parse SSE message:', e);
                            }
                        }
                    }
                }
            } catch (error) {
                console.error('Stream error:', error);
                this.resetInput();
            }
        };
        
        processStream();
        return { close: () => reader.cancel() };
    }
    
    addMessage(role, content) {
        const chatContainer = document.getElementById('chatContainer');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}-message`;
        
        if (content) {
            const contentSpan = document.createElement('span');
            contentSpan.textContent = content;
            messageDiv.appendChild(contentSpan);
        }
        
        chatContainer.appendChild(messageDiv);
        this.scrollToBottom();
        
        return messageDiv;
    }
    
    scrollToBottom() {
        const chatContainer = document.getElementById('chatContainer');
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    resetInput() {
        document.getElementById('messageInput').disabled = false;
        document.getElementById('sendButton').disabled = false;
        document.getElementById('messageInput').focus();
        this.isStreaming = false;
        this.currentEventSource = null;
        this.currentAiMessageElement = null;
        this.fullResponse = '';
    }
    
    handleKeyPress(event) {
        if (event.key === 'Enter' && !this.isStreaming) {
            this.sendMessage();
        }
    }
}

// Инициализация приложения
const chatApp = new ChatApp();

// Глобальные функции для HTML onclick
function sendMessage() {
    chatApp.sendMessage();
}

function handleKeyPress(event) {
    chatApp.handleKeyPress(event);
}