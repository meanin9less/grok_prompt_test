<script setup>
import { ref, inject } from 'vue'
import { useCustomForms } from '../composables/useCustomForms'
import { useSavedPrompts } from '../composables/useSavedPrompts'
import SystemPromptSelector from './SystemPromptSelector.vue'
import CustomFormBuilder from './CustomFormBuilder.vue'

const props = defineProps({
  selectedPrompt: {
    type: String,
    default: 'prompt'
  },
  customForms: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['select-prompt', 'form-input', 'select-form', 'apply-prompt', 'form-deleted'])

// prop으로 받은 customForms 사용, 없으면 새로 생성
const customFormsInstance = props.customForms || useCustomForms()
const { forms, getForm, getFormInputs } = customFormsInstance
const { prompts, createPrompt, deletePrompt, updatePrompt, getPrompt } = useSavedPrompts()

const activeTab = ref('custom')
const selectedFormId = ref(null)
const showFormInput = ref(false)
const showPromptModal = ref(false)
const selectedPromptId = ref(null)
const showCreatePromptModal = ref(false)
const newPromptTitle = ref('')
const newPromptContent = ref('')
const editingPromptTitle = ref('')
const editingPromptContent = ref('')

const handleFormInputReady = (data) => {
  emit('form-input', data)
}

const handleBackToBuilder = () => {
  showFormInput.value = false
}

const handleFormDeleted = (formId) => {
  // 삭제된 폼이 현재 선택된 폼이면 선택 해제
  if (selectedFormId.value === formId) {
    selectedFormId.value = null
    emit('select-form', null)
  }
  // 상위 컴포넌트에 폼 삭제 이벤트 전파
  emit('form-deleted', formId)
}

// Saved Prompts 탭 - 프롬프트 목록에서 프롬프트 보기
const openPromptModal = (promptId) => {
  selectedPromptId.value = promptId
  const prompt = getPrompt(promptId)
  if (prompt) {
    editingPromptTitle.value = prompt.title
    editingPromptContent.value = prompt.content
  }
  showPromptModal.value = true
}

const closePromptModal = () => {
  showPromptModal.value = false
  selectedPromptId.value = null
  editingPromptTitle.value = ''
  editingPromptContent.value = ''
}

const handleSavePromptChanges = () => {
  if (selectedPromptId.value && editingPromptTitle.value.trim() && editingPromptContent.value.trim()) {
    updatePrompt(selectedPromptId.value, editingPromptTitle.value, editingPromptContent.value)
    closePromptModal()
  }
}

const handleDeletePrompt = (promptId) => {
  if (confirm('이 프롬프트를 삭제하시겠습니까?')) {
    deletePrompt(promptId)
  }
}

const handleApplyPrompt = (promptId) => {
  const prompt = getPrompt(promptId)
  if (prompt) {
    emit('apply-prompt', prompt.content)
  }
}

const handleCreatePrompt = () => {
  if (newPromptTitle.value.trim() && newPromptContent.value.trim()) {
    createPrompt(newPromptTitle.value, newPromptContent.value)
    newPromptTitle.value = ''
    newPromptContent.value = ''
    showCreatePromptModal.value = false
  }
}

const closeCreatePromptModal = () => {
  showCreatePromptModal.value = false
  newPromptTitle.value = ''
  newPromptContent.value = ''
}
</script>

<template>
  <div class="prompt-selector">
    <div class="selector-header">
      <h3>📋 Prompts & Settings</h3>
    </div>

    <div class="tabs-container">
      <button
        :class="['tab-btn', { active: activeTab === 'system' }]"
        @click="activeTab = 'system'"
      >
        시스템 프롬프트
      </button>
      <button
        :class="['tab-btn', { active: activeTab === 'custom' }]"
        @click="activeTab = 'custom'"
      >
        커스텀 폼
      </button>
      <button
        :class="['tab-btn', { active: activeTab === 'saved' }]"
        @click="activeTab = 'saved'"
      >
        유저 프롬프트
      </button>
    </div>

    <div class="tab-content">
      <SystemPromptSelector
        v-if="activeTab === 'system'"
        :selected-prompt="selectedPrompt"
        @select-prompt="$emit('select-prompt', $event)"
      />
      <div v-else-if="activeTab === 'custom'" class="custom-forms-wrapper">
        <CustomFormBuilder
          :custom-forms="customFormsInstance"
          @select-form="$emit('select-form', $event)"
          @form-deleted="handleFormDeleted"
        />
      </div>

      <!-- Saved Prompts 탭 -->
      <div v-else-if="activeTab === 'saved'" class="saved-prompts-tab">
        <div class="prompts-header">
          <button class="btn-create-prompt" @click="showCreatePromptModal = true">
            + 새 프롬프트
          </button>
        </div>

        <div v-if="prompts.length === 0" class="empty-saved">
          <p>저장된 프롬프트가 없습니다</p>
        </div>

        <div v-else class="saved-prompts-list">
          <div v-for="prompt in prompts" :key="prompt.id" class="prompt-item" @click="openPromptModal(prompt.id)">
            <div class="prompt-item-left">
              <h4 class="prompt-title">{{ prompt.title }}</h4>
              <p class="prompt-preview">{{ prompt.content.substring(0, 50) }}...</p>
            </div>
            <div class="prompt-item-actions" @click.stop>
              <button
                class="btn-apply"
                @click="handleApplyPrompt(prompt.id)"
                title="채팅에 적용"
              >
                적용
              </button>
              <button
                class="btn-delete"
                @click="handleDeletePrompt(prompt.id)"
                title="삭제"
              >
                🗑️
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 프롬프트 생성 모달 -->
    <div v-if="showCreatePromptModal" class="modal-overlay" @click="closeCreatePromptModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>새 프롬프트 생성</h3>
          <button class="close-btn" @click="closeCreatePromptModal">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>프롬프트 제목</label>
            <input
              v-model="newPromptTitle"
              type="text"
              placeholder="예: 창의적인 글쓰기"
              class="input-field"
            />
          </div>
          <div class="form-group">
            <label>프롬프트 내용</label>
            <textarea
              v-model="newPromptContent"
              placeholder="프롬프트 내용을 입력하세요..."
              class="textarea-field"
              rows="6"
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="closeCreatePromptModal">취소</button>
          <button class="btn-ok" @click="handleCreatePrompt">생성</button>
        </div>
      </div>
    </div>

    <!-- 프롬프트 수정 모달 -->
    <div v-if="showPromptModal" class="modal-overlay" @click="closePromptModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>프롬프트 수정</h3>
          <button class="close-btn" @click="closePromptModal">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>프롬프트 제목</label>
            <input
              v-model="editingPromptTitle"
              type="text"
              class="input-field"
            />
          </div>
          <div class="form-group">
            <label>프롬프트 내용</label>
            <textarea
              v-model="editingPromptContent"
              class="textarea-field"
              rows="6"
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="closePromptModal">취소</button>
          <button class="btn-ok" @click="handleSavePromptChanges">저장</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.prompt-selector {
  display: flex;
  flex-direction: column;
  width: 350px;
  background-color: #f5f5f5;
  border-right: 1px solid #ddd;
  height: 100%;
  overflow: hidden;
  border: 1px solid #ddd;
  border-radius: 5px;
}

.selector-header {
  padding: 16px;
  border-bottom: 1px solid #ddd;
  background-color: #fff;
}

.selector-header h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
  font-weight: 600;
}

