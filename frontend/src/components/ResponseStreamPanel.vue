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
    default: null // req payload
  }
})

const emit = defineEmits(['stream-state-change', 'meta-toggle'])

const runs = ref([])
const selectedRunId = ref(null)
const isLoading = ref(false)
const messagesContainer = ref(null)
const currentMessage = ref('')
const messages = ref([])
const listOpen = ref(true)

const { parseMarkdown } = useChatMarkdown()

const setMessagesContainer = (el) => {
  if (!messagesContainer) return
  messagesContainer.value = el
}

const openMeta = () => emit('meta-toggle', { open: true, run: selectedRun.value })
const closeMeta = () => emit('meta-toggle', { open: false, run: selectedRun.value })

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

const persistRuns = () => localStorage.setItem(STORAGE_KEY_RUNS, JSON.stringify(runs.value))

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

const buildUserPreview = (req) => {
  if (!req?.user_input) return ''
  if (typeof req.user_input === 'string') return req.user_input
  return req.user_input.text || ''
}

const selectRun = (id) => {
  selectedRunId.value = id
  const run = runs.value.find((r) => r.id === id)
  if (run) currentMessage.value = run.responseText || ''
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const runExecution = (req, generationOptions) => {
  if (!req || !req.user_input) return
  const runId = Date.now().toString()
  const userPreview = buildUserPreview(req)
  const run = {
    id: runId,
    title: req.title || req.user_input?.title || '이름 없는 요청',
    model: req.model || props.model || 'unknown',
    modelVersion: req.version || props.modelVersion || '모델 미선택',
    promptContent: typeof req.prompt === 'string' ? req.prompt : req.prompt?.text || '',
    inputRaw: typeof req.user_input === 'string' ? req.user_input : req.user_input?.text || '',
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
  sendMessageStream(req, run)
}

const sendMessageStream = async (req, run) => {
  try {
    const { sendMessage } = await import('../services/grokApi')
    const apiPath = typeof props.apiPath === 'object' && 'value' in props.apiPath ? props.apiPath.value : props.apiPath
    const assistantMessageId = Date.now()
    messages.value = [{ id: assistantMessageId, text: '', sender: 'assistant', timestamp: new Date() }]

    await sendMessage(req, (chunk) => {
      const strChunk = String(chunk ?? '')
      currentMessage.value = `${currentMessage.value}${strChunk}`
      const idx = messages.value.findIndex((m) => m.id === assistantMessageId)
      if (idx !== -1) {
        const updated = { ...messages.value[idx], text: currentMessage.value }
        const clone = [...messages.value]
        clone.splice(idx, 1, updated)
        messages.value = clone
      }
      const runIndex = runs.value.findIndex((r) => r.id === run.id)
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

defineExpose({ runExecution })

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
  <div class="response-panel">
    <div class="shell">
      <aside class="sidebar" :class="{ collapsed: !listOpen }">
        <div class="sidebar-header">
          <div class="header-row">
            <h3 v-if="listOpen">답변 이력</h3>
            <button class="ghost-btn xs" v-if="listOpen" @click="runs = []; persistRuns(); clearMessages()">초기화</button>
          </div>
          <button class="toggle-btn" :class="{ right: !listOpen }" @click="listOpen = !listOpen">
            {{ listOpen ? '<' : '>' }}
          </button>
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
              <span class="mini-index">{{ runs.indexOf(run) + 1 }}</span>
              <div class="item-texts">
                <p class="title">{{ run.title }}</p>
                <p class="subtitle">{{ run.modelVersion }}</p>
                <p class="tiny">{{ new Date(run.createdAt).toLocaleTimeString() }}</p>
              </div>
            </div>
          </div>
          <div v-if="!runs.length" class="empty">답변 이력이 없습니다.</div>
        </div>
      </aside>

      <section class="content">
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
      </section>
    </div>
  </div>
</template>

<style scoped>
.response-panel {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  color: #e6ecff;
}

.shell {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 10px;
  flex: 1;
  min-height: 0;
  align-items: stretch;
}

.sidebar {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 10px;
  width: 260px;
  min-width: 260px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  box-sizing: border-box;
  transition: width 0.2s ease, min-width 0.2s ease;
}

.sidebar.collapsed {
  width: 56px;
  min-width: 56px;
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: space-between;
}

.sidebar.collapsed .sidebar-header {
  justify-content: center;
}

.sidebar.collapsed .ghost-btn,
.sidebar.collapsed h3 {
  display: none;
}

.sidebar.collapsed .header-row {
  display: none;
}

.header-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.toggle-btn.right {
  margin-left: auto;
}

.answer-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 0;
  overflow: auto;
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

.item-titles {
  display: flex;
  gap: 10px;
  align-items: center;
}

.item-texts {
  display: flex;
  flex-direction: column;
  gap: 2px;
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

.mini-index {
  width: 22px;
  height: 22px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  color: #e6ecff;
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.06);
}

.sidebar.collapsed .title,
.sidebar.collapsed .subtitle,
.sidebar.collapsed .tiny {
  display: none;
}

.sidebar.collapsed .item-titles {
  justify-content: center;
}

.content {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 12px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 0;
}

.pill {
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  background: rgba(255, 255, 255, 0.08);
  color: #e6ecff;
  font-size: 12px;
}

.ghost-btn {
  padding: 8px 10px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  background: rgba(255, 255, 255, 0.06);
  color: #e6ecff;
  cursor: pointer;
  font-size: 12px;
}

.ghost-btn.xs {
  padding: 6px 8px;
  font-size: 11px;
}

.toggle-btn {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.06);
  color: #e6ecff;
  cursor: pointer;
  font-weight: 700;
  flex-shrink: 0;
}

.stream-area {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 12px;
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
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
  min-height: 100%;
}

.empty-card {
  border: 1px dashed rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
  max-width: 420px;
}

.step {
  display: grid;
  grid-template-columns: 32px 1fr;
  gap: 10px;
  align-items: center;
}

.step-badge {
  width: 32px;
  height: 32px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.06);
  font-weight: 700;
}

.step-title {
  margin: 0 0 2px 0;
  font-weight: 700;
}

.step-desc {
  margin: 0;
  color: rgba(230, 236, 255, 0.7);
  font-size: 12px;
}

.message {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.message-card {
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
}

.meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: rgba(230, 236, 255, 0.7);
  margin-bottom: 6px;
}

.tag {
  padding: 4px 8px;
  border-radius: 999px;
  background: rgba(99, 179, 255, 0.16);
  color: #cfe7ff;
}

.tag.alt {
  background: rgba(255, 255, 255, 0.12);
  color: #fff;
}

.time {
  margin-left: auto;
  font-size: 11px;
}

.markdown {
  line-height: 1.6;
  font-size: 14px;
}

.plain-text {
  margin: 0;
  white-space: pre-wrap;
  font-family: inherit;
}

.loading {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: rgba(230, 236, 255, 0.7);
}

.spinner {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 2px solid rgba(99, 179, 255, 0.35);
  border-top-color: #63b3ff;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
