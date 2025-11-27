<script setup>
import { computed, reactive, watch } from 'vue'

const SYSTEM_KEY = 'studio_system_prompts'
const INPUT_KEY = 'studio_input_prompts'

const emit = defineEmits(['update:system', 'update:input'])

const state = reactive({
  systemPrompts: [],
  inputPrompts: [],
  systemSearch: '',
  inputSearch: '',
  selectedSystemId: null,
  selectedInputId: null,
  systemDraft: { title: '', content: '' },
  inputDraft: { title: '', content: '' },
  editMode: null // { type: 'system' | 'input', id }
})

const loadPrompts = () => {
  try {
    state.systemPrompts = JSON.parse(localStorage.getItem(SYSTEM_KEY) || '[]')
    state.inputPrompts = JSON.parse(localStorage.getItem(INPUT_KEY) || '[]')
  } catch (err) {
    state.systemPrompts = []
    state.inputPrompts = []
  }
}

const persistPrompts = () => {
  localStorage.setItem(SYSTEM_KEY, JSON.stringify(state.systemPrompts))
  localStorage.setItem(INPUT_KEY, JSON.stringify(state.inputPrompts))
}

const selectPrompt = (type, id) => {
  if (type === 'system') {
    if (state.selectedSystemId === id) {
      state.selectedSystemId = null
      emit('update:system', null)
    } else {
      state.selectedSystemId = id
      emit('update:system', state.systemPrompts.find((p) => p.id === id) || null)
    }
  } else {
    if (state.selectedInputId === id) {
      state.selectedInputId = null
      emit('update:input', null)
    } else {
      state.selectedInputId = id
      emit('update:input', state.inputPrompts.find((p) => p.id === id) || null)
    }
  }
}

const startCreate = (type) => {
  state.editMode = { type, id: null }
  state.systemDraft = { title: '', content: '' }
  state.inputDraft = { title: '', content: '' }
}

const startEdit = (type, prompt) => {
  state.editMode = { type, id: prompt.id }
  if (type === 'system') {
    state.systemDraft = { title: prompt.title, content: prompt.content }
  } else {
    state.inputDraft = { title: prompt.title, content: prompt.content }
  }
}

const savePrompt = (type) => {
  const draft = type === 'system' ? state.systemDraft : state.inputDraft
  const list = type === 'system' ? state.systemPrompts : state.inputPrompts
  if (!draft.title.trim() || !draft.content.trim()) return

  if (state.editMode?.id) {
    const target = list.find((p) => p.id === state.editMode.id)
    if (target) {
      target.title = draft.title
      target.content = draft.content
    }
  } else {
    list.unshift({
      id: `${type}-${Date.now()}`,
      title: draft.title,
      content: draft.content,
      tags: []
    })
  }

  persistPrompts()
  state.editMode = null
}

const deletePrompt = (type, id) => {
  if (!confirm('삭제하시겠습니까?')) return
  if (type === 'system') {
    state.systemPrompts = state.systemPrompts.filter((p) => p.id !== id)
    if (state.selectedSystemId === id) {
      state.selectedSystemId = null
      emit('update:system', null)
    }
  } else {
    state.inputPrompts = state.inputPrompts.filter((p) => p.id !== id)
    if (state.selectedInputId === id) {
      state.selectedInputId = null
      emit('update:input', null)
    }
  }
  persistPrompts()
}

const filteredSystemPrompts = computed(() => {
  if (!state.systemSearch.trim()) return state.systemPrompts
  return state.systemPrompts.filter(
    (p) =>
      p.title.toLowerCase().includes(state.systemSearch.toLowerCase()) ||
      p.content.toLowerCase().includes(state.systemSearch.toLowerCase())
  )
})

const filteredInputPrompts = computed(() => {
  if (!state.inputSearch.trim()) return state.inputPrompts
  return state.inputPrompts.filter(
    (p) =>
      p.title.toLowerCase().includes(state.inputSearch.toLowerCase()) ||
      p.content.toLowerCase().includes(state.inputSearch.toLowerCase())
  )
})

const draftTitle = computed({
  get: () => state.editMode?.type === 'system' ? state.systemDraft.title : state.inputDraft.title,
  set: (value) => {
    if (state.editMode?.type === 'system') {
      state.systemDraft.title = value
    } else {
      state.inputDraft.title = value
    }
  }
})

const draftContent = computed({
  get: () => state.editMode?.type === 'system' ? state.systemDraft.content : state.inputDraft.content,
  set: (value) => {
    if (state.editMode?.type === 'system') {
      state.systemDraft.content = value
    } else {
      state.inputDraft.content = value
    }
  }
})

watch(
  () => state.editMode,
  (mode) => {
    if (!mode) {
      state.systemDraft = { title: '', content: '' }
      state.inputDraft = { title: '', content: '' }
    }
  }
)

loadPrompts()
</script>

