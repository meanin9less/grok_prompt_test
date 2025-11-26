<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()
</script>

<template>
  <div id="app">
    <div class="title-section">
      <h1>AI 챗 인터페이스</h1>
      <p>Grok, GPT, Gemini</p>
    </div>

    <nav class="nav">
      <router-link
        to="/"
        class="tab"
        :class="{ active: route.path === '/' }"
      >
        🦎 Grok
      </router-link>
      <router-link
        to="/prompt-gpt"
        class="tab"
        :class="{ active: route.path === '/prompt-gpt' }"
      >
        🤖 GPT
      </router-link>
      <router-link
        to="/prompt-gemini"
        class="tab"
        :class="{ active: route.path === '/prompt-gemini' }"
      >
        ✨ Gemini
      </router-link>
    </nav>

    <main class="content">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
#app {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #fff;
}

.title-section {
  padding: 24px 0;
  text-align: center;
  border-bottom: 2px solid #ddd;
  background-color: #f9f9f9;
}

.title-section h1 {
  margin: 0 0 8px 0;
  font-size: 32px;
  color: #333;
  font-weight: 700;
}

.title-section p {
  margin: 0;
  font-size: 14px;
  color: #666;
}

.nav {
  display: flex;
  gap: 0;
  background-color: #fff;
  border-bottom: 1px solid #ddd;
  padding: 0 24px;
}

.tab {
  flex: 1;
  max-width: 200px;
  padding: 16px 24px;
  text-decoration: none;
  color: #666;
  text-align: center;
  cursor: pointer;
  border: none;
  border-bottom: 3px solid transparent;
  transition: all 0.3s ease;
  font-weight: 500;
  font-size: 15px;
}

.tab:hover {
  color: #007bff;
  background-color: #f5f5f5;
}

.tab.active {
  color: #007bff;
  border-bottom-color: #007bff;
}

.content {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  padding: 16px;
}
</style>