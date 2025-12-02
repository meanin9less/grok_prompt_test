<script setup>
import { computed, onMounted, reactive, watch } from 'vue'

const USER_INPUT_KEY = 'user_input_texts'
const PROMPT_KEY = 'prompt_entries'

const modelFamilies = [
  {
    id: 'gpt',
    label: 'ChatGPT',
    subModels: ['gpt-5.1', 'gpt-5.1-codex', 'gpt-5-mini', 'gpt-5-nano', 'gpt-4.1', 'gpt-4.1-mini', 'gpt-4o', 'gpt-3.5-turbo']
  },
  {
    id: 'gemini',
    label: 'Gemini',
    subModels: ['gemini-3-pro-preview', 'gemini-2.5-pro', 'gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-1.5-pro']
  },
  {
    id: 'grok',
    label: 'Grok',
    subModels: ['grok-4-1-fast-reasoning', 'grok-4-1-fast-non-reasoning', 'grok-3']
  }
]

const DEFAULT_PROVIDER = 'grok'
const DEFAULT_VERSION = 'grok-4-1-fast-reasoning'

const emit = defineEmits(['update:input'])

const state = reactive({
  userInputs: [],
  prompts: [],
  selectedInputId: null,
  detailMode: 'idle', // idle | view | create | edit
  draft: { title: '', text: '', model: DEFAULT_PROVIDER, version: DEFAULT_VERSION, promptId: null },
  promptModalOpen: false,
  promptMode: 'view', // view | create | edit
  selectedPromptId: null,
  promptDraft: { title: '', text: '' }
})

const loadUserInputs = () => {
  try {
    const raw = JSON.parse(localStorage.getItem(USER_INPUT_KEY) || '[]')
    state.userInputs = Array.isArray(raw)
      ? raw.map((item) => ({
          id: item.id || Math.random().toString(36).slice(2, 11),
          title: item.title || '제목 없음',
          text: item.text || item.content || '',
          model: item.model || item.modelProvider || DEFAULT_PROVIDER,
          version: item.version || item.modelVersion || DEFAULT_VERSION,
          promptId: item.promptId || item.systemPromptId || null
        }))
      : []
  } catch (err) {
    state.userInputs = []
  }
}

const persistUserInputs = () => {
  localStorage.setItem(USER_INPUT_KEY, JSON.stringify(state.userInputs))
}

const loadPrompts = () => {
  try {
    const raw = JSON.parse(localStorage.getItem(PROMPT_KEY) || '[]')
    state.prompts = Array.isArray(raw)
      ? raw.map((p) => ({
          id: p.id || Math.random().toString(36).slice(2, 11),
          title: p.title || '제목 없음',
          text: p.text || p.content || ''
        }))
      : []
  } catch (err) {
    state.prompts = []
  }
}

const persistPrompts = () => {
  localStorage.setItem(PROMPT_KEY, JSON.stringify(state.prompts))
}

const resetDraft = () => {
  state.draft = {
    title: '',
    text: '',
    model: DEFAULT_PROVIDER,
    version: DEFAULT_VERSION,
    promptId: null
  }
}

const selectedInput = computed(() => state.userInputs.find((item) => item.id === state.selectedInputId) || null)
const selectedPrompt = computed(() => state.prompts.find((p) => p.id === state.selectedPromptId) || null)

const currentModelVersions = computed(() => {
  const family = modelFamilies.find((item) => item.id === state.draft.model)
  return family?.subModels || []
})

const viewModelVersions = computed(() => {
  const provider = selectedInput.value?.model || DEFAULT_PROVIDER
  const family = modelFamilies.find((item) => item.id === provider)
  return family?.subModels || []
})

const detailTitle = computed(() => {
  if (state.detailMode === 'create') return '입력정보 추가'
  if (state.detailMode === 'edit') return '입력정보 수정'
  if (selectedInput.value) return selectedInput.value.title
  return '입력정보를 선택하세요.'
})

const detailEyebrow = computed(() => {
  if (state.detailMode === 'create') return '새로 추가'
  if (state.detailMode === 'edit') return '수정 중'
  return ''
})

const emitReq = (input) => {
  if (!input) {
    emit('update:input', null)
    return
  }
  const promptObj = state.prompts.find((p) => p.id === input.promptId) || null
  const req = {
    req_id: input.id,
    model: input.model,
    version: input.version,
    prompt: {
      id: promptObj?.id || '',
      title: promptObj?.title || '',
      text: promptObj?.text || ''
    },
    hist: [],
    user_input: {
      id: input.id,
      title: input.title,
      text: input.text
    }
  }
  emit('update:input', req)
}

