<script setup>
import { computed, nextTick, ref, watch } from 'vue'
import { useChatMarkdown } from '../composables/useChatMarkdown'

const props = defineProps({
  apiPath: {
    type: [String, Object],
    default: '/api/ai_hub/get_prompt_res_text'
  },
  model: {
    type: String,
    default: null
  },
  modelVersion: {
    type: [String, Object],
    default: null
  },
  inputPrompt: {
    type: Object,
    default: null // now treated as req payload
  }
})

const emit = defineEmits(['stream-state-change', 'meta-toggle'])

// 상태 관리
const runs = ref([])
const selectedRunId = ref(null)
const isLoading = ref(false)
const messagesContainer = ref(null)
const currentMessage = ref('')
const messages = ref([])
const setMessagesContainer = (el) => {
  // 방어적으로 ref null 접근을 피함
  if (!messagesContainer) return
  messagesContainer.value = el
}

const openMeta = () => {
  emit('meta-toggle', { open: true, run: selectedRun.value })
}

const closeMeta = () => {
  emit('meta-toggle', { open: false, run: selectedRun.value })
}

const { parseMarkdown } = useChatMarkdown()

const escapeHtml = (str) =>
  String(str ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\"/g, '&quot;')
    .replace(/'/g, '&#39;')

const renderMarkdownHtml = (text) => {
  const str = String(text ?? '')
  if (!str) return ''

  const html = parseMarkdown(str)
  if (html && html.trim()) return html
  return escapeHtml(str).replace(/\n/g, '<br>')
}

const STORAGE_KEY_RUNS = 'studio_response_runs'

const selectedRun = computed(() => runs.value.find((r) => r.id === selectedRunId.value) || null)

const persistRuns = () => {
  localStorage.setItem(STORAGE_KEY_RUNS, JSON.stringify(runs.value))
}

const loadRuns = () => {
  try {
    const stored = JSON.parse(localStorage.getItem(STORAGE_KEY_RUNS) || '[]')
    runs.value = Array.isArray(stored) ? stored : []
    selectedRunId.value = null
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

const buildUserPreview = (req) => (req?.user_input ? req.user_input : '')

const selectRun = (id) => {
  selectedRunId.value = id
  const run = runs.value.find((r) => r.id === id)
  if (run) {
    currentMessage.value = run.responseText || ''
  }
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const runExecution = (req, generationOptions) => {
  if (!req || !req.user_input) return

  // 새 run 생성
  const runId = Date.now().toString()
  const userPreview = buildUserPreview(req)
  const run = {
    id: runId,
    title: req.title || '이름 없는 요청',
    model: req.model || props.model || 'unknown',
    modelVersion: req.version || props.modelVersion || '모델 미선택',
    promptContent: req.prompt || '',
    inputRaw: req.user_input || '',
    inputType: 'text',
    userPreview,
    responseText: '',
    createdAt: new Date().toISOString(),
    options: generationOptions || {}
  }

  runs.value = [run, ...runs.value]
  selectedRunId.value = runId
  currentMessage.value = ''
  messages.value = []
  isLoading.value = true
  emit('stream-state-change', true)
  persistRuns()

  // 비동기로 메시지 전송
  sendMessageStream(req, run)
}

const sendMessageStream = async (req, run) => {
  try {
    const { sendMessage } = await import('../services/grokApi')
    const apiPath = typeof props.apiPath === 'object' && 'value' in props.apiPath ? props.apiPath.value : props.apiPath

    // 어시스턴트 메시지 초기화
    const assistantMessageId = Date.now()
    messages.value = [
      {
        id: assistantMessageId,
        text: '',
        sender: 'assistant',
        timestamp: new Date()
      }
    ]

    await sendMessage(req, (chunk) => {
      const strChunk = String(chunk ?? '')
      currentMessage.value = `${currentMessage.value}${strChunk}`
      // 메시지 배열 업데이트 - 실시간으로 마크다운 렌더링
      const idx = messages.value.findIndex((m) => m.id === assistantMessageId)
      if (idx !== -1) {
        const updated = { ...messages.value[idx], text: currentMessage.value }
        const clone = [...messages.value]
        clone.splice(idx, 1, updated)
        messages.value = clone
      }

      // run 데이터 업데이트
      const runIndex = runs.value.findIndex(r => r.id === run.id)
      if (runIndex !== -1) {
        runs.value[runIndex].responseText = currentMessage.value
        runs.value[runIndex].updatedAt = new Date().toISOString()
        persistRuns()
      }

      scrollToBottom()
    }, apiPath)

  } catch (error) {
    console.error('Error:', error)
    currentMessage.value = `Error: ${error.message || 'Failed to get response'}`
  } finally {
    isLoading.value = false
    emit('stream-state-change', false)
    await scrollToBottom()
  }
}

const clearMessages = () => {
  currentMessage.value = ''
  messages.value = []
}

defineExpose({
  runExecution
})

loadRuns()
watch(selectedRunId, () => {
  const run = runs.value.find((r) => r.id === selectedRunId.value)
  currentMessage.value = run?.responseText || ''
  messages.value = run?.responseText
    ? [{ id: run.id, text: run.responseText, sender: 'assistant', timestamp: new Date(run.createdAt || Date.now()) }]
    : []
})

</script>

<template>
  <div class="response-panel split">
    <div class="answer-detail combined">
      <header class="response-header">
        <div>
          <h3>{{ selectedRun?.title || 'AI 응답' }}</h3>
          <p class="status-line">
            {{ selectedRun?.modelVersion || '모델 미선택' }} · {{ isLoading ? '생성 중...' : '대기 중' }}
          </p>
        </div>
        <div class="header-actions">
          <span class="pill">{{ selectedRun?.inputType === 'form' ? '폼 입력' : '텍스트 입력' }}</span>
          <button class="ghost-btn" @click="openMeta" :disabled="!selectedRun">입력/프롬프트 보기</button>
        </div>
      </header>

      <div class="answer-body">
        <aside class="answer-list">
          <div class="answer-list-header">
            <div>
              <h3>답변 이력</h3>
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
            <div v-if="!runs.length" class="empty">답변 이력이 없습니다.</div>
          </div>
        </aside>

        <div class="stream-area" :ref="setMessagesContainer">
          <div v-if="!messages.length" class="empty">
            <div class="empty-card">
              <div class="step">
                <span class="step-badge">1</span>
                <div>
                  <p class="step-title">입력 값 설정</p>
                  <p class="step-desc">텍스트 혹은 폼을 선택·작성해 주세요.</p>
                </div>
              </div>
              <div class="step">
                <span class="step-badge">2</span>
                <div>
                  <p class="step-title">프롬프트 선택</p>
                  <p class="step-desc">좌측에서 사용할 프롬프트를 고릅니다.</p>
                </div>
              </div>
              <div class="step">
                <span class="step-badge">3</span>
                <div>
                  <p class="step-title">AI 답변 시작</p>
                  <p class="step-desc">센터의 버튼을 눌러 스트리밍을 확인하세요.</p>
                </div>
              </div>
            </div>
          </div>
          <div
            v-for="msg in messages"
            :key="`${msg.id}-${msg.text?.length || 0}`"
            class="message"
            :class="msg.sender || 'assistant'"
          >
            <div class="message-card">
              <div class="meta">
                <span class="tag" v-if="msg.sender !== 'user'">Assistant</span>
                <span class="tag alt" v-else>User</span>
                <span class="time">{{ new Date(msg.timestamp || Date.now()).toLocaleTimeString() }}</span>
              </div>
              <div class="body">
                <template v-if="msg.sender !== 'user'">
                  <div class="markdown" v-html="renderMarkdownHtml(msg.text)"></div>
                </template>
                <pre v-else class="plain-text">{{ msg.text }}</pre>
              </div>
            </div>
          </div>
          <div v-if="isLoading" class="loading">
            <div class="spinner"></div>
            생성 중...
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.response-panel.split {
  display: flex;
  flex-direction: column;
  flex: 1;
  height: 100%;
  min-height: 0;
  overflow: hidden;
  background: transparent;
  color: #e6ecff;
  gap: 12px;
  box-sizing: border-box;
}

.answer-detail {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-height: 0;
}

.answer-detail.combined {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
  padding: 0;
  min-height: 0;
  display: grid;
  grid-template-rows: auto 1fr;
}

.answer-body {
  display: grid;
  grid-template-columns: 260px 1fr;
  gap: 12px;
  padding: 0 12px 12px 12px;
  flex: 1;
  min-height: 0;
  align-items: stretch;
  box-sizing: border-box;
  overflow: hidden;
}

.answer-list {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 14px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-width: 0;
  min-height: 0;
  overflow: hidden;
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

.answer-content {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 14px;
  display: flex;
  flex-direction: column;
  min-width: 0;
  overflow: hidden;
  min-height: 0;
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
  height: 100%;
}

.empty {
  text-align: center;
  color: rgba(230, 236, 255, 0.6);
  padding: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
  min-height: 100%;
}

.empty-card {
  display: grid;
  gap: 12px;
  text-align: left;
  max-width: 520px;
  margin: 0 auto;
  background: rgba(255, 255, 255, 0.02);
  border: 1px dashed rgba(255, 255, 255, 0.12);
  border-radius: 12px;
  padding: 16px;
}

.step {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 10px;
  align-items: start;
}

.step-badge {
  width: 28px;
  height: 28px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: linear-gradient(135deg, #63b3ff, #63ffdd);
  color: #0b1221;
  font-weight: 800;
  font-size: 13px;
}

.step-title {
  margin: 0;
  font-weight: 700;
  color: #e6ecff;
}

.step-desc {
  margin: 2px 0 0;
  color: rgba(230, 236, 255, 0.7);
  font-size: 12px;
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
  white-space: pre-wrap; /* 스트리밍 중 줄바꿈 유지 */
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

.plain-text {
  white-space: pre-wrap;
  word-wrap: break-word;
  word-break: break-word;
  color: rgba(230, 236, 255, 0.88);
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
  flex-shrink: 0;
}

.drawer-backdrop {
  display: none;
}

.drawer-panel {
  display: none;
}

.drawer-header {
  display: none;
}

.drawer-body {
  display: none;
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

@keyframes slideIn {
  from {
    transform: translateX(-100%);
  }
  to {
    transform: translateX(0);
  }
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
