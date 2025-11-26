<script setup>
import { ref } from 'vue'
import SystemPromptSelector from './SystemPromptSelector.vue'

defineProps({
  selectedPrompt: {
    type: String,
    default: 'prompt'
  }
})

const emit = defineEmits(['select-prompt'])

const activeTab = ref('system')
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
        System Prompts
      </button>
      <button
        :class="['tab-btn', { active: activeTab === 'custom' }]"
        @click="activeTab = 'custom'"
      >
        Custom
      </button>
    </div>

    <div class="tab-content">
      <SystemPromptSelector
        v-if="activeTab === 'system'"
        :selected-prompt="selectedPrompt"
        @select-prompt="$emit('select-prompt', $event)"
      />
      <div v-else-if="activeTab === 'custom'" class="custom-content">
        <p>Custom prompt content coming soon...</p>
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

.tabs-container {
  display: flex;
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
</style>
