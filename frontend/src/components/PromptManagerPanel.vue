<script setup>
import { computed, onMounted, reactive, watch } from 'vue'

const STORAGE_KEY = 'studio_input_prompts'
const SYSTEM_KEY = 'studio_system_prompts'
const TEMPLATE_KEY = 'studio_form_templates'
const emit = defineEmits(['update:input', 'update:system'])

const state = reactive({
  prompts: [],
  systemPrompts: [],
  activeTab: 'text', // text | form
  selectedId: null,
  detailMode: 'idle', // idle | view | create | edit
  draft: { title: '', content: '', template: '' },
  selectedSystemId: null,
  systemDraft: { title: '', content: '' },
  systemModalOpen: false,
  systemMode: 'view', // view | create | edit
  templates: [],
  templateModalOpen: false,
  selectedTemplateId: null,
  templateMode: 'view', // view | create
  templateDraft: { name: '', fields: [{ label: '', placeholder: '' }] },
  formValues: []
})

const loadPrompts = () => {
  try {
    const raw = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')
    state.prompts = Array.isArray(raw)
      ? raw.map((p) => {
          const legacyType = p.type || (p.isForm ? 'form' : 'text')
          return {
            ...p,
            type: legacyType === 'form' ? 'form' : 'text'
          }
        })
      : []
  } catch (err) {
    state.prompts = []
  }
}

const persistPrompts = () => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state.prompts))
}

const loadSystemPrompts = () => {
  try {
    const raw = JSON.parse(localStorage.getItem(SYSTEM_KEY) || '[]')
    state.systemPrompts = Array.isArray(raw) ? raw : []
  } catch (err) {
    state.systemPrompts = []
  }
}

const persistSystemPrompts = () => {
  localStorage.setItem(SYSTEM_KEY, JSON.stringify(state.systemPrompts))
}

const loadTemplates = () => {
  try {
    const raw = JSON.parse(localStorage.getItem(TEMPLATE_KEY) || '[]')
    state.templates = Array.isArray(raw) ? raw : []
  } catch (err) {
    state.templates = []
  }
}

const persistTemplates = () => {
  localStorage.setItem(TEMPLATE_KEY, JSON.stringify(state.templates))
}

const tabPrompts = computed(() =>
  state.prompts.filter((p) => (state.activeTab === 'form' ? p.type === 'form' : p.type !== 'form'))
)

const selectedPrompt = computed(() => state.prompts.find((p) => p.id === state.selectedId) || null)

const resetDraft = () => {
  state.draft = { title: '', content: '', template: '' }
  state.formValues = []
}

const currentTemplate = computed(() => {
  if (!state.draft.template) return null
  try {
    return JSON.parse(state.draft.template)
  } catch (err) {
    return null
  }
})

const syncFormValuesFromTemplate = (templateStr) => {
  if (!templateStr) {
    state.formValues = []
    return
  }
  try {
    const parsed = JSON.parse(templateStr)
    if (Array.isArray(parsed.fields)) {
      state.formValues = parsed.fields.map((f, idx) => ({
        label: f.label || '',
        placeholder: f.placeholder || '',
        value: state.formValues?.[idx]?.value || f.value || ''
      }))
      return
    }
  } catch (err) {
    // ignore
  }
  state.formValues = []
}

const detailTitle = computed(() => {
  if (state.detailMode === 'create') return state.activeTab === 'form' ? '입력 폼 추가' : '입력정보 추가'
  if (state.detailMode === 'edit') return state.activeTab === 'form' ? '입력 폼 수정' : '입력정보 수정'
  if (selectedPrompt.value) return selectedPrompt.value.title
  return state.activeTab === 'form' ? '입력 폼을 선택하세요.' : '텍스트를 선택해주세요.'
})

const detailEyebrow = computed(() => {
  if (state.detailMode === 'create') return '새로 추가'
  if (state.detailMode === 'edit') return '수정 중'
  if (selectedPrompt.value) return '선택됨'
  return state.activeTab === 'form' ? '입력 폼' : '입력정보'
})

const selectedSystem = computed(() => state.systemPrompts.find((p) => p.id === state.selectedSystemId) || null)

const systemPreview = computed(() => {
  if (!selectedSystem.value) return ''
  return selectedSystem.value.content?.slice(0, 120) || ''
})

