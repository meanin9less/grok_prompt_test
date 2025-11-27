<script setup>
import { ref, nextTick, watch, defineProps, defineEmits, onMounted, computed, inject } from 'vue'
import { useChat } from '../composables/useChat'
import { useChatHistory } from '../composables/useChatHistory'
import { useChatMarkdown } from '../composables/useChatMarkdown'
import { useCustomForms } from '../composables/useCustomForms'

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
  },
  selectedFormId: {
    type: String,
    default: null
  }
})

const emit = defineEmits(['clear-form', 'change-api'])

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

// 폼 관리 - inject로 제공된 인스턴스 사용, 없으면 새로 생성
const injectedCustomForms = inject('customForms', null)
const customForms = injectedCustomForms || useCustomForms()
const { getForm, addFieldToForm, removeFieldFromForm, updateFormName, updateFieldValue, forms } = customForms
const currentFormInputs = ref({})
const newFieldName = ref('')

const selectedForm = computed(() => {
  if (!props.selectedFormId) return null
  return getForm(props.selectedFormId)
})

// selectedModel 변경 감지
watch(() => props.selectedModel, (newModel) => {
  chatState.selectedModel.value = newModel
})

// selectedPrompt 변경 감지
watch(() => props.selectedPrompt, (newPrompt) => {
  chatState.selectedPrompt.value = newPrompt
})

// selectedFormId 변경 감지 - 폼 필드 값을 currentFormInputs에 로드
watch(() => props.selectedFormId, (newFormId) => {
  console.log('[ChatWindow] selectedFormId 변경:', newFormId)
  console.log('[ChatWindow] 현재 forms:', forms.value)

  if (newFormId) {
    // selectedForm computed 대신 직접 getForm 호출
    const form = getForm(newFormId)
    console.log('[ChatWindow] getForm 결과:', form)

    if (form) {
      currentFormInputs.value = {}

      // 폼의 각 필드의 value를 currentFormInputs에 로드
      form.fields.forEach(field => {
        currentFormInputs.value[field.id] = field.value
      })

      console.log('[ChatWindow] 폼 로드 완료, currentFormInputs:', currentFormInputs.value)
    } else {
      console.log('[ChatWindow] getForm으로 폼을 찾지 못함')
    }
  } else {
    console.log('[ChatWindow] selectedFormId가 null')
  }
}, { immediate: false })

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
  const models = getModelList()
  if (!chatState.selectedModel.value && models.length) {
    chatState.selectedModel.value = models[0]
  }
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

// 폼 필드 추가 (빈 필드명으로 추가)
const handleAddField = () => {
  if (!props.selectedFormId) return

  // 빈 필드명으로 추가
  addFieldToForm(props.selectedFormId, '')
}

// 폼 필드 삭제
const handleDeleteField = (fieldId) => {
  if (!props.selectedFormId) return
  if (confirm('필드를 삭제하시겠습니까?')) {
    removeFieldFromForm(props.selectedFormId, fieldId)
    // 삭제된 필드의 입력값 제거
    delete currentFormInputs.value[fieldId]
  }
}

// 폼 저장 - 각 필드의 value 업데이트
const handleSaveFormValues = () => {
  console.log('[ChatWindow] handleSaveFormValues 호출됨')
  if (!props.selectedFormId || !selectedForm.value) return

  // 필드명이 비어있는지 확인
  const hasEmptyNames = selectedForm.value.fields.some(f => !f.name.trim())
  if (hasEmptyNames) {
    alert('모든 필드명을 입력해주세요.')
    return
  }

  // 각 필드의 value를 currentFormInputs의 값으로 업데이트
  selectedForm.value.fields.forEach(field => {
    const newValue = currentFormInputs.value[field.id] || ''
    console.log(`[ChatWindow] 필드 '${field.name}' 값 업데이트: '${field.value}' → '${newValue}'`)
    updateFieldValue(props.selectedFormId, field.id, newValue)
  })

  console.log('[ChatWindow] 모든 필드 값이 저장되었습니다')
}

// 폼 전송 - 필드명 검증 후 메시지 작성
const handleSendForm = () => {
  if (!selectedForm.value) return

  // 필드명이 비어있는지 확인
  const hasEmptyNames = selectedForm.value.fields.some(f => !f.name.trim())
  if (hasEmptyNames) {
    alert('모든 필드명을 입력해주세요.')
    return
  }

  // 폼 데이터를 메시지로 변환
  const lines = selectedForm.value.fields.map(f => `${f.name}: ${currentFormInputs.value[f.id] || ''}`).join('\n')
  chatState.inputMessage.value = `[${selectedForm.value.name}]\n${lines}`

  // 폼 선택 해제
  emit('clear-form')
}