const startCreate = () => {
  state.detailMode = 'create'
  state.selectedInputId = null
  resetDraft()
  emitReq(null)
}

const selectInput = (id) => {
  state.selectedInputId = id
  state.detailMode = 'view'
  const found = state.userInputs.find((item) => item.id === id) || null
  if (found) {
    state.selectedPromptId = found.promptId || null
  }
  emitReq(found)
}

const startEdit = () => {
  if (!selectedInput.value) return
  state.detailMode = 'edit'
  state.draft = {
    title: selectedInput.value.title,
    text: selectedInput.value.text,
    model: selectedInput.value.model || DEFAULT_PROVIDER,
    version: selectedInput.value.version || DEFAULT_VERSION,
    promptId: selectedInput.value.promptId || null
  }
  state.selectedPromptId = selectedInput.value.promptId || null
}

const saveInput = () => {
  const title = state.draft.title.trim()
  const text = state.draft.text.trim()
  if (!title || !text) return

  const id =
    state.detailMode === 'edit' && selectedInput.value
      ? selectedInput.value.id
      : Math.random().toString(36).slice(2, 11)

  const payload = {
    id,
    title,
    text,
    model: state.draft.model,
    version: state.draft.version,
    promptId: state.draft.promptId || null
  }

  const existingIndex = state.userInputs.findIndex((p) => p.id === id)
  if (existingIndex >= 0) {
    state.userInputs.splice(existingIndex, 1, payload)
  } else {
    state.userInputs.unshift(payload)
  }
  persistUserInputs()
  state.selectedInputId = id
  state.detailMode = 'view'
  emitReq(payload)
}

const deleteInput = () => {
  if (!selectedInput.value) return
  if (!confirm('삭제하시겠습니까?')) return
  state.userInputs = state.userInputs.filter((p) => p.id !== selectedInput.value.id)
  persistUserInputs()
  state.selectedInputId = null
  state.detailMode = 'idle'
  emitReq(null)
}

const openPromptModal = () => {
  state.promptModalOpen = true
  if (state.prompts.length) {
    const first = state.prompts[0]
    state.selectedPromptId = first.id
    state.promptDraft = { title: first.title, text: first.text }
    state.promptMode = 'view'
  } else {
    state.selectedPromptId = null
    state.promptDraft = { title: '', text: '' }
    state.promptMode = 'create'
  }
}

const closePromptModal = () => {
  state.promptModalOpen = false
}

const selectPromptForModal = (id) => {
  const found = state.prompts.find((p) => p.id === id)
  if (!found) return
  state.selectedPromptId = id
  state.promptMode = 'view'
  state.promptDraft = { title: found.title, text: found.text }
}

const startPromptCreate = () => {
  state.promptMode = 'create'
  state.selectedPromptId = null
  state.promptDraft = { title: '', text: '' }
}

const startPromptEdit = () => {
  if (!state.selectedPromptId) return
  state.promptMode = 'edit'
}

const cancelPromptEditOrCreate = () => {
  if (state.promptMode === 'create') {
    if (state.prompts.length) {
      const first = state.prompts[0]
      state.selectedPromptId = first.id
      state.promptDraft = { title: first.title, text: first.text }
      state.promptMode = 'view'
    } else {
      state.promptDraft = { title: '', text: '' }
      state.promptMode = 'view'
    }
    return
  }
  if (state.promptMode === 'edit') {
    const current = state.prompts.find((p) => p.id === state.selectedPromptId)
    if (current) {
      state.promptDraft = { title: current.title, text: current.text }
    }
    state.promptMode = 'view'
  }
}

const savePrompt = () => {
  const title = state.promptDraft.title.trim()
  const text = state.promptDraft.text.trim()
  if (!title || !text) return
  const id = state.selectedPromptId || Math.random().toString(36).slice(2, 11)
  const payload = { id, title, text }
  const idx = state.prompts.findIndex((p) => p.id === id)
  if (idx >= 0) state.prompts.splice(idx, 1, payload)
  else state.prompts.unshift(payload)
  persistPrompts()
  state.selectedPromptId = id
  state.promptMode = 'view'
}