const openSystemModal = () => {
  state.systemModalOpen = true
  state.systemMode = 'view'
  if (state.systemPrompts.length && !state.selectedSystemId) {
    state.selectedSystemId = state.systemPrompts[0].id
    state.systemDraft = { ...state.systemPrompts[0] }
  } else if (!state.systemPrompts.length) {
    state.selectedSystemId = null
    state.systemDraft = { title: '', content: '' }
    state.systemMode = 'create'
  }
}

const closeSystemModal = () => {
  state.systemModalOpen = false
}

const selectSystemPrompt = (id) => {
  const found = state.systemPrompts.find((p) => p.id === id)
  if (!found) return
  state.selectedSystemId = id
  state.systemMode = 'view'
  state.systemDraft = { ...found }
  emit('update:system', state.systemDraft)
}

const startSystemCreate = () => {
  state.systemDraft = { title: '', content: '' }
  state.systemMode = 'create'
  state.selectedSystemId = null
}

const startSystemEdit = () => {
  if (!selectedSystem.value) return
  state.systemMode = 'edit'
}

const cancelSystemEditOrCreate = () => {
  if (state.systemPrompts.length) {
    const target = state.systemPrompts.find((p) => p.id === state.selectedSystemId) || state.systemPrompts[0]
    state.selectedSystemId = target?.id || null
    state.systemDraft = target ? { ...target } : { title: '', content: '' }
    state.systemMode = target ? 'view' : 'create'
  } else {
    state.systemDraft = { title: '', content: '' }
    state.systemMode = 'create'
    state.systemModalOpen = false
  }
}

const saveSystemPrompt = () => {
  if (!state.systemDraft.title.trim() || !state.systemDraft.content.trim()) return
  const id = state.selectedSystemId || Math.random().toString(36).slice(2, 11)
  const payload = { id, title: state.systemDraft.title.trim(), content: state.systemDraft.content.trim() }
  const idx = state.systemPrompts.findIndex((p) => p.id === id)
  if (idx >= 0) state.systemPrompts.splice(idx, 1, payload)
  else state.systemPrompts.unshift(payload)
  state.selectedSystemId = id
  state.systemMode = 'view'
  persistSystemPrompts()
  emit('update:system', payload)
}

const deleteSystemPrompt = () => {
  if (!selectedSystem.value) return
  if (!confirm('삭제하시겠습니까?')) return
  state.systemPrompts = state.systemPrompts.filter((p) => p.id !== selectedSystem.value.id)
  persistSystemPrompts()
  state.selectedSystemId = state.systemPrompts[0]?.id || null
  state.systemDraft = state.systemPrompts[0] || { title: '', content: '' }
  emit('update:system', state.systemPrompts[0] || null)
}

const applySystemPrompt = () => {
  if (!selectedSystem.value) return
  if (state.systemMode !== 'view') return
  emit('update:system', selectedSystem.value)
  state.systemModalOpen = false
}

watch(
  () => state.selectedSystemId,
  () => {
    if (selectedSystem.value) emit('update:system', selectedSystem.value)
  }
)

const resetTemplateDraft = () => {
  state.templateDraft = { name: '', fields: [{ label: '', placeholder: '' }] }
}

const openTemplateModal = () => {
  state.templateModalOpen = true
  state.templateMode = 'view'
  if (state.templates.length) {
    state.selectedTemplateId = state.templates[0].id
    state.templateDraft = {
      name: state.templates[0].name,
      fields: state.templates[0].fields ? state.templates[0].fields.map((f) => ({ ...f })) : []
    }
  } else {
    state.selectedTemplateId = null
    resetTemplateDraft()
    state.templateMode = 'create'
  }
}

const closeTemplateModal = () => {
  state.templateModalOpen = false
}

const selectTemplateForModal = (id) => {
  const found = state.templates.find((t) => t.id === id)
  if (!found) return
  state.selectedTemplateId = id
  state.templateMode = 'view'
  state.templateDraft = {
    name: found.name,
    fields: found.fields ? found.fields.map((f) => ({ ...f })) : []
  }
}

const startTemplateCreate = () => {
  state.templateMode = 'create'
  state.selectedTemplateId = null
  resetTemplateDraft()
}

