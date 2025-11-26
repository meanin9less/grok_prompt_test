<script setup>
import { ref, onMounted } from 'vue'
import { getPromptsList, getPromptContent } from '../services/promptService'

defineProps({
  selectedPrompt: {
    type: String,
    default: 'prompt'
  }
})

const emit = defineEmits(['select-prompt'])

const prompts = ref([])
const isLoading = ref(false)
const error = ref(null)
const selectedPromptContent = ref('')
const loadingContent = ref(false)
const showModal = ref(false)
const previewPromptKey = ref(null)

onMounted(async () => {
  isLoading.value = true
  try {
    const data = await getPromptsList()
    prompts.value = data.prompts || []
  } catch (err) {
    error.value = err.message || 'Failed to load prompts'
    console.error('Error loading prompts:', err)
  } finally {
    isLoading.value = false
  }
})

const loadPromptContent = async (promptKey) => {
  loadingContent.value = true
  try {
    const data = await getPromptContent(promptKey)
    selectedPromptContent.value = data.content || ''
  } catch (err) {
    console.error('Error loading prompt content:', err)
    selectedPromptContent.value = 'Failed to load prompt content'
  } finally {
    loadingContent.value = false
  }
}

const handlePreviewPrompt = async (promptKey) => {
  previewPromptKey.value = promptKey
  showModal.value = true
  await loadPromptContent(promptKey)
}

const handleApply = () => {
  emit('select-prompt', previewPromptKey.value)
  closeModal()
}

const closeModal = () => {
  showModal.value = false
  previewPromptKey.value = null
  selectedPromptContent.value = ''
}
</script>

<template>
  <div class="prompt-selector">
    <div class="selector-header">
      <h3>📋 System Prompts</h3>
    </div>

    <div v-if="isLoading" class="loading">
      <div class="spinner"></div>
      <p>Loading prompts...</p>
    </div>

    <div v-else-if="error" class="error">
      <p>⚠️ {{ error }}</p>
    </div>

    <div v-else-if="prompts.length === 0" class="empty">
      <p>No prompts available</p>
    </div>

    <div v-else class="content">
      <div class="prompts-list">
        <button
          v-for="prompt in prompts"
          :key="prompt"
          :class="['prompt-item', { active: selectedPrompt === prompt }]"
          @click="handlePreviewPrompt(prompt)"
        >
          <span class="prompt-name">{{ prompt }}</span>
        </button>
      </div>
    </div>
  </div>

  <!-- Modal Popup -->
  <div v-if="showModal" class="modal-overlay" @click="closeModal">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>📝 {{ previewPromptKey }}</h3>
        <button class="close-btn" @click="closeModal">✕</button>
      </div>

      <div class="modal-body">
        <div v-if="loadingContent" class="loading-content">
          <div class="spinner-small"></div>
          <p>Loading...</p>
        </div>
        <div v-else class="prompt-content-text">
          {{ selectedPromptContent }}
        </div>
      </div>

      <div class="modal-footer">
        <button class="cancel-btn" @click="closeModal">Cancel</button>
        <button class="apply-btn" @click="handleApply">Apply</button>
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

.content {
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
}

.prompts-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.prompt-item {
  padding: 12px;
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
  text-align: left;
  font-size: 13px;
  transition: all 0.2s;
  color: #555;
  font-weight: 500;
}

.prompt-item:hover {
  background-color: #f9f9f9;
  border-color: #007bff;
  color: #007bff;
}

.prompt-item.active {
  background-color: #007bff;
  border-color: #007bff;
  color: white;
}

.prompt-name {
  display: block;
  word-break: break-word;
}

.loading,
.error,
.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  color: #999;
  font-size: 13px;
  gap: 8px;
}

.error {
  color: #d32f2f;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #ddd;
  border-top-color: #007bff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 스크롤바 스타일 */
.prompts-list::-webkit-scrollbar {
  width: 6px;
}

.prompts-list::-webkit-scrollbar-track {
  background: transparent;
}

.prompts-list::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 3px;
}

.prompts-list::-webkit-scrollbar-thumb:hover {
  background: #999;
}

/* Modal Styles */
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
  max-width: 600px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  padding: 20px;
  border-bottom: 1px solid #ddd;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #f9f9f9;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
  padding: 0;
  width: 32px;
  height: 32px;
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
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.prompt-content-text {
  font-size: 13px;
  line-height: 1.8;
  color: #555;
  white-space: pre-wrap;
  word-break: break-word;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  gap: 8px;
  color: #999;
  font-size: 12px;
}

.spinner-small {
  width: 20px;
  height: 20px;
  border: 2px solid #ddd;
  border-top-color: #007bff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

.modal-footer {
  padding: 16px 20px;
  border-top: 1px solid #ddd;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  background-color: #f9f9f9;
}

.cancel-btn,
.apply-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-btn {
  background-color: #e9ecef;
  color: #333;
}

.cancel-btn:hover {
  background-color: #dee2e6;
}

.apply-btn {
  background-color: #007bff;
  color: white;
}

.apply-btn:hover {
  background-color: #0056b3;
}

.modal-body::-webkit-scrollbar {
  width: 6px;
}

.modal-body::-webkit-scrollbar-track {
  background: transparent;
}

.modal-body::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 3px;
}

.modal-body::-webkit-scrollbar-thumb:hover {
  background: #999;
}
</style>
