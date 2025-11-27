<script setup>
import { ref, provide } from 'vue'
import ChatWindow from '../components/ChatWindow.vue'
import PromptSelector from '../components/PromptSelector.vue'
import { useCustomForms } from '../composables/useCustomForms'
import { useRouter } from 'vue-router'

const router = useRouter()
const selectedPrompt = ref('prompt')
const selectedFormId = ref(null)
const chatWindowRef = ref(null)
const currentApiPath = ref('/api/grok/prompt-chat')

// 공유 폼 인스턴스 제공
const customFormsInstance = useCustomForms()
provide('customForms', customFormsInstance)

const handleSelectForm = (formId) => {
  selectedFormId.value = formId
}

const handleChangeApi = (apiPath) => {
  // API 경로에 따라 페이지 이동
  if (apiPath.includes('/openai/')) {
    router.push('/prompt-gpt')
  } else if (apiPath.includes('/gemini/')) {
    router.push('/prompt-gemini')
  } else if (apiPath.includes('/grok/')) {
    currentApiPath.value = apiPath
  }
}

const handleClearForm = () => {
  selectedFormId.value = null
}

const handleApplyPrompt = (promptContent) => {
  if (chatWindowRef.value) {
    chatWindowRef.value.setInputMessage(promptContent)
  }
}

const handleFormDeleted = (formId) => {
  // 삭제된 폼이 현재 선택된 폼이면 선택 해제
  if (selectedFormId.value === formId) {
    selectedFormId.value = null
  }
}
</script>

<template>
  <div class="page">
    <div class="content">
      <ChatWindow
        ref="chatWindowRef"
        :api-path="currentApiPath"
        :selected-prompt="selectedPrompt"
        :selected-form-id="selectedFormId"
        @clear-form="handleClearForm"
        @change-api="handleChangeApi"
      />
      <PromptSelector
        :selected-prompt="selectedPrompt"
        :custom-forms="customFormsInstance"
        @select-prompt="selectedPrompt = $event"
        @select-form="handleSelectForm"
        @apply-prompt="handleApplyPrompt"
        @form-deleted="handleFormDeleted"
      />
    </div>
  </div>
</template>

<style scoped>
.page {
  display: flex;
  justify-content: center;
  height: 100%;
  padding: 24px 16px;
  background-color: #f5f5f5;
  box-sizing: border-box;
}

.content {
  display: flex;
  flex: 1;
  max-width: 1200px;
  width: 100%;
  justify-content: space-evenly;
  gap: 0;
  padding: 16px;
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

@media (max-width: 960px) {
  .content {
    flex-direction: column;
  }
}
</style>
