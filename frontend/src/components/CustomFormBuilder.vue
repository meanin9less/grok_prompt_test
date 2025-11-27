<script setup>
import { ref, computed } from 'vue'
import { useCustomForms } from '../composables/useCustomForms'

const props = defineProps({
  customForms: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['select-form', 'form-deleted'])

// prop으로 받은 customForms 사용, 없으면 새로 생성
const customFormsInstance = props.customForms || useCustomForms()
const { forms, createForm, deleteForm, getForm } = customFormsInstance

const showCreateModal = ref(false)
const newFormName = ref('')

const handleCreateForm = () => {
  if (!newFormName.value.trim()) return

  const newFormId = createForm(newFormName.value)
  newFormName.value = ''
  showCreateModal.value = false

  // 새로 생성된 폼 자동 선택
  if (newFormId) {
    emit('select-form', newFormId)
  }
}

const handleSelectForm = (formId) => {
  emit('select-form', formId)
}

const handleDeleteForm = (formId) => {
  if (confirm(`'${getForm(formId).name}' 폼을 삭제하시겠습니까?`)) {
    deleteForm(formId)
    emit('form-deleted', formId)
  }
}

const closeCreateModal = () => {
  showCreateModal.value = false
  newFormName.value = ''
}
</script>

<template>
  <div class="custom-form-builder">
    <!-- 폼 목록 섹션 -->
    <div class="forms-section">
      <div class="section-header">
        <h4>📋 나의 폼</h4>
        <button class="btn-new" @click="showCreateModal = true">+ 새 폼</button>
      </div>

      <div class="forms-list">
        <div v-if="forms.length === 0" class="empty-state">
          <p>생성된 폼이 없습니다.</p>
        </div>

        <div v-for="form in forms" :key="form.id" class="form-item">
          <div class="form-item-header" @click="handleSelectForm(form.id)">
            <span class="form-name">{{ form.name }}</span>
            <span class="field-count">{{ form.fields.length }} 항목</span>
          </div>
          <div class="form-item-actions">
            <button class="btn-small btn-delete" @click.stop="handleDeleteForm(form.id)" title="삭제">🗑️</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 폼 생성 모달 -->
    <div v-if="showCreateModal" class="modal-overlay" @click="closeCreateModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>새 폼 생성</h3>
          <button class="close-btn" @click="closeCreateModal">✕</button>
        </div>
        <div class="modal-body">
          <input
            v-model="newFormName"
            type="text"
            placeholder="폼 이름 입력 (예: 고객정보)"
            class="input-field"
            @keydown.enter="handleCreateForm"
            autofocus
          />
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="closeCreateModal">취소</button>
          <button class="btn-ok" @click="handleCreateForm">생성</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.custom-form-builder {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.forms-section {
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
  padding: 8px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  margin-bottom: 8px;
}

.section-header h4 {
  margin: 0;
  font-size: 13px;
  font-weight: 600;
  color: #333;
}

.btn-new {
  padding: 4px 8px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 3px;
  font-size: 11px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-new:hover {
  background-color: #0056b3;
}

.forms-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
  color: #999;
  font-size: 12px;
}

.form-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.form-item:hover {
  border-color: #007bff;
  background-color: #f9f9f9;
}

.form-item-header {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.form-name {
  font-size: 12px;
  font-weight: 500;
}

.field-count {
  font-size: 10px;
  opacity: 0.7;
}

.form-item-actions {
  display: flex;
  gap: 4px;
}

.btn-small {
  padding: 2px 6px;
  background: none;
  border: none;
  font-size: 12px;
  cursor: pointer;
  border-radius: 2px;
  transition: background-color 0.2s;
}

.btn-small:hover {
  background-color: rgba(0, 0, 0, 0.1);
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
  max-width: 400px;
  overflow: hidden;
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
}

.modal-footer {
  padding: 12px 16px;
  border-top: 1px solid #ddd;
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  background-color: #f9f9f9;
}

.forms-list::-webkit-scrollbar {
  width: 6px;
}

.forms-list::-webkit-scrollbar-track {
  background: transparent;
}

.forms-list::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 3px;
}

.forms-list::-webkit-scrollbar-thumb:hover {
  background: #999;
}
</style>