.tabs-container {
  display: none;
  gap: 0;
  background-color: #fff;
  border-bottom: 1px solid #ddd;
}

.tab-btn {
  flex: 1;
  padding: 12px 16px;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  color: #666;
  transition: all 0.2s;
}

.tab-btn:hover {
  color: #007bff;
  background-color: #f9f9f9;
}

.tab-btn.active {
  color: #007bff;
  border-bottom-color: #007bff;
  background-color: transparent;
}

.tab-content {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.custom-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  color: #999;
  padding: 20px;
  text-align: center;
}

.custom-content p {
  margin: 0;
  font-size: 13px;
}

.custom-forms-wrapper {
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
}

.form-input-wrapper {
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
}

.btn-back {
  padding: 8px 12px;
  background-color: #6c757d;
  color: white;
  border: none;
  border-radius: 0;
  font-size: 12px;
  cursor: pointer;
  transition: background-color 0.2s;
  border-bottom: 1px solid #ddd;
}

.btn-back:hover {
  background-color: #5a6268;
}

.saved-prompts-tab {
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
  padding: 8px;
  gap: 8px;
}

.prompts-header {
  display: flex;
  gap: 8px;
}

.btn-create-prompt {
  padding: 8px 12px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  transition: background-color 0.2s;
}

.btn-create-prompt:hover {
  background-color: #0056b3;
}

.empty-saved {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
  color: #999;
  font-size: 13px;
}

.empty-saved p {
  margin: 0;
}

.saved-prompts-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.prompt-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 4px;
  transition: all 0.2s;
}

.prompt-item:hover {
  border-color: #007bff;
  background-color: #f9f9f9;
}

.prompt-item-left {
  flex: 1;
  min-width: 0;
}

.prompt-title {
  margin: 0 0 4px 0;
  font-size: 12px;
  font-weight: 600;
  color: #333;
}

.prompt-preview {
  margin: 0;
  font-size: 11px;
  color: #666;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.prompt-item-actions {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
  margin-left: 8px;
}

.btn-apply {
  padding: 4px 8px;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  font-size: 11px;
  font-weight: 600;
  transition: background-color 0.2s;
}

.btn-apply:hover {
  background-color: #218838;
}

.btn-edit {
  padding: 4px 8px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  font-size: 12px;
  transition: background-color 0.2s;
}

.btn-edit:hover {
  background-color: #0056b3;
}

.btn-delete {
  padding: 4px 6px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 12px;
  transition: opacity 0.2s;
}

.btn-delete:hover {
  opacity: 0.7;
}

.saved-prompts-list::-webkit-scrollbar {
  width: 6px;
}

.saved-prompts-list::-webkit-scrollbar-track {
  background: transparent;
}

.saved-prompts-list::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 3px;
}

.saved-prompts-list::-webkit-scrollbar-thumb:hover {
  background: #999;
}

/* 모달 스타일 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  width: 90%;
  max-width: 500px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  max-height: 80vh;
}

.modal-header {
  padding: 16px;
  border-bottom: 1px solid #ddd;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #f9f9f9;
}

.modal-header h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #999;
  padding: 0;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s;
}

.close-btn:hover {
  color: #333;
  background-color: #e9ecef;
}

.modal-body {
  padding: 16px;
  overflow-y: auto;
  flex: 1;
}

.form-group {
  margin-bottom: 16px;
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-size: 12px;
  font-weight: 600;
  color: #333;
}

.input-field,
.textarea-field {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: inherit;
  font-size: 13px;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.input-field:focus,
.textarea-field:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.1);
}

.textarea-field {
  resize: vertical;
}

.modal-footer {
  padding: 12px 16px;
  border-top: 1px solid #ddd;
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  background-color: #f9f9f9;
}

.btn-cancel {
  padding: 8px 16px;
  background-color: #6c757d;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  transition: background-color 0.2s;
}

.btn-cancel:hover {
  background-color: #5a6268;
}

.btn-ok {
  padding: 8px 16px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  transition: background-color 0.2s;
}

.btn-ok:hover {
  background-color: #0056b3;
}
</style>