const deletePrompt = () => {
  if (!state.selectedPromptId) return
  if (!confirm('삭제하시겠습니까?')) return
  state.prompts = state.prompts.filter((p) => p.id !== state.selectedPromptId)
  persistPrompts()
  if (state.prompts.length) {
    state.selectedPromptId = state.prompts[0].id
    state.promptDraft = { title: state.prompts[0].title, text: state.prompts[0].text }
    state.promptMode = 'view'
  } else {
    state.selectedPromptId = null
    state.promptDraft = { title: '', text: '' }
    state.promptMode = 'create'
  }
}

const applyPrompt = () => {
  if (!state.selectedPromptId) return
  state.draft.promptId = state.selectedPromptId
  state.promptModalOpen = false
}

const updateSelectedModel = (provider) => {
  if (!selectedInput.value) return
  const versions = modelFamilies.find((f) => f.id === provider)?.subModels || []
  const nextVersion = versions.includes(selectedInput.value.version) ? selectedInput.value.version : versions[0] || selectedInput.value.version
  const updated = { ...selectedInput.value, model: provider, version: nextVersion }
  const idx = state.userInputs.findIndex((u) => u.id === selectedInput.value.id)
  if (idx >= 0) state.userInputs.splice(idx, 1, updated)
  persistUserInputs()
  emitReq(updated)
}

const updateSelectedVersion = (version) => {
  if (!selectedInput.value) return
  const updated = { ...selectedInput.value, version }
  const idx = state.userInputs.findIndex((u) => u.id === selectedInput.value.id)
  if (idx >= 0) state.userInputs.splice(idx, 1, updated)
  persistUserInputs()
  emitReq(updated)
}

const updateSelectedPrompt = (promptId) => {
  if (!selectedInput.value) return
  const normalized = promptId || null
  const updated = { ...selectedInput.value, promptId: normalized }
  const idx = state.userInputs.findIndex((u) => u.id === selectedInput.value.id)
  if (idx >= 0) state.userInputs.splice(idx, 1, updated)
  persistUserInputs()
  emitReq(updated)
}

watch(
  () => state.draft.model,
  (provider) => {
    const versions = modelFamilies.find((f) => f.id === provider)?.subModels || []
    if (!versions.includes(state.draft.version)) {
      state.draft.version = versions[0] || DEFAULT_VERSION
    }
  }
)

watch(
  () => state.selectedPromptId,
  (id) => {
    state.draft.promptId = id
  }
)

onMounted(() => {
  loadUserInputs()
  loadPrompts()
})
</script>