<template>
  <div class="prompt-manager">
    <div class="column">
      <div class="header">
        <div>
          <p class="eyebrow">입력 값 설정</p>
          <h4>입력 값 목록</h4>
        </div>
        <button class="ghost-btn" @click="startCreate('input')">+ 새 프롬프트</button>
      </div>
      <div class="search-row">
        <input v-model="state.inputSearch" placeholder="검색 / 태그 필터" />
      </div>
      <div class="list">
        <div
          v-for="prompt in filteredInputPrompts"
          :key="prompt.id"
          class="list-item"
          :class="{ active: state.selectedInputId === prompt.id }"
          @click="selectPrompt('input', prompt.id)"
        >
          <div>
            <p class="title">{{ prompt.title }}</p>
            <p class="preview">{{ prompt.content }}</p>
          </div>
          <div class="actions" @click.stop>
            <button class="ghost-btn xs" @click="startEdit('input', prompt)">✏️</button>
            <button class="ghost-btn xs" @click="deletePrompt('input', prompt.id)">🗑️</button>
          </div>
        </div>
        <div v-if="filteredInputPrompts.length === 0" class="empty">프롬프트가 없습니다.</div>
      </div>
    </div>

    <teleport to="body">
      <div class="editor-modal" v-if="state.editMode">
        <div class="editor-modal-content">
          <div class="editor-header">
            <div>
              <p class="eyebrow">{{ state.editMode.type === 'system' ? '시스템' : '인풋' }} 프롬프트</p>
              <h4>{{ state.editMode.id ? '프롬프트 수정' : '새 프롬프트 생성' }}</h4>
            </div>
            <div class="editor-actions">
              <button class="ghost-btn" @click="state.editMode = null">취소</button>
              <button class="primary-btn" @click="savePrompt(state.editMode.type)">저장</button>
            </div>
          </div>
          <div class="form">
            <input
              v-model="draftTitle"
              placeholder="프롬프트 제목"
            />
            <textarea
              v-model="draftContent"
              placeholder="프롬프트 내용"
              rows="10"
            ></textarea>
          </div>
        </div>
      </div>
    </teleport>
  </div>
</template>

<style scoped>
.prompt-manager {
  display: grid;
  grid-template-columns: 1fr;
  grid-template-rows: 1fr;
  gap: 12px;
  color: #e6ecff;
  height: 100%;
  overflow: hidden;
  box-sizing: border-box;
}

.column {
  display: flex;
  flex-direction: column;
  gap: 8px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 12px;
  padding: 12px;
  box-sizing: border-box;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.eyebrow {
  margin: 0;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-size: 14px;
  color: #8fb5ff;
}

h4 {
  margin: 2px 0 0;
}

.search-row input {
  width: 100%;
  padding: 10px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.05);
  color: #e6ecff;
  box-sizing: border-box;
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
  display: flex;
  justify-content: space-between;
  gap: 8px;
  padding: 10px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.04);
  cursor: pointer;
  transition: border-color 0.2s ease, transform 0.2s ease;
  min-width: 0;
  box-sizing: border-box;
}

.list-item > div:first-child {
  min-width: 0;
  flex: 1;
  box-sizing: border-box;
  overflow: hidden;
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
  display: -webkit-box;
  -webkit-line-clamp: 1;   /* 원하s는 줄 수 */
  -webkit-box-orient: vertical;
}

/* .preview {
  margin: 4px 0 0;
  font-size: 11px;
  color: rgba(230, 236, 255, 0.7);
  text-overflow: ellipsis;
  white-space: normal;
} */
.preview {
  white-space: normal;
  font-size: 11px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 1;   /* 원하s는 줄 수 */
  -webkit-box-orient: vertical;
}

.actions {
  display: flex;
  gap: 4px;
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

.ghost-btn.xs {
  padding: 6px 8px;
}

.ghost-btn:hover {
  border-color: rgba(99, 179, 255, 0.7);
  box-shadow: 0 6px 18px rgba(99, 179, 255, 0.2);
}

.preview-container {
  margin-top: 6px;
}

.preview pre {
  white-space: pre-wrap;
  background: rgba(0, 0, 0, 0.25);
  padding: 10px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #e6ecff;
  font-size: 12px;
  line-height: 1.5;
}

.preview .label {
  margin: 0 0 6px;
  color: rgba(230, 236, 255, 0.7);
  font-size: 12px;
}

.empty {
  text-align: center;
  color: rgba(230, 236, 255, 0.6);
  padding: 12px;
  font-size: 12px;
}

.editor-modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 20px;
}

.editor-modal-content {
  background: linear-gradient(135deg, rgba(12, 18, 32, 0.95), rgba(15, 23, 42, 0.95));
  border: 1px solid rgba(99, 179, 255, 0.2);
  border-radius: 16px;
  padding: 24px;
  width: 100%;
  max-width: 600px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.editor-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(99, 179, 255, 0.2);
}

.editor-header h4 {
  margin: 4px 0 0;
  font-size: 18px;
  font-weight: 700;
  color: #ffffff;
}

.editor-actions {
  display: flex;
  gap: 8px;
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
}

.primary-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(99, 179, 255, 0.3);
}

.form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.form input,
.form textarea {
  width: 100%;
  border-radius: 10px;
  border: 1px solid rgba(99, 179, 255, 0.2);
  background: rgba(255, 255, 255, 0.05);
  color: #e6ecff;
  padding: 12px;
  font-size: 13px;
  outline: none;
  font-family: inherit;
  transition: border-color 0.2s ease;
  box-sizing: border-box;
}

.form input:focus,
.form textarea:focus {
  border-color: rgba(99, 179, 255, 0.6);
  background: rgba(255, 255, 255, 0.08);
}
</style>
