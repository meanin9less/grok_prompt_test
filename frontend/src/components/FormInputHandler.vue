<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useCustomForms } from '../composables/useCustomForms'

const props = defineProps({
  selectedFormId: {
    type: String,
    default: null
  }
})

const emit = defineEmits(['form-input-ready'])

const { getForm, saveFormInput, getFormInputs, getInput, removeInput, updateFieldValue } = useCustomForms()

const currentFormId = ref(props.selectedFormId)
const selectedForm = computed(() => {
  if (!currentFormId.value) return null
  return getForm(currentFormId.value)
})

const formInputValues = ref({})
const savedInputsList = ref([])
const showSavedInputs = ref(false)

// 폼 필드 초기화
const initializeFormInputs = () => {
  if (!selectedForm.value) {
    formInputValues.value = {}
    return
  }

  const inputs = {}
  selectedForm.value.fields.forEach(field => {
    inputs[field.id] = field.value || ''
  })
  formInputValues.value = inputs
}

// 입력값 업데이트
const handleFieldChange = (fieldId, value) => {
  formInputValues.value[fieldId] = value
}

// 입력값을 문자열로 변환
const formatFormInput = () => {
  if (!selectedForm.value) return ''

  const lines = selectedForm.value.fields.map(field => {
    const value = formInputValues.value[field.id] || ''
    return `${field.name}: ${value}`
  })

  return lines.join('\n')
}

// 입력값 저장
const handleSaveInput = () => {
  if (!currentFormId.value || !selectedForm.value) return

  const inputData = {}
  selectedForm.value.fields.forEach(field => {
    inputData[field.name] = formInputValues.value[field.id] || ''
  })

  saveFormInput(currentFormId.value, inputData)
  loadSavedInputs()
  alert('입력값이 저장되었습니다.')
}

// 저장된 입력값 로드
const handleLoadInput = (inputId) => {
  if (!currentFormId.value) return

  const input = getInput(currentFormId.value, inputId)
  if (!input) return

  // 입력값을 폼에 채우기
  selectedForm.value.fields.forEach(field => {
    const value = input.data[field.name] || ''
    formInputValues.value[field.id] = value
  })

  showSavedInputs.value = false
}

// 저장된 입력값 삭제
const handleDeleteInput = (inputId) => {
  if (confirm('이 입력값을 삭제하시겠습니까?')) {
    removeInput(currentFormId.value, inputId)
    loadSavedInputs()
  }
}

// 저장된 입력값 목록 로드
const loadSavedInputs = () => {
  if (!currentFormId.value) {
    savedInputsList.value = []
    return
  }

  savedInputsList.value = getFormInputs(currentFormId.value)
}

// 입력값을 채팅에 전송
const handleSendInput = () => {
  const formattedInput = formatFormInput()
  if (!formattedInput.trim()) {
    alert('입력한 항목이 없습니다.')
    return
  }

  emit('form-input-ready', {
    formId: currentFormId.value,
    formName: selectedForm.value.name,
    input: formattedInput
  })

  // 입력값 초기화
  initializeFormInputs()
}

// 입력값 초기화
const handleClearInput = () => {
  initializeFormInputs()
}

watch(() => props.selectedFormId, (newFormId) => {
  currentFormId.value = newFormId
  initializeFormInputs()
  loadSavedInputs()
})

onMounted(() => {
  initializeFormInputs()
  loadSavedInputs()
})
</script>