<template>
  <div class="prompt-manager two-col">
    <div class="list-pane">
      <div class="list-pane-header">
        <div>
          <p class="eyebrow">입력정보</p>
          <h3>저장된 입력</h3>
        </div>
        <div class="list-actions">
          <button class="ghost-btn xs" @click="startCreate">+ 새 입력</button>
        </div>
      </div>

      <div class="list">
        <div
          v-for="input in state.userInputs"
          :key="input.id"
          class="list-item"
          :class="{ active: state.selectedInputId === input.id }"
          @click="selectInput(input.id)"
        >
          <div class="list-top">
            <p class="title">{{ input.title }}</p>
            <span class="pill mini">{{ input.model }}</span>
          </div>
          <p class="meta">{{ input.version }}</p>
          <p class="meta light">프롬프트: {{ state.prompts.find((p) => p.id === input.promptId)?.title || '미선택' }}</p>
        </div>
        <div v-if="state.userInputs.length === 0" class="empty">리스트가 없습니다.</div>
      </div>
    </div>

    <div class="detail-pane">
      <div class="detail-header">
        <div>
          <p class="eyebrow" v-if="detailEyebrow">{{ detailEyebrow }}</p>
          <h3>{{ detailTitle }}</h3>
        </div>
        <div class="header-actions">
          <template v-if="state.detailMode === 'view' && selectedInput">
            <button class="ghost-btn xs" @click="startEdit">수정</button>
            <button class="ghost-btn xs danger" @click="deleteInput">삭제</button>
          </template>
        </div>
      </div>

      <div class="detail-body">
        <template v-if="state.detailMode === 'create' || state.detailMode === 'edit'">
          <div class="grid-two">
            <div class="field">
              <label>모델</label>
              <select v-model="state.draft.model">
                <option v-for="family in modelFamilies" :key="family.id" :value="family.id">
                  {{ family.label }}
                </option>
              </select>
            </div>
            <div class="field">
              <label>버전</label>
              <select v-model="state.draft.version">
                <option v-for="sub in currentModelVersions" :key="sub" :value="sub">
                  {{ sub }}
                </option>
              </select>
            </div>
          </div>

          <div class="field">
            <label>프롬프트</label>
            <div class="select-row">
              <select v-model="state.draft.promptId">
                <option value="">프롬프트 선택 안 함</option>
                <option v-for="p in state.prompts" :key="p.id" :value="p.id">
                  {{ p.title }}
                </option>
              </select>
              <button class="ghost-btn xs" @click="openPromptModal">관리</button>
            </div>
            <p class="helper" v-if="state.draft.promptId">
              미리보기: {{ state.prompts.find((p) => p.id === state.draft.promptId)?.text.slice(0, 120) }}
            </p>
          </div>

          <div class="grid-two">
            <div class="field">
              <label>입력정보 이름</label>
              <input v-model="state.draft.title" placeholder="입력정보 이름을 입력하세요." />
            </div>
            <div class="field">
              <label>입력 형태</label>
              <div class="segmented disabled">
                <button class="active" disabled>텍스트</button>
                <button disabled>폼 (준비 중)</button>
              </div>
            </div>
          </div>

          <div class="field">
            <label>입력 값</label>
            <textarea v-model="state.draft.text" rows="8" placeholder="보낼 텍스트를 작성하세요."></textarea>
          </div>

          <div class="actions">
            <button class="ghost-btn" @click="state.detailMode = 'idle'; resetDraft()">취소</button>
            <button class="primary-btn" @click="saveInput">저장</button>
          </div>
        </template>

        <template v-else-if="selectedInput">
          <div class="info-grid">
            <div class="field">
              <label>모델 / 버전</label>
              <div class="inline-pair">
                <select :value="selectedInput.model" @change="updateSelectedModel($event.target.value)">
                  <option v-for="family in modelFamilies" :key="family.id" :value="family.id">
                    {{ family.label }}
                  </option>
                </select>
                <select :value="selectedInput.version" @change="updateSelectedVersion($event.target.value)">
                  <option v-for="sub in viewModelVersions" :key="sub" :value="sub">
                    {{ sub }}
                  </option>
                </select>
              </div>
            </div>
            <div class="field">
              <label>프롬프트</label>
              <div class="select-row">
                <select :value="selectedInput.promptId || ''" @change="updateSelectedPrompt($event.target.value)">
                  <option value="">프롬프트 선택 안 함</option>
                  <option v-for="p in state.prompts" :key="p.id" :value="p.id">
                    {{ p.title }}
                  </option>
                </select>
                <button class="ghost-btn xs" @click="openPromptModal">관리</button>
              </div>
            </div>
            <div class="field">
              <label>입력정보 이름</label>
              <div class="detail-card">{{ selectedInput.title }}</div>
            </div>
          </div>

          <div class="field">
            <label>입력 값</label>
            <div class="detail-card"><pre>{{ selectedInput.text }}</pre></div>
          </div>
        </template>

        <div v-else class="empty-detail">
          좌측에서 입력정보를 선택하거나 추가하세요.
        </div>
      </div>
    </div>
  </div>

  <teleport to="body">
    <div class="prompt-modal" v-if="state.promptModalOpen">
      <div class="prompt-modal-content">
        <div class="modal-header">
          <div>
            <p class="eyebrow template-title">프롬프트 관리</p>
            <h4>{{ state.promptMode === 'create' ? '새 프롬프트 추가' : '프롬프트 선택' }}</h4>
          </div>
          <div class="header-actions">
            <button class="ghost-btn" @click="startPromptCreate">+ 프롬프트 추가</button>
            <button class="ghost-btn" @click="closePromptModal">닫기</button>
          </div>
        </div>
        <div class="template-layout">
          <div class="template-list">
            <div
              v-for="p in state.prompts"
              :key="p.id"
              class="template-item"
              :class="{ active: state.selectedPromptId === p.id }"
              @click="selectPromptForModal(p.id)"
            >
              <p class="title">{{ p.title }}</p>
              <p class="meta">본문 {{ p.text.length }}자</p>
            </div>
            <div v-if="state.prompts.length === 0" class="empty">프롬프트가 없습니다.</div>
          </div>
          <div class="template-detail">
            <div class="field">
              <label>제목</label>
              <input
                v-model="state.promptDraft.title"
                :disabled="state.promptMode === 'view'"
                placeholder="프롬프트 제목"
              />
            </div>
            <div class="field">
              <label>내용</label>
              <textarea
                v-model="state.promptDraft.text"
                rows="8"
                :disabled="state.promptMode === 'view'"
                placeholder="프롬프트 내용을 입력하세요."
              ></textarea>
            </div>
            <div class="actions">
              <button
                class="ghost-btn"
                v-if="state.promptMode === 'view' && state.selectedPromptId"
                @click="startPromptEdit"
              >
                수정
              </button>
              <button class="ghost-btn" v-else @click="cancelPromptEditOrCreate">취소</button>
              <button
                class="ghost-btn danger"
                v-if="state.promptMode !== 'create' && state.selectedPromptId"
                @click="deletePrompt"
              >
                삭제
              </button>
              <button
                v-if="state.promptMode !== 'view'"
                :class="['primary-btn', { 'save-btn': state.promptMode !== 'view' }]"
                @click="savePrompt"
              >
                저장
              </button>
              <button
                class="ghost-btn apply-btn"
                @click="applyPrompt"
                :disabled="!state.selectedPromptId || state.promptMode !== 'view'"
                v-if="state.promptMode === 'view'"
              >
                적용
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </teleport>
</template>

