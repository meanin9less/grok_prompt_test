<script setup>
import { ref, nextTick, watch, defineProps, onMounted } from 'vue'
import { useChat } from '../composables/useChat'
import { useChatHistory } from '../composables/useChatHistory'
import { useChatMarkdown } from '../composables/useChatMarkdown'

const props = defineProps({
  apiPath: {
    type: String,
    default: '/api/grok/chat'
  },
  selectedModel: {
    type: String,
    default: null
  },
  selectedPrompt: {
    type: String,
    default: 'prompt'
  }
})

// Composables
const { parseMarkdown } = useChatMarkdown()
const { loadHistory, saveHistory, clearHistory } = useChatHistory(props.apiPath)

const scrollToBottom = async () => {
  await nextTick()
  if (chatState.messagesContainer.value) {
    chatState.messagesContainer.value.scrollTop = chatState.messagesContainer.value.scrollHeight
  }
}

const chatState = useChat(props.apiPath, () => saveHistory(chatState.messages), scrollToBottom, props.selectedModel, props.selectedPrompt)

// selectedModel 변경 감지
watch(() => props.selectedModel, (newModel) => {
  chatState.selectedModel.value = newModel
})

// selectedPrompt 변경 감지
watch(() => props.selectedPrompt, (newPrompt) => {
  chatState.selectedPrompt.value = newPrompt
})

// API 경로에 따른 제목 생성
const getChatTitle = () => {
  if (props.apiPath.includes('/openai/')) {
    return 'Chat with GPT'
  } else if (props.apiPath.includes('/gemini/')) {
    return 'Chat with Gemini'
  } else if (props.apiPath.includes('/grok/')) {
    return 'Chat with Grok'
  } else {
    return 'Chat'
  }
}

// 로딩 메시지
const getLoadingMessage = () => {
  if (props.apiPath.includes('/openai/')) {
    return 'GPT is thinking...'
  } else if (props.apiPath.includes('/gemini/')) {
    return 'Gemini is thinking...'
  } else if (props.apiPath.includes('/grok/')) {
    return 'Grok is thinking...'
  } else {
    return 'Thinking...'
  }
}

// apiPath 변경 감지 - 탭 전환 시 히스토리 초기화 및 재로드
watch(() => props.apiPath, () => {
  chatState.inputMessage.value = ''
  chatState.messages.value = []
  loadHistory(chatState.messages)
})

// 메시지 변경 시 자동 스크롤
watch(chatState.messages, scrollToBottom)

// 컴포넌트 마운트 시 히스토리 로드
onMounted(() => {
  loadHistory(chatState.messages)
})

const handleClearChat = () => {
  clearHistory(chatState.messages)
  chatState.inputMessage.value = ''
}

// 모델 목록
const getModelList = () => {
  if (props.apiPath.includes('/openai/')) {
    return ['gpt-5.1', 'gpt-5-mini', 'gpt-5-nano', 'gpt-5-pro', 'gpt-4.1-mini', 'gpt-4.1', 'gpt-4.1-nano', 'gpt-4o']
  } else if (props.apiPath.includes('/gemini/')) {
    return ['gemini-3-pro-preview', 'gemini-2.5-pro', 'gemini-2.5-flash', 'gemini-2.5-flash-lite', 'gemini-2.0-flash', 'gemini-2.0-flash-lite']
  } else if (props.apiPath.includes('/grok/')) {
    return ['grok-4-1-fast-reasoning', 'grok-4-1-fast-non-reasoning', 'grok-code-fast-1', 'grok-4-fast-reasoning', 'grok-4-fast-non-reasoning', 'grok-4-0709', 'grok-3-mini', 'grok-3']
  }
  return []
}

const handleModelChange = (event) => {
  chatState.selectedModel.value = event.target.value
}
</script>