const startTemplateEdit = () => {
  if (!state.selectedTemplateId) return
  state.templateMode = 'edit'
}

const cancelTemplateEditOrCreate = () => {
  if (state.templateMode === 'create') {
    if (state.templates.length) {
      const first = state.templates[0]
      state.selectedTemplateId = first.id
      state.templateDraft = {
        name: first.name,
        fields: first.fields ? first.fields.map((f) => ({ ...f })) : []
      }
      state.templateMode = 'view'
    } else {
      resetTemplateDraft()
      state.templateMode = 'view'
    }
    return
  }

  if (state.templateMode === 'edit') {
    const current = state.templates.find((t) => t.id === state.selectedTemplateId)
    if (current) {
      state.templateDraft = {
        name: current.name,
        fields: current.fields ? current.fields.map((f) => ({ ...f })) : []
      }
    }
    state.templateMode = 'view'
  }
}

const deleteTemplate = () => {
  if (!state.selectedTemplateId) return
  if (!confirm('삭제하시겠습니까?')) return
  state.templates = state.templates.filter((t) => t.id !== state.selectedTemplateId)
  persistTemplates()
  if (state.templates.length) {
    state.selectedTemplateId = state.templates[0].id
    state.templateDraft = {
      name: state.templates[0].name,
      fields: state.templates[0].fields ? state.templates[0].fields.map((f) => ({ ...f })) : []
    }
    state.templateMode = 'view'
  } else {
    state.selectedTemplateId = null
    resetTemplateDraft()
    state.templateMode = 'create'
  }
}

const addTemplateField = () => {
  state.templateDraft.fields = [...state.templateDraft.fields, { label: '', placeholder: '' }]
}

const removeTemplateField = (idx) => {
  if (state.templateDraft.fields.length === 1) return
  state.templateDraft.fields = state.templateDraft.fields.filter((_, i) => i !== idx)
}

const saveTemplate = () => {
  const name = state.templateDraft.name.trim()
  if (!name) return
  const fields = state.templateDraft.fields.map((f) => ({
    label: (f.label || '').trim(),
    placeholder: (f.placeholder || '').trim()
  }))
  const cleanedFields = fields.length ? fields : []
  const id = state.selectedTemplateId || Math.random().toString(36).slice(2, 11)
  const payload = { id, name, fields: cleanedFields }
  const idx = state.templates.findIndex((t) => t.id === id)
  if (idx >= 0) {
    state.templates.splice(idx, 1, payload)
  } else {
    state.templates.unshift(payload)
  }
  persistTemplates()
  state.selectedTemplateId = id
  state.templateMode = 'view'
}

const getFormFields = (prompt) => {
  if (!prompt || prompt.type !== 'form') return []
  try {
    const parsed = JSON.parse(prompt.content || '{}')
    if (Array.isArray(parsed.fields)) {
      return parsed.fields.map((f) => ({
        label: f.label || '',
        placeholder: f.placeholder || '',
        value: f.value || ''
      }))
    }
  } catch (err) {
    return []
  }
  return []
}

const currentTemplateName = (prompt) => {
  if (!prompt || prompt.type !== 'form') return ''
  try {
    const parsed = JSON.parse(prompt.content || '{}')
    return parsed.templateName || parsed.name || ''
  } catch (err) {
    return ''
  }
}

const applyTemplate = () => {
  if (!state.templateDraft.name) return
  state.draft.template = JSON.stringify({
    name: state.templateDraft.name,
    fields: state.templateDraft.fields
  })
  syncFormValuesFromTemplate(state.draft.template)
  state.templateModalOpen = false
}

const handleTemplateSelect = (value) => {
  state.draft.template = value
  syncFormValuesFromTemplate(value)
}

const startCreate = () => {
  state.detailMode = 'create'
  state.selectedId = null
  resetDraft()
  emit('update:input', null)
}

const selectPrompt = (id) => {
  state.selectedId = id
  state.detailMode = 'view'
  const found = state.prompts.find((p) => p.id === id) || null
  emit('update:input', found)
}