<style scoped>
.prompt-manager {
  display: grid;
  grid-template-columns: 0.95fr 1.55fr;
  grid-template-rows: 1fr;
  gap: 12px;
  color: #e6ecff;
  height: 100%;
  min-height: 0;
  overflow: hidden;
  box-sizing: border-box;
}

.list-pane {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 12px;
  padding: 10px;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.list-pane-header {
  padding: 4px 2px 8px;
  min-width: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.list-pane-header h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: -0.15px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.list-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.detail-pane {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 12px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  min-width: 0;
  min-height: 0;
  overflow: hidden;
}

.read-only-form .readonly-box {
  padding: 10px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.04);
  color: #e6ecff;
  font-size: 13px;
}
.template-name {
  margin: 0 0 8px 0;
  font-size: 12px;
  color: rgba(230, 236, 255, 0.8);
}
.meta-preview {
  margin: 6px 0 0;
  font-size: 12px;
  color: rgba(230, 236, 255, 0.75);
  max-width: 460px;
  white-space: pre-wrap;
}

.primary-btn.xs {
  padding: 8px 12px;
  font-size: 12px;
}

.list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
  overflow-y: auto;
  box-sizing: border-box;
}

.list-item {
  padding: 10px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.04);
  cursor: pointer;
  transition: border-color 0.2s ease, transform 0.2s ease;
}

.list-item:hover {
  border-color: rgba(99, 179, 255, 0.6);
}

.list-item.active {
  border-color: rgba(99, 179, 255, 0.9);
  background: rgba(99, 179, 255, 0.12);
}

.title {
  margin: 0;
  font-weight: 700;
  font-size: 13px;
  text-overflow: ellipsis;
  white-space: nowrap;
  overflow: hidden;
}

.list-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 6px;
}

.meta {
  margin: 4px 0 0;
  font-size: 12px;
  color: rgba(230, 236, 255, 0.8);
}

.meta.light {
  color: rgba(230, 236, 255, 0.65);
}

.empty {
  text-align: center;
  color: rgba(230, 236, 255, 0.6);
  padding: 12px;
  font-size: 12px;
}

.detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  flex-wrap: nowrap;
}

.detail-header > div:first-child {
  flex: 1 1 0;
  min-width: 0;
}

.detail-header h3 {
  margin: 2px 0 0;
  flex: 1 1 200px;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: nowrap;
  justify-content: flex-end;
  flex-shrink: 0;
  white-space: nowrap;
}

.pill {
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  background: rgba(255, 255, 255, 0.08);
  color: #e6ecff;
  font-size: 12px;
  letter-spacing: 0.02em;
  flex-shrink: 0;
}

.pill.mini {
  padding: 4px 8px;
  font-size: 11px;
}