<template>
  <div class="chat-window">
    <div class="chat-header">
      <h2>{{ getChatTitle() }}</h2>
      <div class="header-controls">
        <select
          :value="chatState.selectedModel.value || ''"
          @change="handleModelChange"
          class="model-select"
        >
          <option value="">Default Model</option>
          <option v-for="model in getModelList()" :key="model" :value="model">
            {{ model }}
          </option>
        </select>
        <button class="clear-btn" @click="handleClearChat" :disabled="chatState.isLoading.value">
          Clear
        </button>
      </div>
    </div>

    <div class="messages-container" ref="chatState.messagesContainer">
      <div v-if="chatState.messages.value.length === 0" class="empty-state">
        <p>No messages yet. Start a conversation!</p>
      </div>

      <div v-for="msg in chatState.messages.value" :key="msg.id" :class="['message', msg.sender]">
        <div class="message-bubble">
          <!-- 사용자 메시지는 일반 텍스트로 표시 -->
          <p v-if="msg.sender === 'user'">{{ msg.text }}</p>

          <!-- AI 응답은 마크다운으로 렌더링 -->
          <div v-else class="markdown-content" v-html="parseMarkdown(msg.text)"></div>

          <span class="timestamp">{{
            msg.timestamp.toLocaleTimeString()
          }},</span>
        </div>
      </div>

      <div v-if="chatState.isLoading.value" class="loading-indicator">
        <div class="spinner"></div>
        <span>{{ getLoadingMessage() }}</span>
      </div>
    </div>

    <div class="input-area">
      <textarea
        :ref="(el) => { chatState.textareaRef.value = el }"
        v-model="chatState.inputMessage.value"
        placeholder="Type your message here... (Shift+Enter for new line)"
        class="message-input"
        :disabled="chatState.isLoading.value"
        @keydown="chatState.handleKeyDown"
        @compositionstart="chatState.handleCompositionStart"
        @compositionend="chatState.handleCompositionEnd"
        rows="3"
      ></textarea>
      <button
        class="send-btn"
        @click="chatState.handleSendMessage"
        :disabled="!chatState.inputMessage.value.trim() || chatState.isLoading.value"
      >
        {{ chatState.isLoading.value ? 'Sending...' : 'Send' }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.chat-window {
  display: flex;
  flex-direction: column;
  flex: 1;
  height: 100%;
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
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

.header-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.model-select {
  padding: 6px 10px;
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: background-color 0.3s;
}

.model-select option {
  background-color: #fff;
  color: #333;
}

.model-select:hover {
  background-color: rgba(255, 255, 255, 0.3);
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
  min-height: 300px;
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

.markdown-content h1,
.markdown-content h2,
.markdown-content h3,
.markdown-content h4,
.markdown-content h5,
.markdown-content h6 {
  margin: 12px 0 8px 0;
  font-weight: 600;
}

.markdown-content h1 {
  font-size: 20px;
}

.markdown-content h2 {
  font-size: 18px;
}

.markdown-content h3 {
  font-size: 16px;
}

.markdown-content h4 {
  font-size: 15px;
}

.markdown-content ul,
.markdown-content ol {
  margin: 8px 0;
  padding-left: 20px;
}

.markdown-content li {
  margin: 4px 0;
  line-height: 1.5;
}

.markdown-content code {
  background-color: rgba(0, 0, 0, 0.1);
  padding: 2px 6px;
  border-radius: 3px;
  font-family: monospace;
  font-size: 13px;
}

.markdown-content pre {
  background-color: rgba(0, 0, 0, 0.15);
  padding: 10px;
  border-radius: 5px;
  overflow-x: auto;
  margin: 8px 0;
  line-height: 1.4;
}

.markdown-content pre code {
  background-color: transparent;
  padding: 0;
  font-size: 12px;
}

.markdown-content blockquote {
  border-left: 4px solid rgba(0, 0, 0, 0.2);
  margin: 8px 0;
  padding: 8px 12px;
  background-color: rgba(0, 0, 0, 0.05);
  font-style: italic;
}

.markdown-content a {
  color: #0056b3;
  text-decoration: none;
}

.markdown-content a:hover {
  text-decoration: underline;
}

.markdown-content table {
  border-collapse: collapse;
  margin: 8px 0;
  width: 100%;
}

.markdown-content table td,
.markdown-content table th {
  border: 1px solid rgba(0, 0, 0, 0.2);
  padding: 6px 8px;
  text-align: left;
}

.markdown-content table th {
  background-color: rgba(0, 0, 0, 0.1);
  font-weight: 600;
}

.markdown-content p {
  margin: 6px 0;
  line-height: 1.6;
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
  overflow: scrollHeight;
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