const startEdit = () => {
  if (!selectedPrompt.value) return
  state.detailMode = 'edit'
  state.draft.title = selectedPrompt.value.title
  state.draft.content = selectedPrompt.value.content

  if (selectedPrompt.value.type === 'form') {
    try {
      const parsed = JSON.parse(selectedPrompt.value.content || '{}')
      const tplName = parsed.templateName || parsed.name || ''
      const tplFields = Array.isArray(parsed.fields)
        ? parsed.fields.map((f) => ({ label: f.label || '', placeholder: f.placeholder || '' }))
        : []
      state.draft.template = JSON.stringify({ name: tplName, fields: tplFields })
      syncFormValuesFromTemplate(JSON.stringify({ name: tplName, fields: parsed.fields || [] }))
    } catch (err) {
      state.draft.template = ''
      state.formValues = []
    }
  } else {
    state.draft.template = ''
    state.formValues = []
  }
}

const deletePrompt = () => {
  if (!selectedPrompt.value) return
  if (!confirm('삭제하시겠습니까?')) return
  state.prompts = state.prompts.filter((p) => p.id !== selectedPrompt.value.id)
  persistPrompts()
  state.selectedId = null
  state.detailMode = 'idle'
  emit('update:input', null)
}

const savePrompt = () => {
  const title = state.draft.title.trim()
  const isForm = state.activeTab === 'form'

  if (!title) return

  let templateObj = null
  if (isForm) {
    const template = state.draft.template.trim()
    if (!template) return
    try {
      templateObj = JSON.parse(template)
    } catch (err) {
      return
    }
  } else if (!state.draft.content.trim()) {
    return
  }

  const id = state.detailMode === 'edit' && selectedPrompt.value ? selectedPrompt.value.id : Math.random().toString(36).slice(2, 11)
  const formContent = isForm && templateObj
    ? JSON.stringify({
        templateName: templateObj.name,
        fields: Array.isArray(templateObj.fields)
          ? templateObj.fields.map((f, idx) => ({
              label: f.label || '',
              placeholder: f.placeholder || '',
              value: state.formValues?.[idx]?.value || ''
            }))
          : []
      })
    : null

  const payload = {
    id,
    title,
    content: isForm ? formContent : state.draft.content.trim(),
    type: isForm ? 'form' : 'text'
  }

  const existingIndex = state.prompts.findIndex((p) => p.id === id)
  if (existingIndex >= 0) {
    state.prompts.splice(existingIndex, 1, payload)
  } else {
    state.prompts.unshift(payload)
  }

  persistPrompts()
  state.selectedId = id
  state.detailMode = 'view'
  emit('update:input', payload)
}

watch(
  () => state.activeTab,
  () => {
    state.selectedId = null
    state.detailMode = 'idle'
    resetDraft()
    emit('update:input', null)
  }
)

onMounted(() => {
  loadPrompts()
  loadTemplates()
  loadSystemPrompts()
})
</script>

