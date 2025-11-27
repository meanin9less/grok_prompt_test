<script setup>
import { computed, reactive, watch } from 'vue'

const SYSTEM_KEY = 'studio_system_prompts'

const props = defineProps({
  systemPromptLabel: {
    type: String,
    default: ''
  },
  inputPromptLabel: {
    type: String,
    default: ''
  },
  selectedProvider: {
    type: String,
    default: 'grok'
  },
  selectedModel: {
    type: String,
    default: ''
  },
  disabled: {
    type: Boolean,
    default: false
  },
  readyForRun: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:provider', 'update:model', 'update:options', 'execute'])

const state = reactive({
  showPersonaModal: false,
  systemPrompts: [],
  searchText: '',
  selectedPersonaTitle: ''
})

const loadSystemPrompts = () => {
  try {
    state.systemPrompts = JSON.parse(localStorage.getItem(SYSTEM_KEY) || '[]')
  } catch (err) {
    state.systemPrompts = []
  }
}

const filteredPrompts = computed(() => {
  if (!state.searchText.trim()) return state.systemPrompts
  return state.systemPrompts.filter(
    (p) =>
      p.title.toLowerCase().includes(state.searchText.toLowerCase()) ||
      p.content.toLowerCase().includes(state.searchText.toLowerCase())
  )
})

loadSystemPrompts()

const modelFamilies = [
  {
    id: 'gpt',
    label: 'ChatGPT',
    description: '고품질 텍스트, 분석, 생성에 최적화',
    badge: 'OpenAI',
    subModels: ['gpt-4.1', 'gpt-4.1-mini', 'gpt-4o', 'gpt-3.5-turbo']
  },
  {
    id: 'gemini',
    label: 'Gemini',
    description: '멀티모달/실시간 응답에 강점',
    badge: 'Google',
    subModels: ['gemini-2.5-pro', 'gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-1.5-pro']
  },
  {
    id: 'grok',
    label: 'Grok',
    description: '빠르고 거친 스타일의 응답',
    badge: 'xAI',
    subModels: ['grok-4-1-fast-reasoning', 'grok-4-1-fast-non-reasoning', 'grok-3']
  }
]

const generationOptions = reactive({
  temperature: 0.7,
  maxTokens: 1024,
  topP: 0.95,
  systemOverride: ''
})

watch(
  generationOptions,
  () => emit('update:options', { ...generationOptions }),
  { deep: true }
)

const activeFamily = computed(() => modelFamilies.find((item) => item.id === props.selectedProvider) || modelFamilies[0])
const subModelOptions = computed(() => activeFamily.value?.subModels || [])

watch(
  () => props.selectedProvider,
  (next) => {
    const family = modelFamilies.find((item) => item.id === next)
    if (family && !family.subModels.includes(props.selectedModel)) {
      emit('update:model', family.subModels[0])
    }
  },
  { immediate: true }
)

const handleRun = () => emit('execute')
</script>

<template>
  <div class="model-panel" :class="{ disabled }">
    <div class="content-wrapper">
      <div class="control-group">
        <label>API 선택</label>
        <select
          :value="selectedProvider"
          @change="emit('update:provider', $event.target.value)"
          :disabled="disabled"
        >
          <option v-for="family in modelFamilies" :key="family.id" :value="family.id">
            {{ family.label }}
          </option>
        </select>
      </div>

      <div class="control-group">
        <label>모델 선택</label>
        <select
          :value="selectedModel"
          @change="emit('update:model', $event.target.value)"
          :disabled="disabled"
        >
          <option v-for="sub in subModelOptions" :key="sub" :value="sub">
            {{ sub }}
          </option>
        </select>
      </div>

      <div class="control-group">
        <label>Temperature ({{ generationOptions.temperature }})</label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.05"
          v-model.number="generationOptions.temperature"
          :disabled="disabled"
        />
      </div>

      <div class="control-group">
        <label>페르소나 설정</label>
        <button class="select-btn" :class="{ selected: state.selectedPersonaTitle }" :disabled="disabled" @click="state.showPersonaModal = true">
          {{ state.selectedPersonaTitle || '페르소나 목록' }}
        </button>
      </div>

      <button
        class="run-button"
        :disabled="disabled || !readyForRun"
        @click="handleRun"
      >
        요청 실행
      </button>

      <div class="run-status" :class="{ ready: readyForRun }">
        <span v-if="readyForRun">준비 완료</span>
        <span v-else>프롬프트 선택 필요</span>
      </div>
    </div>

    <teleport to="body">
      <div class="persona-modal" v-if="state.showPersonaModal">
        <div class="persona-modal-content">
          <div class="modal-header">
            <div>
              <p class="eyebrow">페르소나 선택</p>
              <h4>시스템 프롬프트 목록</h4>
            </div>
            <button class="close-btn" @click="state.showPersonaModal = false">✕</button>
          </div>

          <div class="search-row">
            <input v-model="state.searchText" placeholder="검색 / 태그 필터" />
          </div>

          <div class="list">
            <div
              v-for="prompt in filteredPrompts"
              :key="prompt.id"
              class="list-item"
              @click="() => { generationOptions.systemOverride = prompt.content; state.selectedPersonaTitle = prompt.title; state.showPersonaModal = false }"
            >
              <div>
                <p class="title">{{ prompt.title }}</p>
                <p class="preview">{{ prompt.content }}</p>
              </div>
            </div>
            <div v-if="filteredPrompts.length === 0" class="empty">페르소나가 없습니다.</div>
          </div>
        </div>
      </div>
    </teleport>
  </div>
</template>

<style scoped>
.model-panel {
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  color: #e6ecff;
  height: 100%;
  width: 100%;
  box-sizing: border-box;
}

.model-panel::after {
  display: none;
}

.model-panel.disabled {
  opacity: 0.55;
  pointer-events: none;
}

.content-wrapper {
  display: flex;
  flex-direction: column;
  gap: 14px;
  width: 230px;
  max-width: 280px;
  padding: 15px;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.control-group label {
  font-size: 12px;
  color: rgba(230, 236, 255, 0.8);
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

select,
input {
  width: 100%;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.06);
  color: #e6ecff;
  padding: 10px;
  font-family: inherit;
  font-size: 13px;
  outline: none;
  transition: border-color 0.2s ease, background-color 0.2s ease;
  box-sizing: border-box;
}

select:focus,
input:focus {
  border-color: rgba(99, 179, 255, 0.9);
  background: rgba(255, 255, 255, 0.1);
}

input[type='range'] {
  padding: 0;
}

.select-btn {
  width: 100%;
  padding: 10px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.06);
  color: #e6ecff;
  font-size: 13px;
  cursor: pointer;
  transition: border-color 0.2s ease, background-color 0.2s ease;
  font-family: inherit;
}

.select-btn:hover:not(:disabled) {
  border-color: rgba(99, 179, 255, 0.7);
  background: rgba(255, 255, 255, 0.1);
}

.select-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.run-button {
  padding: 12px 18px;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, #63b3ff 0%, #63ffdd 100%);
  color: #0b1221;
  font-weight: 700;
  font-size: 14px;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  width: 100%;
  margin-top: 8px;
}

.run-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(99, 179, 255, 0.4);
}

.run-button:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.run-status {
  font-size: 12px;
  color: rgba(230, 236, 255, 0.6);
  text-align: center;
  margin-top: 4px;
}

.run-status.ready {
  color: #9ce0ff;
}

.persona-modal {
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

.persona-modal-content {
  background: linear-gradient(135deg, rgba(12, 18, 32, 0.95), rgba(15, 23, 42, 0.95));
  border: 1px solid rgba(99, 179, 255, 0.2);
  border-radius: 16px;
  padding: 24px;
  width: 100%;
  max-width: 500px;
  height: 80vh;
  max-height: 600px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(99, 179, 255, 0.2);
}

.modal-header h4 {
  margin: 4px 0 0;
  font-size: 18px;
  font-weight: 700;
  color: #ffffff;
}

.eyebrow {
  margin: 0;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-size: 12px;
  color: #8fb5ff;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  color: #e6ecff;
  font-size: 24px;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s ease;
}

.close-btn:hover {
  color: #63b3ff;
}

.search-row {
  margin-bottom: 12px;
}

.search-row input {
  width: 100%;
  padding: 10px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.05);
  color: #e6ecff;
  box-sizing: border-box;
  font-size: 13px;
  outline: none;
  transition: border-color 0.2s ease;
}

.search-row input:focus {
  border-color: rgba(99, 179, 255, 0.6);
  background: rgba(255, 255, 255, 0.08);
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
  background: rgba(99, 179, 255, 0.12);
}

.title {
  margin: 0;
  font-weight: 700;
  font-size: 13px;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  color: #ffffff;
}

.preview {
  margin: 4px 0 0;
  white-space: normal;
  font-size: 11px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  color: rgba(230, 236, 255, 0.7);
}

.empty {
  text-align: center;
  color: rgba(230, 236, 255, 0.6);
  padding: 12px;
  font-size: 12px;
}
</style>
