<script setup>
import { ref, onMounted } from 'vue'
import { getPromptsList } from '../services/grokApi'

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

const handleSelectPrompt = (promptKey) => {
  emit('select-prompt', promptKey)
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

    <div v-else class="prompts-list">
      <button
        v-for="prompt in prompts"
        :key="prompt"
        :class="['prompt-item', { active: selectedPrompt === prompt }]"
        @click="handleSelectPrompt(prompt)"
      >
        <span class="prompt-name">{{ prompt }}</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.prompt-selector {
  display: flex;
  flex-direction: column;
  width: 250px;
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
</style>