<template>
    <div class="prompt-manager">
    <div class="system-toolbar">
      <div>
        <p class="selected-badge" v-if="selectedSystem">선택된 프롬프트</p>
        <h3 class="meta-title">{{ selectedSystem?.title || '프롬프트 관리에서 프롬프트를 선택하세요.' }}</h3>
      </div>
      <div class="system-actions">
        <button class="ghost-btn" @click="openSystemModal">프롬프트 관리</button>
      </div>
    </div>
      <div class="list-pane">
        <div class="list-pane-header">
          <h3>입력 정보 목록</h3>
        </div>
        <div class="tab-row">
          <button
            class="tab-btn"
            :class="{ active: state.activeTab === 'text' }"
            @click="state.activeTab = 'text'"
        >
          텍스트
        </button>
        <button
          class="tab-btn"
          :class="{ active: state.activeTab === 'form' }"
          @click="state.activeTab = 'form'"
        >
          입력 폼
        </button>
        <button class="add-btn" @click="startCreate">+</button>
      </div>

      <div class="list">
        <div
          v-for="prompt in tabPrompts"
          :key="prompt.id"
          class="list-item"
          :class="{ active: state.selectedId === prompt.id }"
          @click="selectPrompt(prompt.id)"
        >
          <p class="title">{{ prompt.title }}</p>
        </div>
        <div v-if="tabPrompts.length === 0" class="empty">리스트가 없습니다.</div>
      </div>
    </div>

    <div class="detail-pane">
      <div class="detail-header">
        <div>
          <p class="eyebrow">{{ detailEyebrow }}</p>
          <h3>{{ detailTitle }}</h3>
        </div>
        <div class="header-actions">
          <span class="pill" :class="{ form: state.activeTab === 'form' }">
            {{ state.activeTab === 'form' ? '입력 폼' : '텍스트' }}
          </span>
          <template v-if="state.detailMode === 'view' && selectedPrompt">
            <button class="ghost-btn xs" @click="startEdit">수정</button>
            <button class="ghost-btn xs danger" @click="deletePrompt">삭제</button>
          </template>
        </div>
      </div>

      <div class="detail-body">
        <template v-if="state.detailMode === 'create' || state.detailMode === 'edit'">
          <div class="field">
            <label>제목</label>
            <input v-model="state.draft.title" placeholder="제목을 입력하세요." />
          </div>

          <div v-if="state.activeTab === 'text'" class="field">
            <label>입력 내용</label>
            <textarea v-model="state.draft.content" rows="8" placeholder="입력정보 내용을 작성하세요."></textarea>
          </div>

          <div v-else class="field">
            <label>템플릿을 선택하세요.</label>
            <div class="template-row">
              <select :value="state.draft.template" @change="handleTemplateSelect($event.target.value)">
                <option disabled value="">템플릿 선택</option>
                <option
                  v-for="tpl in state.templates"
                  :key="tpl.id"
                  :value="JSON.stringify({ name: tpl.name, fields: tpl.fields })"
                >
                  {{ tpl.name }}
                </option>
              </select>
              <button class="ghost-btn" @click.prevent="openTemplateModal">...</button>
            </div>
            <div v-if="currentTemplate?.fields?.length" class="fill-fields">
              <div
                v-for="(field, idx) in currentTemplate.fields"
                :key="idx"
                class="field-fill-row"
              >
                <label>{{ field.label || `필드 ${idx + 1}` }}</label>
                <input
                  v-model="state.formValues[idx].value"
                  :placeholder="field.placeholder || '값을 입력하세요.'"
                />
              </div>
            </div>
            <p class="helper">템플릿을 선택 후 필드 값을 채워 저장하세요.</p>
          </div>

          <div class="actions">
            <button class="ghost-btn" @click="state.detailMode = 'idle'; resetDraft()">취소</button>
            <button class="primary-btn" @click="savePrompt">저장</button>
          </div>
        </template>

        <template v-else-if="selectedPrompt">
          <div class="field">
            <label>제목</label>
            <div class="detail-card">{{ selectedPrompt.title }}</div>
          </div>
          <div class="field" v-if="selectedPrompt.type === 'text'">
            <label>입력정보 내용</label>
            <div class="detail-card"><pre>{{ selectedPrompt.content }}</pre></div>
          </div>
          <div class="field" v-else>
            <label>입력 폼</label>
            <div class="detail-card">
              <p class="template-name" v-if="currentTemplateName(selectedPrompt)">템플릿: {{ currentTemplateName(selectedPrompt) }}</p>
              <div v-if="getFormFields(selectedPrompt).length" class="fill-fields read-only-form">
                <div
                  v-for="(field, idx) in getFormFields(selectedPrompt)"
                  :key="idx"
                  class="field-fill-row"
                >
                  <label>{{ field.label || `필드 ${idx + 1}` }}</label>
                  <div class="readonly-box">{{ field.value || '(미입력)' }}</div>
                </div>
              </div>
              <div v-else>폼 데이터 없음</div>
            </div>
          </div>
        </template>

        <div v-else class="empty-detail">
          좌측에서 입력정보나 입력 폼을 선택하거나 추가하세요.
        </div>
      </div>
    </div>
  </div>


  <teleport to="body">
    <div class="system-modal" v-if="state.systemModalOpen">
      <div class="template-modal-content">
          <div class="modal-header">
            <div>
              <p class="eyebrow template-title">프롬프트</p>
              <h4>{{ state.systemMode === 'create' ? '새 프롬프트 추가' : '프롬프트 관리' }}</h4>
            </div>
            <div class="header-actions">
              <button class="ghost-btn" @click="startSystemCreate">+ 새 프롬프트</button>
              <button class="ghost-btn" @click="closeSystemModal">닫기</button>
            </div>
          </div>
          <div class="template-layout">
            <div class="template-list">
            <div
              v-for="sp in state.systemPrompts"
              :key="sp.id"
              class="template-item"
              :class="{ active: state.selectedSystemId === sp.id }"
              @click="selectSystemPrompt(sp.id)"
            >
              <p class="title">{{ sp.title }}</p>
              <p class="meta">본문 {{ sp.content.length }}자</p>
            </div>
            <div v-if="state.systemPrompts.length === 0" class="empty">프롬프트가 없습니다.</div>
            </div>
            <div class="template-detail">
              <div class="field">
                <label>제목</label>
                <input
                  v-model="state.systemDraft.title"
                  :disabled="state.systemMode === 'view'"
                  placeholder="시스템 프롬프트 제목"
                />
              </div>
              <div class="field">
                <label>내용</label>
                <textarea
                  v-model="state.systemDraft.content"
                  rows="8"
                  :disabled="state.systemMode === 'view'"
                  placeholder="시스템 프롬프트 내용을 입력하세요."
              ></textarea>
              </div>
              <div class="actions">
                <div class="action-left">
                  <template v-if="state.systemMode === 'create'">
                    <button class="primary-btn" @click="saveSystemPrompt">저장</button>
                    <button class="ghost-btn" @click="cancelSystemEditOrCreate">취소</button>
                  </template>
                  <template v-else>
                    <button class="ghost-btn" v-if="state.systemMode === 'view' && selectedSystem" @click="startSystemEdit">수정</button>
                    <button class="primary-btn" v-if="state.systemMode === 'edit'" @click="saveSystemPrompt">저장</button>
                    <button class="ghost-btn danger" v-if="selectedSystem" @click="deleteSystemPrompt">삭제</button>
                  </template>
                </div>
                <div class="action-right">
                  <template v-if="state.systemMode !== 'create'">
                    <button class="ghost-btn" @click="applySystemPrompt" :disabled="!selectedSystem || state.systemMode !== 'view'">적용</button>
                  </template>
                </div>
              </div>
            </div>
          </div>
      </div>
    </div>
  </teleport>
  <teleport to="body">
    <div class="template-modal" v-if="state.templateModalOpen">
      <div class="template-modal-content">
        <div class="modal-header">
          <div>
            <p class="eyebrow template-title">입력 폼 템플릿 관리</p>
            <h4>{{ state.templateMode === 'create' ? '새 템플릿 추가' : '템플릿 선택' }}</h4>
          </div>
          <div class="header-actions">
            <button class="ghost-btn" @click="startTemplateCreate">+ 템플릿 추가</button>
            <button class="ghost-btn" @click="closeTemplateModal">닫기</button>
          </div>
        </div>
        <div class="template-layout">
          <div class="template-list">
            <div
              v-for="tpl in state.templates"
              :key="tpl.id"
              class="template-item"
              :class="{ active: state.selectedTemplateId === tpl.id }"
              @click="selectTemplateForModal(tpl.id)"
            >
              <p class="title">{{ tpl.name }}</p>
              <p class="meta">필드 {{ tpl.fields?.length || 0 }}</p>
            </div>
            <div v-if="state.templates.length === 0" class="empty">템플릿이 없습니다.</div>
          </div>
          <div class="template-detail">
            <div class="field">
              <label>템플릿 이름</label>
              <input
                v-model="state.templateDraft.name"
                placeholder="템플릿 이름"
                :disabled="state.templateMode === 'view'"
              />
            </div>
            <div class="field">
              <div class="field-row">
                <label>필드</label>
                <button class="ghost-btn xs" @click="addTemplateField" :disabled="state.templateMode === 'view'">+ 필드 추가</button>
              </div>
              <div class="field-list">
                <div
                  v-for="(field, idx) in state.templateDraft.fields"
                  :key="idx"
                  class="field-card"
                >
                  <input v-model="field.label" placeholder="라벨" :disabled="state.templateMode === 'view'" />
                  <input v-model="field.placeholder" placeholder="예시/placeholder" :disabled="state.templateMode === 'view'" />
                  <button class="ghost-btn xs" @click="removeTemplateField(idx)" :disabled="state.templateMode === 'view'">삭제</button>
                </div>
              </div>
            </div>
            <div class="actions">
              <button
                class="ghost-btn"
                v-if="state.templateMode === 'view' && state.selectedTemplateId"
                @click="startTemplateEdit"
              >
                수정
              </button>
              <button class="ghost-btn" v-else @click="cancelTemplateEditOrCreate">취소</button>
              <button
                class="ghost-btn danger"
                v-if="state.templateMode !== 'create' && state.selectedTemplateId"
                @click="deleteTemplate"
              >
                삭제
              </button>
              <button
                v-if="state.templateMode !== 'view'"
                :class="['primary-btn', { 'save-btn': state.templateMode !== 'view' }]"
                @click="saveTemplate"
              >
                저장
              </button>
              <button
                class="ghost-btn apply-btn"
                @click="applyTemplate"
                :disabled="!state.templateDraft.name || state.templateMode !== 'view'"
                v-if="state.templateMode === 'view'"
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
  grid-template-columns: 0.9fr 1.6fr;
  grid-template-rows: auto 1fr;
  gap: 10px;
  color: #e6ecff;
  height: 100%;
  min-height: 0;
  overflow: hidden;
  box-sizing: border-box;
}