.ghost-btn {
  padding: 8px 10px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  background: rgba(255, 255, 255, 0.06);
  color: #e6ecff;
  cursor: pointer;
  font-size: 12px;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.ghost-btn.danger {
  border-color: rgba(255, 99, 99, 0.5);
  color: #ffcaca;
}

.ghost-btn.xs {
  padding: 6px 8px;
  font-size: 11px;
}

.ghost-btn:hover {
  border-color: rgba(99, 179, 255, 0.7);
  box-shadow: 0 6px 18px rgba(99, 179, 255, 0.2);
}

.detail-body {
  flex: 1;
  overflow: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 12px;
  min-height: 0;
  padding-bottom: 14px;
}

.grid-two {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 10px;
}

.inline-pair {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.inline-pair select {
  width: 100%;
}

.segmented {
  display: inline-flex;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 10px;
  overflow: hidden;
}

.segmented button {
  border: none;
  background: transparent;
  color: #e6ecff;
  padding: 8px 10px;
  cursor: pointer;
  font-size: 12px;
}

.segmented button.active {
  background: rgba(99, 179, 255, 0.16);
  color: #cfe7ff;
}

.segmented.disabled button {
  cursor: not-allowed;
  opacity: 0.7;
}

.select-row {
  display: flex;
  gap: 8px;
  align-items: center;
}

.select-row select {
  flex: 1;
}

.field label {
  display: block;
  margin: 0 0 6px 0;
  font-size: 12px;
  color: rgba(230, 236, 255, 0.7);
  letter-spacing: 0.04em;
}

.field input,
.field textarea,
.field select {
  width: 100%;
  min-width: 0;
  box-sizing: border-box;
  border-radius: 10px;
  border: 1px solid rgba(99, 179, 255, 0.2);
  background: rgba(255, 255, 255, 0.05);
  color: #e6ecff;
  padding: 10px;
  font-size: 13px;
  outline: none;
  font-family: inherit;
}

.field textarea {
  resize: vertical;
  min-height: 120px;
}

.detail-card {
  padding: 12px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.04);
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 13px;
}

.detail-card pre {
  margin: 0;
  white-space: pre-wrap;
  font-family: inherit;
}

.actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  align-items: center;
}

.action-left {
  display: flex;
  gap: 8px;
  justify-content: flex-start;
}

.action-right {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.primary-btn {
  padding: 10px 16px;
  border: none;
  border-radius: 10px;
  background: linear-gradient(135deg, #63b3ff 0%, #63ffdd 100%);
  color: #0b1221;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  font-family: inherit;
}

.primary-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(99, 179, 255, 0.3);
}

.helper {
  margin: 6px 0 0;
  color: rgba(230, 236, 255, 0.7);
  font-size: 12px;
}

.empty-detail {
  padding: 14px;
  border: 1px dashed rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  color: rgba(230, 236, 255, 0.7);
  text-align: center;
}

.prompt-modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 120;
  padding: 20px;
}

.prompt-modal-content {
  background: linear-gradient(135deg, rgba(12, 18, 32, 0.95), rgba(15, 23, 42, 0.95));
  border: 1px solid rgba(99, 179, 255, 0.2);
  border-radius: 16px;
  padding: 20px;
  width: 100%;
  max-width: 760px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  gap: 14px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  overflow: auto;
  box-sizing: border-box;
}

.template-layout {
  display: grid;
  grid-template-columns: 0.65fr 1.35fr;
  gap: 12px;
  min-height: 0;
  height: 100%;
  min-width: 0;
}

.template-list {
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow-y: auto;
  min-width: 0;
}

.template-item {
  padding: 10px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.04);
  cursor: pointer;
  color: #e6ecff;
}

.template-item.active {
  border-color: rgba(99, 179, 255, 0.9);
  background: rgba(99, 179, 255, 0.12);
}

.template-item .meta {
  margin: 4px 0 0;
  font-size: 11px;
  color: rgba(230, 236, 255, 0.8);
}

.template-detail {
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  overflow: auto;
  color: #e6ecff;
  min-height: 320px;
  max-height: 70vh;
  min-width: 0;
}

.template-detail .actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: nowrap;
}

.template-detail .actions .apply-btn {
  margin-left: auto;
}

.template-detail .actions .save-btn {
  margin-left: auto;
}

@media (max-width: 700px) {
  .field-card {
    flex-direction: column;
    align-items: flex-start;
  }
  .field-card button {
    align-self: flex-end;
    width: auto;
  }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(99, 179, 255, 0.2);
  padding-bottom: 10px;
  margin-bottom: 6px;
}

.modal-header h4 {
  margin: 4px 0 0;
  color: #ffffff;
}

.template-title {
  color: #ffffff;
}

@media (max-width: 900px) {
  .template-layout {
    grid-template-columns: 1fr;
  }
}

.system-modal .template-modal-content {
  max-width: 760px;
}

.system-modal .template-detail {
  max-height: 70vh;
}
@media (max-width: 1100px) {
  .prompt-manager {
    grid-template-columns: 1fr;
  }
  .grid-two {
    grid-template-columns: 1fr;
  }
}
</style>
