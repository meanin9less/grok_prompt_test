<script setup>
import { computed, nextTick, ref, watch } from 'vue'
import { useChat } from '../composables/useChat'
import { useChatMarkdown } from '../composables/useChatMarkdown'

const props = defineProps({
  apiPath: {
    type: [String, Object],
    default: '/api/grok/prompt-chat'
  },
  selectedModel: {
    type: String,
    default: null
  },
  systemPrompt: {
    type: Object,
    default: null
  },
  inputPrompt: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['stream-state-change'])

const headerCompareOpen = ref(false)
const autoScrollEnabled = ref(true)
const selectedMessageForComparison = ref(null)

const { parseMarkdown } = useChatMarkdown()

const chat = useChat(
  () => (typeof props.apiPath === 'object' && 'value' in props.apiPath ? props.apiPath.value : props.apiPath),
  () => {},
  async () => {
    if (!autoScrollEnabled.value) return
    await nextTick()
    if (chat.messagesContainer.value) {
      chat.messagesContainer.value.scrollTop = chat.messagesContainer.value.scrollHeight
    }
  },
  props.selectedModel,
  props.systemPrompt?.id || 'system'
)

watch(
  () => chat.isLoading.value,
  (loading) => emit('stream-state-change', loading),
  { immediate: true }
)

watch(
  () => props.selectedModel,
  (model) => {
    if (chat.selectedModel) chat.selectedModel.value = model
  }
)

watch(
  () => props.systemPrompt,
  (sp) => {
    if (chat.selectedPrompt) chat.selectedPrompt.value = sp?.id || 'system'
  }
)

const headerModelName = computed(() => props.selectedModel || '모델 미선택')

const runExecution = (systemPrompt, inputPrompt) => {
  const inputText = inputPrompt?.content || ''
  // 사용자 메시지 표시 없이 직접 API 호출
  if (!inputText) return

  // 로딩 상태 변경
  chat.isLoading.value = true

  // API 호출
  const sendPromptMessage = async () => {
    try {
      const startTime = Date.now()
      const assistantMessageId = Date.now()
      const assistantMessage = {
        id: assistantMessageId,
        text: '',
        sender: 'assistant',
        timestamp: new Date(),
        responseTime: 0
      }
      chat.messages.value.push(assistantMessage)

      const { sendMessage } = await import('../services/grokApi')
      const apiPath = typeof props.apiPath === 'object' && 'value' in props.apiPath ? props.apiPath.value : props.apiPath

      await sendMessage(inputText, (chunk) => {
        const assistantMsg = chat.messages.value.find(msg => msg.id === assistantMessageId)
        if (assistantMsg) {
          assistantMsg.text += chunk
        }
      }, apiPath, [], chat.selectedModel.value, systemPrompt?.id || 'system')

      const endTime = Date.now()
      const assistantMsg = chat.messages.value.find(msg => msg.id === assistantMessageId)
      if (assistantMsg) {
        assistantMsg.responseTime = endTime - startTime
      }
    } catch (error) {
      console.error('Error sending message:', error)
      chat.messages.value.push({
        id: Date.now() + 1,
        text: `Error: ${error.message || 'Failed to get response from server'}`,
        sender: 'assistant',
        timestamp: new Date(),
        responseTime: 0
      })
    } finally {
      chat.isLoading.value = false
    }
  }

  sendPromptMessage()
}

const clearMessages = () => {
  chat.messages.value = []
}

const toggleCompareDropdown = () => {
  headerCompareOpen.value = !headerCompareOpen.value
}

defineExpose({
  runExecution
})
</script>

<template>
  <div class="response-panel">
    <header class="response-header">
      <div>
        <p class="eyebrow">3. 응답 스트리밍 + 비교</p>
        <h3>{{ headerModelName }}</h3>
        <p class="status-line">
          {{ chat.isLoading.value ? '생성 중...' : '대기 중' }}
        </p>
      </div>
      <div class="header-actions">
        <div class="dropdown" @click="toggleCompareDropdown">
          <button class="ghost-btn">비교하기 ▾</button>
          <div v-if="headerCompareOpen" class="dropdown-menu">
            <p>준비 중 기능 (다른 모델/히스토리 비교)</p>
          </div>
        </div>
        <button class="ghost-btn" @click="clearMessages" :disabled="chat.isLoading.value">Clear</button>
      </div>
    </header>

    <div class="toolbar">
      <div class="badge">Auto Scroll: {{ autoScrollEnabled ? 'ON' : 'OFF' }}</div>
      <div class="toolbar-actions">
        <button class="ghost-btn xs" @click="autoScrollEnabled = !autoScrollEnabled">토글</button>
        <button class="ghost-btn xs" @click="chat.messagesContainer.value && (chat.messagesContainer.value.scrollTop = 0)">Top</button>
        <button class="ghost-btn xs" @click="chat.messagesContainer.value && (chat.messagesContainer.value.scrollTop = chat.messagesContainer.value.scrollHeight)">Bottom</button>
      </div>
    </div>

    <div class="stream-area" :ref="(el) => (chat.messagesContainer.value = el)">
      <div v-if="chat.messages.value.length === 0" class="empty">
        응답 없음. 모델을 선택하고 실행해주세요.
      </div>
      <div
        v-for="msg in chat.messages.value"
        :key="msg.id"
        class="message"
        :class="msg.sender"
      >
        <div class="message-card">
          <div class="meta">
            <span class="tag" v-if="msg.sender === 'assistant'">Assistant</span>
            <span class="tag alt" v-else>User</span>
            <span class="time">{{ msg.timestamp.toLocaleTimeString() }}</span>
          </div>
          <div class="body">
            <div v-if="msg.sender === 'assistant'" class="markdown" v-html="parseMarkdown(msg.text)"></div>
            <pre v-else>{{ msg.text }}</pre>
          </div>
          <div class="footer" v-if="msg.sender === 'assistant'">
            <button class="mini-btn" @click="selectedMessageForComparison = msg">비교하기</button>
          </div>
        </div>
      </div>
      <div v-if="chat.isLoading.value" class="loading">
        <div class="spinner"></div>
        생성 중...
      </div>
    </div>
  </div>
</template>

<style scoped>
.response-panel {
  display: flex;
  flex-direction: column;
  flex: 1;
  height: 100%;
  min-height: 0;
  overflow: hidden;
  background: transparent;
  color: #e6ecff;
  border-radius: 0;
  border: none;
  box-shadow: none;
  box-sizing: border-box;
  min-height: 0;
}

.response-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 18px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  background: rgba(255, 255, 255, 0.02);
}