.system-toolbar {
  min-height: 44px;
  grid-column: 1 / -1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 10px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.03);
}

.system-toolbar .meta-title {
  margin: 2px 0 0;
}

.system-toolbar .system-actions {
  display: flex;
  gap: 8px;
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
}

.list-pane-header h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: -0.15px;
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


.selected-badge {
  margin: 6px 0 0;
  font-size: 11px;
  color: #cfe7ff;
  letter-spacing: 0.05em;
}
.system-actions {
  display: flex;
  gap: 8px;
  align-items: center;
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
.tab-row {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 10px;
}

.tab-btn {
  flex: 1;
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.05);
  color: #e6ecff;
  cursor: pointer;
  font-size: 13px;
  transition: border-color 0.2s ease, background-color 0.2s ease;
}

.tab-btn.active {
  border-color: rgba(99, 179, 255, 0.8);
  background: rgba(99, 179, 255, 0.16);
}

.add-btn {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.08);
  color: #e6ecff;
  cursor: pointer;
  font-weight: 700;
  font-size: 16px;
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
}

.detail-header h3 {
  margin: 2px 0 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 6px;
}

.pill {
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  background: rgba(255, 255, 255, 0.08);
  color: #e6ecff;
  font-size: 12px;
  letter-spacing: 0.02em;
}

