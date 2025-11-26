<script setup>
import { ref, onMounted, computed } from 'vue'
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

const handleSelectPrompt = async (promptKey) => {
  emit('select-prompt', promptKey)
  await loadPromptContent(promptKey)
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
          @click="handleSelectPrompt(prompt)"
        >
          <span class="prompt-name">{{ prompt }}</span>
        </button>
      </div>

      <div class="content-divider"></div>

      <div class="prompt-content-section">
        <div class="content-header">
          <h4>📝 Content</h4>
        </div>

        <div v-if="loadingContent" class="loading-content">
          <div class="spinner-small"></div>
          <p>Loading...</p>
        </div>

        <div v-else class="prompt-content">
          {{ selectedPromptContent || 'Select a prompt to view its content' }}
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
  max-height: 40%;
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

.content-divider {
  height: 1px;
  background-color: #ddd;
  margin: 0;
}

.prompt-content-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-color: #fff;
}

.content-header {
  padding: 12px 16px;
  border-bottom: 1px solid #ddd;
  background-color: #f9f9f9;
}

.content-header h4 {
  margin: 0;
  font-size: 14px;
  color: #333;
  font-weight: 600;
}

.prompt-content {
  flex: 1;
  padding: 12px 16px;
  overflow-y: auto;
  font-size: 12px;
  line-height: 1.6;
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
  width: 16px;
  height: 16px;
  border: 2px solid #ddd;
  border-top-color: #007bff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

.prompt-content::-webkit-scrollbar {
  width: 6px;
}

.prompt-content::-webkit-scrollbar-track {
  background: transparent;
}

.prompt-content::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 3px;
}

.prompt-content::-webkit-scrollbar-thumb:hover {
  background: #999;
}
</style>