<template>
  <div class="form-input-handler">
    <div v-if="!currentFormId || !selectedForm" class="no-form-message">
      <p>폼을 선택하세요</p>
    </div>

    <div v-else class="form-inputs">
      <!-- 폼 이름 -->
      <div class="form-name">
        <h4>{{ selectedForm.name }}</h4>
      </div>

      <!-- 입력 필드 -->
      <div class="input-fields">
        <div v-for="field in selectedForm.fields" :key="field.id" class="field-input">
          <label :for="`field-${field.id}`" class="field-label">{{ field.name }}</label>
          <input
            :id="`field-${field.id}`"
            :value="formInputValues[field.id]"
            @input="handleFieldChange(field.id, $event.target.value)"
            type="text"
            class="field-text-input"
            :placeholder="`${field.name} 입력`"
          />
        </div>
      </div>

      <!-- 액션 버튼 -->
      <div class="action-buttons">
        <button class="btn-save" @click="handleSaveInput" title="입력값 저장">
          💾 저장
        </button>
        <button class="btn-clear" @click="handleClearInput" title="입력값 초기화">
          🔄 초기화
        </button>
        <button
          class="btn-history"
          @click="showSavedInputs = !showSavedInputs"
          title="저장된 입력값 보기"
          v-if="savedInputsList.length > 0"
        >
          📚 기록 ({{ savedInputsList.length }})
        </button>
      </div>

      <!-- 저장된 입력값 목록 -->
      <div v-if="showSavedInputs && savedInputsList.length > 0" class="saved-inputs-section">
        <h5>저장된 입력값</h5>
        <div class="saved-inputs-list">
          <div v-for="(savedInput, index) in savedInputsList" :key="savedInput.id" class="saved-input-item">
            <div class="saved-input-preview">
              <span class="saved-input-num">{{ savedInputsList.length - index }}</span>
              <span class="saved-input-date">
                {{ new Date(savedInput.savedAt).toLocaleDateString() }}
              </span>
            </div>
            <div class="saved-input-actions">
              <button
                class="btn-small btn-load"
                @click="handleLoadInput(savedInput.id)"
                title="로드"
              >
                ↩️
              </button>
              <button
                class="btn-small btn-delete-input"
                @click="handleDeleteInput(savedInput.id)"
                title="삭제"
              >
                🗑️
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 전송 버튼 -->
      <div class="send-section">
        <button class="btn-send" @click="handleSendInput">
          ✈️ 메시지로 전송
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.form-input-handler {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.no-form-message {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
  color: #999;
  font-size: 13px;
}

.form-inputs {
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
  padding: 8px;
}

.form-name {
  padding: 8px 0;
  margin-bottom: 8px;
  border-bottom: 1px solid #ddd;
}

.form-name h4 {
  margin: 0;
  font-size: 13px;
  color: #333;
  font-weight: 600;
}

.input-fields {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 8px;
  padding-right: 4px;
}

.field-input {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.field-label {
  font-size: 11px;
  font-weight: 600;
  color: #555;
}

.field-text-input {
  padding: 6px 8px;
  border: 1px solid #ddd;
  border-radius: 3px;
  font-size: 12px;
  transition: border-color 0.2s;
}

.field-text-input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.1);
}

.action-buttons {
  display: flex;
  gap: 4px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.btn-save,
.btn-clear,
.btn-history {
  flex: 1;
  padding: 6px 8px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 3px;
  font-size: 11px;
  cursor: pointer;
  transition: background-color 0.2s;
  white-space: nowrap;
  min-width: 60px;
}

.btn-save:hover {
  background-color: #0056b3;
}

.btn-clear {
  background-color: #6c757d;
}

.btn-clear:hover {
  background-color: #5a6268;
}

.btn-history {
  background-color: #17a2b8;
}

.btn-history:hover {
  background-color: #138496;
}

.saved-inputs-section {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  padding: 8px;
  background-color: #f9f9f9;
  border-radius: 3px;
  margin-bottom: 8px;
}

.saved-inputs-section h5 {
  margin: 0 0 6px 0;
  font-size: 11px;
  font-weight: 600;
  color: #555;
}

.saved-inputs-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.saved-input-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px;
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 2px;
}

.saved-input-preview {
  display: flex;
  align-items: center;
  gap: 6px;
  flex: 1;
}

.saved-input-num {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background-color: #e9ecef;
  border-radius: 50%;
  font-size: 10px;
  font-weight: 600;
  color: #555;
}

.saved-input-date {
  font-size: 10px;
  color: #999;
}

.saved-input-actions {
  display: flex;
  gap: 2px;
}

.btn-small {
  padding: 2px 4px;
  background: none;
  border: 1px solid #ddd;
  border-radius: 2px;
  font-size: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-small:hover {
  background-color: #e9ecef;
}

.btn-delete-input:hover {
  background-color: #ff6b6b;
  border-color: #ff6b6b;
  color: white;
}

.send-section {
  display: flex;
  gap: 4px;
}

.btn-send {
  flex: 1;
  padding: 8px 12px;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 3px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-send:hover {
  background-color: #218838;
}

.input-fields::-webkit-scrollbar {
  width: 6px;
}

.input-fields::-webkit-scrollbar-track {
  background: transparent;
}

.input-fields::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 3px;
}

.input-fields::-webkit-scrollbar-thumb:hover {
  background: #999;
}

.saved-inputs-list::-webkit-scrollbar {
  width: 6px;
}

.saved-inputs-list::-webkit-scrollbar-track {
  background: transparent;
}

.saved-inputs-list::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 3px;
}

.saved-inputs-list::-webkit-scrollbar-thumb:hover {
  background: #999;
}
</style>