// 폼 입력 처리
const handleFormInput = (data) => {
  if (!data || !data.input) return

  // 폼 입력 데이터를 메시지에 포함
  const formMessage = `[${data.formName}]\n${data.input}`
  chatState.inputMessage.value = formMessage

  // 자동 전송 (옵션: 수동 전송으로 변경 가능)
  // chatState.handleSendMessage()
}

// 외부에서 입력 메시지를 설정하는 메서드 (프롬프트 적용 시 사용)
const setInputMessage = (content) => {
  chatState.inputMessage.value = content
}

// 외부 컴포넌트에서 접근 가능하도록 expose
defineExpose({
  setInputMessage
})
</script>

<template>
  <div class="chat-window">
    <div class="chat-header">
      <div class="header-top">
        <h2>{{ getChatTitle() }}</h2>
        <div class="header-controls">
          <select
            :value="chatState.selectedModel.value || getModelList()[0] || ''"
            @change="handleModelChange"
            class="model-select"
          >
            <option v-for="model in getModelList()" :key="model" :value="model">
              {{ model }}
            </option>
          </select>
          <button class="clear-btn" @click="handleClearChat" :disabled="chatState.isLoading.value">
            Clear
          </button>
        </div>
      </div>

      <!-- API 선택 탭 -->
      <div class="api-tabs">
        <button
          :class="['api-tab', { active: props.apiPath === '/api/grok/prompt-chat' }]"
          @click="$emit('change-api', '/api/grok/prompt-chat')"
        >
          Grok
        </button>
        <button
          :class="['api-tab', { active: props.apiPath === '/api/openai/prompt-chat' }]"
          @click="$emit('change-api', '/api/openai/prompt-chat')"
        >
          GPT
        </button>
        <button
          :class="['api-tab', { active: props.apiPath === '/api/gemini/prompt-chat' }]"
          @click="$emit('change-api', '/api/gemini/prompt-chat')"
        >
          Gemini
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

    <!-- 일반 채팅 입력 -->
    <div v-if="!selectedForm" class="input-area">
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

    <!-- 폼 입력 영역 -->
    <div v-else class="form-input-area">
      <!-- 폼 헤더 -->
      <div class="form-header">
        <h4>{{ selectedForm.name }}</h4>
        <div class="form-header-buttons">
          <button class="btn-add-field-header" @click="handleAddField" title="필드 추가">
            ➕ 필드 추가
          </button>
          <button class="btn-back-to-chat" @click="$emit('clear-form')" title="채팅으로 돌아가기">
            💬 채팅
          </button>
        </div>
      </div>

      <!-- 폼 필드 영역 -->
      <div class="form-fields">
        <div v-if="selectedForm.fields.length === 0" class="empty-fields">
          필드가 없습니다. 위의 "➕ 필드 추가" 버튼으로 필드를 추가하세요.
        </div>

        <!-- 항상 필드명과 값을 수정할 수 있는 영역 -->
        <div v-for="field in selectedForm.fields" :key="field.id" class="form-field-wrapper">
          <!-- 필드명 수정 입력 -->
          <div class="field-header">
            <input
              :value="field.name"
              @blur="(e) => { field.name = e.target.value; forms = [...forms] }"
              type="text"
              class="field-name-input-inline"
              placeholder="필드명"
            />
            <button
              class="btn-delete-field"
              @click="handleDeleteField(field.id)"
              title="필드 삭제"
            >
              ✕
            </button>
          </div>

          <!-- 필드값 입력 -->
          <input
            :id="`field-${field.id}`"
            :value="currentFormInputs[field.id]"
            @input="currentFormInputs[field.id] = $event.target.value"
            type="text"
            class="form-input"
            :placeholder="`값 입력`"
          />
        </div>
      </div>

      <!-- 폼 액션 버튼 -->
      <div class="form-actions">
        <button
          class="form-btn form-save-btn"
          @click="handleSaveFormValues"
          title="입력값 저장"
        >
          💾 저장
        </button>
        <button
          class="form-btn form-send-btn"
          @click="handleSendForm"
          :disabled="chatState.isLoading.value"
          title="메시지로 전송"
        >
          ✈️ 전송
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
@import './ChatWindow.css';
</style>