.eyebrow {
  margin: 0;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  font-size: 14px;
  color: #8fb5ff;
  font-weight: 600;
}

.response-header h3 {
  margin: 4px 0 0;
  font-size: 16px;
  font-weight: 700;
}

.status-line {
  margin: 6px 0 0;
  color: rgba(230, 236, 255, 0.65);
  font-size: 12px;
}

.header-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.ghost-btn {
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  background: rgba(255, 255, 255, 0.06);
  color: #e6ecff;
  cursor: pointer;
  font-size: 12px;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.ghost-btn:hover:not(:disabled) {
  border-color: rgba(99, 179, 255, 0.7);
  box-shadow: 0 8px 22px rgba(99, 179, 255, 0.25);
}

.ghost-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 18px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  background: rgba(255, 255, 255, 0.01);
}

.badge {
  padding: 6px 10px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.08);
  font-size: 12px;
}

.toolbar-actions {
  display: flex;
  gap: 6px;
}

.ghost-btn.xs {
  padding: 8px 10px;
  font-size: 11px;
}

.stream-area {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: rgba(255, 255, 255, 0.01);
  box-sizing: border-box;
}

.empty {
  text-align: center;
  color: rgba(230, 236, 255, 0.6);
  padding: 16px;
}

.message {
  display: flex;
}

.message-card {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  width: 100%;
  gap: 8px;
}

.meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tag {
  padding: 4px 8px;
  border-radius: 8px;
  background: rgba(99, 179, 255, 0.2);
  color: #9ce0ff;
  font-weight: 700;
  font-size: 11px;
}

.tag.alt {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.time {
  font-size: 11px;
  color: rgba(230, 236, 255, 0.7);
}

.body pre {
  margin: 0;
  white-space: pre-wrap;
  color: rgba(230, 236, 255, 0.88);
  background: rgba(0, 0, 0, 0.25);
  padding: 10px;
  border-radius: 8px;
  box-sizing: border-box;
}

.markdown {
  color: rgba(230, 236, 255, 0.88);
  width: 100%;
  word-break: break-word; /* 긴 단어 자동 줄바꿈 */
  overflow-wrap: break-word;
  box-sizing: border-box;
}
.markdown pre {
  max-width: 100%;
  overflow-x: auto; /* 코드 블록 가로 스크롤 */
  white-space: pre-wrap; /* 줄바꿈 없이 스크롤만 */
  
}
.markdown code {
  white-space: pre-wrap; /* 긴 코드 라인도 줄바꿈 */
  word-break: break-word;
}


.footer {
  display: flex;
  justify-content: flex-end;
}

.mini-btn {
  padding: 6px 8px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.06);
  color: #e6ecff;
  cursor: pointer;
}

.loading {
  display: flex;
  align-items: center;
  gap: 8px;
  color: rgba(230, 236, 255, 0.8);
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-top-color: #63b3ff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
