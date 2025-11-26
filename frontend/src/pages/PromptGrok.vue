<script setup>
import { ref } from 'vue'
import ChatWindow from '../components/ChatWindow.vue'
import PromptSelector from '../components/PromptSelector.vue'

const selectedModel = ref(null)
const selectedPrompt = ref('prompt')

const grokModels = ['grok-4-1-fast-reasoning', 'grok-4-1-fast-non-reasoning', 'grok-code-fast-1', 'grok-4-fast-reasoning', 'grok-4-fast-non-reasoning', 'grok-4-0709', 'grok-3-mini', 'grok-3']
</script>

<template>
  <div class="page">
    <div class="header">
      <h1>Prompt Grok</h1>
      <p>Chat with Grok using prompts</p>

      <div class="model-selector">
        <label for="grok-model">Select Model:</label>
        <select id="grok-model" v-model="selectedModel">
          <option value="">Default Model</option>
          <option v-for="model in grokModels" :key="model" :value="model">
            {{ model }}
          </option>
        </select>
      </div>
    </div>

    <div class="content">
      <PromptSelector
        :selected-prompt="selectedPrompt"
        @select-prompt="selectedPrompt = $event"
      />
      <ChatWindow
        api-path="/api/grok/prompt-chat"
        :selected-model="selectedModel"
        :selected-prompt="selectedPrompt"
      />
    </div>
  </div>
</template>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 0;
}

.header {
  padding: 20px;
  border-bottom: 1px solid #ddd;
  background-color: #fff;
}

h1 {
  margin: 0 0 8px 0;
  font-size: 28px;
  color: #333;
}

p {
  margin: 0 0 16px 0;
  color: #666;
}

.model-selector {
  display: flex;
  align-items: center;
  gap: 12px;
}

.model-selector label {
  font-weight: 600;
  color: #333;
}

.model-selector select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background-color: #fff;
  cursor: pointer;
  transition: border-color 0.3s;
}

.model-selector select:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.1);
}

.content {
  display: flex;
  flex: 1;
  overflow: hidden;
  gap: 0;
}
</style>
