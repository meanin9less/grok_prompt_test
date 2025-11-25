<script setup>
import { ref, nextTick, watch } from 'vue'
import { sendMessage } from '../services/grokApi'

const messages = ref([])
const inputMessage = ref('')
const isLoading = ref(false)
const messagesContainer = ref(null)

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const handleSendMessage = async () => {
  const message = inputMessage.value.trim()
  if (!message) return

  
  messages.value.push({
    id: Date.now(),
    text: message,
    sender: 'user',
    timestamp: new Date(),
  })
  inputMessage.value = ''
  isLoading.value = true
  await scrollToBottom()

  try {
    
    const assistantMessageId = Date.now() + 1
    messages.value.push({
      id: assistantMessageId,
      text: '',
      sender: 'assistant',
      timestamp: new Date(),
    })
    await scrollToBottom()

    
    await sendMessage(message, (chunk) => {
      const assistantMsg = messages.value.find(msg => msg.id === assistantMessageId)
      if (assistantMsg) {
        assistantMsg.text += chunk
      }
    })
    await scrollToBottom()
  } catch (error) {
    console.error('Error sending message:', error)
    messages.value.push({
      id: Date.now() + 2,
      text: `Error: ${error.message || 'Failed to get response from server'}`,
      sender: 'assistant',
      timestamp: new Date(),
    })
  } finally {
    isLoading.value = false
    await scrollToBottom()
  }
}

const handleKeyDown = (e) => {
  if (e.key === 'Enter' && !e.shiftKey && !isLoading.value) {
    e.preventDefault()
    handleSendMessage()
  }
}

const clearChat = () => {
  messages.value = []
  inputMessage.value = ''
}

watch(messages, scrollToBottom)
</script>

<template>
  <div class="chat-window">
    <div class="chat-header">
      <h2>Chat with Grok</h2>
      <button class="clear-btn" @click="clearChat" :disabled="isLoading">
        Clear
      </button>
    </div>

    <div class="messages-container" ref="messagesContainer">
      <div v-if="messages.length === 0" class="empty-state">
        <p>No messages yet. Start a conversation!</p>
      </div>

      <div v-for="msg in messages" :key="msg.id" :class="['message', msg.sender]">
        <div class="message-bubble">
          <p>{{ msg.text }}</p>
          <span class="timestamp">{{
            msg.timestamp.toLocaleTimeString()
          }}</span>
        </div>
      </div>

      <div v-if="isLoading" class="loading-indicator">
        <div class="spinner"></div>
        <span>Grok is thinking...</span>
      </div>
    </div>

    <div class="input-area">
      <textarea
        v-model="inputMessage"
        placeholder="Type your message here... (Shift+Enter for new line)"
        class="message-input"
        :disabled="isLoading"
        @keydown="handleKeyDown"
        rows="3"
      ></textarea>
      <button
        class="send-btn"
        @click="handleSendMessage"
        :disabled="!inputMessage.trim() || isLoading"
      >
        {{ isLoading ? 'Sending...' : 'Send' }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.chat-window {
  display: flex;
  flex-direction: column;
  height: 100%;
  max-height: 600px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background-color: #007bff;
  color: white;
  border-bottom: 1px solid #ddd;
}

.chat-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.clear-btn {
  padding: 6px 12px;
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: background-color 0.3s;
}

.clear-btn:hover:not(:disabled) {
  background-color: rgba(255, 255, 255, 0.3);
}

.clear-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  background-color: #f9f9f9;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #999;
  text-align: center;
}

.message {
  display: flex;
  margin-bottom: 8px;
}

.message.user {
  justify-content: flex-end;
}

.message.assistant {
  justify-content: flex-start;
}

.message-bubble {
  max-width: 70%;
  padding: 10px 14px;
  border-radius: 8px;
  word-wrap: break-word;
  white-space: pre-wrap;
}

.message.user .message-bubble {
  background-color: #007bff;
  color: white;
}

.message.assistant .message-bubble {
  background-color: #e9ecef;
  color: #000;
}

.timestamp {
  display: block;
  font-size: 11px;
  margin-top: 4px;
  opacity: 0.7;
}

.message.user .timestamp {
  color: rgba(255, 255, 255, 0.7);
  text-align: right;
}

.message.assistant .timestamp {
  color: rgba(0, 0, 0, 0.6);
}

.loading-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  color: #666;
  font-size: 14px;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid #ddd;
  border-top-color: #007bff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.input-area {
  display: flex;
  gap: 8px;
  padding: 12px;
  border-top: 1px solid #ddd;
  background-color: #fff;
}

.message-input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: inherit;
  font-size: 14px;
  resize: none;
  transition: border-color 0.3s;
}

.message-input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.1);
}

.message-input:disabled {
  background-color: #f0f0f0;
  cursor: not-allowed;
}

.send-btn {
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  transition: background-color 0.3s;
  white-space: nowrap;
}

.send-btn:hover:not(:disabled) {
  background-color: #0056b3;
}

.send-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
</style>
