<script setup>
import { ref } from 'vue'
import ChatWindow from '../components/ChatWindow.vue'
import PromptSelector from '../components/PromptSelector.vue'

const selectedPrompt = ref('prompt')
</script>

<template>
  <div class="page">
    <div class="content">
      <ChatWindow
        api-path="/api/openai/prompt-chat"
        :selected-prompt="selectedPrompt"
      />
      <PromptSelector
        :selected-prompt="selectedPrompt"
        @select-prompt="selectedPrompt = $event"
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
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.content {
  display: flex;
  flex: 1;
  overflow: hidden;
  gap: 16px;
}
</style>
