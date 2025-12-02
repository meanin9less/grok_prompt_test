<script setup>
import { computed, onMounted, reactive, watch } from 'vue'
import InputList from './InputList.vue'
import InputDetail from './InputDetail.vue'
import PromptSelectorModal from './PromptSelectorModal.vue'
import FormTemplateModal from './FormTemplateModal.vue'

const USER_INPUT_KEY = 'user_input_texts'
const PROMPT_KEY = 'prompt_entries'
const TEMPLATE_KEY = 'form_templates'

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

const parseOptions = (val) => {
  if (Array.isArray(val)) return val.filter(Boolean)
  return String(val || '')
    .split(/\n|,/)
    .map((o) => o.trim())
    .filter(Boolean)
}

const toOptionObjects = (val) => {
  const arr = parseOptions(val)
  return arr.map((v) => ({ label: v, value: v }))
}

const state = reactive({
  userInputs: [],
  prompts: [],
  templates: [],
  selectedInputId: null,
  detailMode: 'idle', // idle | view | create | edit
  draft: { title: '', text: '', model: DEFAULT_PROVIDER, version: DEFAULT_VERSION, promptId: null, inputType: 'text', templateId: null, formData: {} },
  promptModalOpen: false,
  promptMode: 'view', // view | create | edit
  selectedPromptId: null,
  promptDraft: { title: '', text: '' },
  templateModalOpen: false,
  templateMode: 'view',
  selectedTemplateId: null,
  templateDraft: { name: '', description: '', fields: [] }
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
          promptId: item.promptId || item.systemPromptId || null,
          inputType: item.inputType || 'text',
          templateId: item.templateId || null,
          formData: item.formData || {}
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

const loadTemplates = () => {
  try {
    const raw = JSON.parse(localStorage.getItem(TEMPLATE_KEY) || '[]')
    state.templates = Array.isArray(raw)
      ? raw.map((t) => ({
          id: t.id || Math.random().toString(36).slice(2, 11),
          name: t.name || '이름 없는 폼',
          description: t.description || '',
          schemaVersion: t.schemaVersion || 1,
          fields: Array.isArray(t.fields)
            ? t.fields.map((f, idx) => ({
                id: f.id || `${Date.now()}-${idx}`,
                name: f.name || `field_${idx}`,
                label: f.label || f.name || `필드 ${idx + 1}`,
                type: f.type || 'text',
                required: Boolean(f.required),
                options: Array.isArray(f.options)
                  ? f.options.map((opt) =>
                      typeof opt === 'string'
                        ? { label: opt, value: opt }
                        : { label: opt.label || opt.value || '', value: opt.value || opt.label || '' }
                    )
                  : toOptionObjects(f.options || []),
                optionsInput: Array.isArray(f.options)
                  ? f.options.map((opt) => (typeof opt === 'string' ? opt : opt.label || opt.value || '')).join('\n')
                  : ''
              }))
            : []
        }))
      : []
  } catch (err) {
    state.templates = []
  }
}

const persistTemplates = () => {
  localStorage.setItem(TEMPLATE_KEY, JSON.stringify(state.templates))
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
    promptId: null,
    inputType: 'text',
    templateId: null,
    formData: {}
  }
}

const updateDraft = (partial) => {
  state.draft = { ...state.draft, ...partial }
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
    user_input:
      (input.inputType || 'text') === 'form'
        ? {
            id: input.id,
            title: input.title,
            type: 'form',
            template_id: input.templateId || null,
            form: input.formData || {},
            text: JSON.stringify(input.formData || {})
          }
        : {
            id: input.id,
            title: input.title,
            text: input.text,
            type: 'text'
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

const cancelEdit = () => {
  state.detailMode = 'idle'
  resetDraft()
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
    promptId: selectedInput.value.promptId || null,
    inputType: selectedInput.value.inputType || 'text',
    templateId: selectedInput.value.templateId || null,
    formData: selectedInput.value.formData || {}
  }
  state.selectedPromptId = selectedInput.value.promptId || null
}

const saveInput = () => {
  const title = state.draft.title.trim()
  const text = state.draft.text.trim()
  if (!title) return
  if (state.draft.inputType === 'text' && !text) return

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
    promptId: state.draft.promptId || null,
    inputType: state.draft.inputType || 'text',
    templateId: state.draft.templateId || null,
    formData: state.draft.formData || {}
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

const updateTemplateSelection = (templateId) => {
  state.draft.templateId = templateId || null
  const tmpl = state.templates.find((t) => t.id === templateId)
  if (tmpl) {
    const nextFormData = {}
    tmpl.fields.forEach((f) => {
      nextFormData[f.name] = state.draft.formData?.[f.name] || ''
    })
    state.draft.formData = nextFormData
  }
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

// Form templates CRUD
const openTemplateModal = () => {
  state.templateModalOpen = true
  if (state.templates.length) {
    const first = state.templates[0]
    state.selectedTemplateId = first.id
    state.templateDraft = { ...first, fields: [...first.fields] }
    state.templateMode = 'view'
  } else {
    state.selectedTemplateId = null
    state.templateDraft = { name: '', description: '', fields: [] }
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
  state.templateDraft = { ...found, fields: [...found.fields] }
}

const startTemplateCreate = () => {
  state.templateMode = 'create'
  state.selectedTemplateId = null
  state.templateDraft = { name: '', description: '', fields: [] }
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
      state.templateDraft = { ...first, fields: [...first.fields] }
      state.templateMode = 'view'
    } else {
      state.templateDraft = { name: '', description: '', fields: [] }
      state.templateMode = 'view'
    }
    return
  }
  if (state.templateMode === 'edit') {
    const current = state.templates.find((t) => t.id === state.selectedTemplateId)
    if (current) state.templateDraft = { ...current, fields: [...current.fields] }
    state.templateMode = 'view'
  }
}

const saveTemplate = () => {
  const name = state.templateDraft.name.trim()
  if (!name) return
  const id = state.selectedTemplateId || Math.random().toString(36).slice(2, 11)

  const fields = Array.isArray(state.templateDraft.fields) ? state.templateDraft.fields : []
  const normalizedFields = fields.map((f, idx) => {
    const options = toOptionObjects(f.optionsInput ?? f.options)
    return {
      id: f.id || `${id}-${idx}`,
      name: (f.name || '').trim(),
      label: (f.label || '').trim(),
      type: f.type || 'text',
      required: Boolean(f.required),
      options,
      optionsInput: (f.optionsInput ?? options.map((o) => o.label || o.value || '').join('\n')) || ''
    }
  })

  const hasEmpty = normalizedFields.some((f) => !f.name || !f.label)
  if (hasEmpty) {
    alert('라벨과 필드명은 비워둘 수 없습니다.')
    return
  }
  const selectWithoutOptions = normalizedFields.some((f) => f.type === 'select' && (!Array.isArray(f.options) || f.options.length === 0))
  if (selectWithoutOptions) {
    alert('select 필드는 옵션을 한 개 이상 입력해야 합니다.')
    return
  }

  const payload = {
    id,
    name,
    description: state.templateDraft.description || '',
    schemaVersion: state.templateDraft.schemaVersion || 1,
    fields: normalizedFields
  }
  const idx = state.templates.findIndex((t) => t.id === id)
  if (idx >= 0) state.templates.splice(idx, 1, payload)
  else state.templates.unshift(payload)
  persistTemplates()
  state.selectedTemplateId = id
  state.templateMode = 'view'
}

const deleteTemplate = () => {
  if (!state.selectedTemplateId) return
  if (!confirm('삭제하시겠습니까?')) return
  state.templates = state.templates.filter((t) => t.id !== state.selectedTemplateId)
  persistTemplates()
  if (state.templates.length) {
    const first = state.templates[0]
    state.selectedTemplateId = first.id
    state.templateDraft = { ...first, fields: [...first.fields] }
    state.templateMode = 'view'
  } else {
    state.selectedTemplateId = null
    state.templateDraft = { name: '', description: '', fields: [] }
    state.templateMode = 'create'
  }
}

const applyTemplate = () => {
  if (!state.selectedTemplateId) return
  updateTemplateSelection(state.selectedTemplateId)
  state.templateModalOpen = false
}

const addTemplateField = () => {
  const next = {
    id: Math.random().toString(36).slice(2, 11),
    name: '',
    label: '',
    type: 'text',
    required: false,
    options: [],
    optionsInput: ''
  }
  state.templateDraft.fields = [...(state.templateDraft.fields || []), next]
}

const updateTemplateField = (id, partial) => {
  state.templateDraft.fields = (state.templateDraft.fields || []).map((f) => (f.id === id ? { ...f, ...partial } : f))
}

const removeTemplateField = (id) => {
  state.templateDraft.fields = (state.templateDraft.fields || []).filter((f) => f.id !== id)
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
  loadTemplates()
})
</script>

<template>
  <div class="prompt-manager two-col">
    <InputList
      :items="state.userInputs"
      :prompts="state.prompts"
      :selected-id="state.selectedInputId"
      @create="startCreate"
      @select="selectInput"
    />

    <InputDetail
      :mode="state.detailMode"
      :draft="state.draft"
      :selected-input="selectedInput"
      :prompts="state.prompts"
      :templates="state.templates"
      :model-families="modelFamilies"
      :current-model-versions="currentModelVersions"
      :view-model-versions="viewModelVersions"
      :detail-title="detailTitle"
      :detail-eyebrow="detailEyebrow"
      @change-draft="updateDraft"
      @save="saveInput"
      @cancel="cancelEdit"
      @start-edit="startEdit"
      @delete="deleteInput"
      @open-prompt-modal="openPromptModal"
      @open-template-modal="openTemplateModal"
      @update-selected-model="updateSelectedModel"
      @update-selected-version="updateSelectedVersion"
      @update-selected-prompt="updateSelectedPrompt"
      @update-template="updateTemplateSelection"
    />
  </div>

  <PromptSelectorModal
    :open="state.promptModalOpen"
    :prompts="state.prompts"
    :selected-prompt-id="state.selectedPromptId"
    :prompt-draft="state.promptDraft"
    :prompt-mode="state.promptMode"
    @close="closePromptModal"
    @start-create="startPromptCreate"
    @select="selectPromptForModal"
    @start-edit="startPromptEdit"
    @cancel="cancelPromptEditOrCreate"
    @save="savePrompt"
    @delete="deletePrompt"
    @apply="applyPrompt"
    @change-draft="(partial) => (state.promptDraft = { ...state.promptDraft, ...partial })"
  />

  <FormTemplateModal
    :open="state.templateModalOpen"
    :templates="state.templates"
    :selected-template-id="state.selectedTemplateId"
    :template-draft="state.templateDraft"
    :template-mode="state.templateMode"
    @close="closeTemplateModal"
    @start-create="startTemplateCreate"
    @select="selectTemplateForModal"
    @start-edit="startTemplateEdit"
    @cancel="cancelTemplateEditOrCreate"
    @save="saveTemplate"
    @delete="deleteTemplate"
    @apply="applyTemplate"
    @add-field="addTemplateField"
    @update-field="updateTemplateField"
    @remove-field="removeTemplateField"
    @change-draft="(partial) => (state.templateDraft = { ...state.templateDraft, ...partial })"
  />
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

@media (max-width: 1100px) {
  .prompt-manager {
    grid-template-columns: 1fr;
  }
}
</style>