.pill.form {
  border-color: rgba(99, 179, 255, 0.5);
  color: #cfe7ff;
  background: rgba(99, 179, 255, 0.15);
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

.template-row {
  display: flex;
  gap: 8px;
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

.template-modal {
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

.template-modal-content {
  background: linear-gradient(135deg, rgba(12, 18, 32, 0.95), rgba(15, 23, 42, 0.95));
  border: 1px solid rgba(99, 179, 255, 0.2);
  border-radius: 16px;
  padding: 20px;
  width: 100%;
  max-width: 780px;
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

.field-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.field-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 360px;
  overflow: auto;
  margin-top: 8px;
}

.field-card {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 8px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.04);
  align-items: flex-start;
}

.field-card input {
  flex: 1 1 150px;
  min-width: 0;
}

.field-card button {
  flex: 0 0 auto;
  min-width: 72px;
  align-self: center;
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

.template-detail {
  min-height: 320px;
}

@media (max-width: 900px) {
  .template-layout {
    grid-template-columns: 1fr;
  }
}


.fill-fields {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 10px;
}

.field-fill-row {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-fill-row label {
  font-size: 12px;
  color: rgba(230, 236, 255, 0.8);
  margin: 0;
}

.field-fill-row input {
  width: 100%;
  border-radius: 10px;
  border: 1px solid rgba(99, 179, 255, 0.2);
  background: rgba(255, 255, 255, 0.05);
  color: #e6ecff;
  padding: 10px;
  font-size: 13px;
}

.preview-field {
  margin-bottom: 6px;
}

.field-value {
  margin: 2px 0 0;
  font-size: 12px;
  color: rgba(230, 236, 255, 0.85);
}

.system-modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 125;
  padding: 20px;
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
}
</style>
