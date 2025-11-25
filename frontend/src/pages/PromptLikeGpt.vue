<script setup>
import ChatWindow from '../components/ChatWindow.vue'
</script>

<template>
  <div class="page">
    <h1>Prompt Like GPT</h1>
    <p>Chat with AI using GPT-like prompts</p>
    <ChatWindow />
  </div>
</template>

<style scoped>
.page {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  height: 100%;
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
</style>
