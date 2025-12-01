<script setup>
import { computed, nextTick, ref, watch } from 'vue'
import { useChatMarkdown } from '../composables/useChatMarkdown'

const props = defineProps({
  apiPath: {
    type: [String, Object],
    default: '/api/chat/prompt-chat'
  },
  model: {
    type: String,
    default: null
  },
  modelVersion: {
    type: [String, Object],
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

// 상태 관리
const autoScrollEnabled = ref(true)
const runs = ref([])
const selectedRunId = ref(null)
const metaModalOpen = ref(false)
const isLoading = ref(false)
const messagesContainer = ref(null)
const currentMessage = ref('')

const { parseMarkdown } = useChatMarkdown()
const renderMarkdown = (text) => {
  try {
    return parseMarkdown(String(text ?? ''))
  } catch (err) {
    return `<div style="color: red;">Error rendering</div>`
  }
}

const STORAGE_KEY_RUNS = 'studio_response_runs'

const headerModelName = computed(() => {
  const run = runs.value.find((r) => r.id === selectedRunId.value)
  return run?.modelVersion || props.modelVersion || '모델 미선택'
})

const selectedRun = computed(() => runs.value.find((r) => r.id === selectedRunId.value) || null)

const persistRuns = () => {
  localStorage.setItem(STORAGE_KEY_RUNS, JSON.stringify(runs.value))
}

const loadRuns = () => {
  try {
    const stored = JSON.parse(localStorage.getItem(STORAGE_KEY_RUNS) || '[]')
    runs.value = Array.isArray(stored) ? stored : []
    selectedRunId.value = runs.value[0]?.id || null
  } catch (err) {
    runs.value = []
    selectedRunId.value = null
  }
}

const parseFormPayload = (content) => {
  if (!content) return []
  try {
    const parsed = JSON.parse(content)
    return Array.isArray(parsed.fields) ? parsed.fields : []
  } catch (err) {
    return []
  }
}

const buildUserPreview = (prompt) => {
  if (!prompt) return ''
  if (prompt.type === 'form') {
    const fields = parseFormPayload(prompt.content)
    if (!fields.length) return '폼 입력값 없음'
    return fields.map((f) => `${f.label || '항목'}: ${f.value || f.placeholder || ''}`).join(' · ')
  }
  return prompt.content || ''
}

const selectRun = (id) => {
  selectedRunId.value = id
  const run = runs.value.find((r) => r.id === id)
  if (run) {
    currentMessage.value = run.responseText || ''
  }
}

const scrollToBottom = async () => {
  if (!autoScrollEnabled.value) return
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const runExecution = (systemPrompt, inputPrompt, generationOptions) => {
  const inputText = inputPrompt?.content || ''
  if (!inputText) return

  // 새 run 생성
  const runId = Date.now().toString()
  const userPreview = buildUserPreview(inputPrompt)
  const run = {
    id: runId,
    title: systemPrompt?.title || inputPrompt?.title || '이름 없는 프롬프트',
    model: props.model || 'unknown',
    modelVersion: props.modelVersion || '모델 미선택',
    promptContent: systemPrompt?.content || '',
    inputRaw: inputPrompt?.content || '',
    inputType: inputPrompt?.type || 'text',
    userPreview,
    responseText: '',
    createdAt: new Date().toISOString(),
    options: generationOptions || {}
  }

  runs.value = [run, ...runs.value]
  selectedRunId.value = runId
  currentMessage.value = ''
  isLoading.value = true
  emit('stream-state-change', true)
  persistRuns()

  // 비동기로 메시지 전송
  sendMessageStream(inputText, run, systemPrompt)
}

const sendMessageStream = async (inputText, run, systemPrompt) => {
  try {
    const { sendMessage } = await import('../services/grokApi')
    const apiPath = typeof props.apiPath === 'object' && 'value' in props.apiPath ? props.apiPath.value : props.apiPath

    await sendMessage(inputText, (chunk) => {
      currentMessage.value += chunk

      // run 데이터 업데이트
      const runIndex = runs.value.findIndex(r => r.id === run.id)
      if (runIndex !== -1) {
        runs.value[runIndex].responseText = currentMessage.value
        runs.value[runIndex].updatedAt = new Date().toISOString()
        persistRuns()
      }

      scrollToBottom()
    }, apiPath, [], props.model || null, systemPrompt?.content || '', props.modelVersion || null, '')

  } catch (error) {
    console.error('Error:', error)
    currentMessage.value = `Error: ${error.message || 'Failed to get response'}`
  } finally {
    isLoading.value = false
    emit('stream-state-change', false)
  }
}

const clearMessages = () => {
  currentMessage.value = ''
}

defineExpose({
  runExecution
})

loadRuns()
watch(selectedRunId, () => {
  const run = runs.value.find((r) => r.id === selectedRunId.value)
  currentMessage.value = run?.responseText || ''
})
</script>

<template>
  <div class="response-panel split">
    <aside class="answer-list">
      <div class="answer-list-header">
        <div>
          <p class="eyebrow">답변 리스트</p>
          <h3>실행 이력</h3>
        </div>
        <button class="ghost-btn xs" @click="runs = []; persistRuns(); clearMessages()">초기화</button>
      </div>
      <div class="answer-items">
        <div
          v-for="run in runs"
          :key="run.id"
          class="answer-item"
          :class="{ active: run.id === selectedRunId }"
          @click="selectRun(run.id)"
        >
          <div class="item-titles">
            <p class="title">{{ run.title }}</p>
            <p class="subtitle">{{ run.modelVersion }}</p>
          </div>
          <p class="tiny">{{ new Date(run.createdAt).toLocaleTimeString() }}</p>
        </div>
        <div v-if="!runs.length" class="empty">실행 이력이 없습니다.</div>
      </div>
    </aside>

    <div class="answer-detail">
      <header class="response-header">
        <div>
          <p class="eyebrow">{{ selectedRun?.title || '선택된 실행 없음' }}</p>
          <h3>{{ headerModelName }}</h3>
          <p class="status-line">
            {{ isLoading ? '생성 중...' : '대기 중' }}
          </p>
        </div>
        <div class="header-actions">
          <span class="pill">{{ selectedRun?.inputType === 'form' ? '폼 입력' : '텍스트 입력' }}</span>
          <button class="ghost-btn" @click="metaModalOpen = true" :disabled="!selectedRun">입력/프롬프트 보기</button>
          <button class="ghost-btn" @click="clearMessages" :disabled="isLoading">Clear</button>
        </div>
      </header>

      <div class="toolbar">
        <div class="badge">Auto Scroll: {{ autoScrollEnabled ? 'ON' : 'OFF' }}</div>
        <div class="toolbar-actions">
          <button class="ghost-btn xs" @click="autoScrollEnabled = !autoScrollEnabled">토글</button>
          <button class="ghost-btn xs" @click="messagesContainer && (messagesContainer.scrollTop = 0)">Top</button>
          <button class="ghost-btn xs" @click="messagesContainer && (messagesContainer.scrollTop = messagesContainer.scrollHeight)">Bottom</button>
        </div>
      </div>

      <div class="stream-area" :ref="(el) => (messagesContainer = el)">
        <div v-if="!currentMessage" class="empty">
          응답 없음. 모델을 선택하고 실행해주세요.
        </div>
        <div v-if="currentMessage" class="message assistant">
          <div class="message-card">
            <div class="meta">
              <span class="tag">Assistant</span>
              <span class="time">{{ new Date().toLocaleTimeString() }}</span>
            </div>
            <div class="body">
              <div class="markdown" v-html="renderMarkdown(currentMessage)"></div>
            </div>
          </div>
        </div>
        <div v-if="isLoading" class="loading">
          <div class="spinner"></div>
          생성 중...
        </div>
      </div>
    </div>

    <div v-if="metaModalOpen" class="modal-backdrop" @click.self="metaModalOpen = false">
      <div class="modal">
        <div class="modal-header">
          <h4>입력정보 / 프롬프트</h4>
          <button class="ghost-btn xs" @click="metaModalOpen = false">닫기</button>
        </div>
        <div class="modal-body">
          <section class="modal-section">
            <p class="eyebrow">사용된 입력</p>
            <p class="modal-text">{{ selectedRun?.userPreview || '입력정보 없음' }}</p>
          </section>
          <section class="modal-section">
            <p class="eyebrow">모델</p>
            <p class="modal-text">{{ selectedRun?.modelVersion || '모델 미선택' }}</p>
          </section>
          <section class="modal-section">
            <p class="eyebrow">프롬프트 내용</p>
            <pre class="modal-pre">{{ selectedRun?.promptContent || '프롬프트가 비어 있습니다.' }}</pre>
          </section>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.response-panel.split {
  display: flex;
  flex-direction: row;
  flex: 1;
  height: 100%;
  min-height: 0;
  overflow: hidden;
  background: transparent;
  color: #e6ecff;
  gap: 16px;
  box-sizing: border-box;
}

.answer-list {
  width: 260px;
  min-width: 220px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 14px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.answer-list-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.answer-items {
  flex: 1;
  min-height: 0;
  overflow: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.answer-item {
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.03);
  cursor: pointer;
  transition: border-color 0.2s ease, transform 0.2s ease;
}

.answer-item:hover {
  border-color: rgba(99, 179, 255, 0.7);
  transform: translateY(-2px);
}

.answer-item.active {
  border-color: rgba(99, 255, 221, 0.8);
  background: rgba(99, 255, 221, 0.08);
}

.item-titles .title {
  margin: 0;
  font-weight: 700;
}

.subtitle {
  margin: 2px 0 0;
  color: rgba(230, 236, 255, 0.7);
  font-size: 12px;
}

.tiny {
  margin: 6px 0 0;
  font-size: 11px;
  color: rgba(230, 236, 255, 0.5);
}

.answer-detail {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
  overflow: hidden;
}

.response-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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
  gap: 10px;
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
  border-radius: 8px;
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

.pill {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 12px;
  background: rgba(99, 179, 255, 0.18);
  font-size: 11px;
  color: #9ce0ff;
  font-weight: 700;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(5, 8, 18, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 30;
  padding: 20px;
  box-sizing: border-box;
}

.modal {
  width: 520px;
  max-width: 100%;
  background: rgba(14, 18, 30, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 14px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.35);
  padding: 16px;
  color: #e6ecff;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.modal-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.modal-section {
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 10px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.02);
}

.modal-text {
  margin: 4px 0 0;
  color: rgba(230, 236, 255, 0.86);
  white-space: pre-wrap;
}

.modal-pre {
  margin: 6px 0 0;
  padding: 10px;
  background: rgba(0, 0, 0, 0.35);
  border-radius: 8px;
  color: rgba(230, 236, 255, 0.86);
  white-space: pre-wrap;
  max-height: 240px;
  overflow: auto;
}

@media (max-width: 1100px) {
  .response-panel.split {
    flex-direction: column;
  }
  .answer-list {
    width: 100%;
    flex-direction: row;
    flex-wrap: wrap;
    gap: 10px;
  }
  .answer-items {
    flex-direction: row;
    flex-wrap: wrap;
  }
  .answer-item {
    width: calc(50% - 6px);
  }
}
</style>
