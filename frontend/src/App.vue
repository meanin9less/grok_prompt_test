<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()
</script>

<template>
  <div id="app">
    <header class="header">
      <nav class="nav">
        <router-link
          to="/"
          class="tab"
          :class="{ active: route.path === '/' }"
        >
          PromptGrok
        </router-link>
        <router-link
          to="/prompt-gpt"
          class="tab"
          :class="{ active: route.path === '/prompt-gpt' }"
        >
          PromptGpt
        </router-link>
        <router-link
          to="/prompt-gemini"
          class="tab"
          :class="{ active: route.path === '/prompt-gemini' }"
        >
          PromptGemini
        </router-link>
      </nav>
    </header>
    <main class="content">
      <router-view />
    </main>
  </div>
</template>

<style scoped>

#app{
  padding: 0 50px;
}

.header {
  width: 80%;
  padding: 0;
  margin: 0 auto;
}

.nav {
  display: flex;
  gap: 5px;
}

.tab {
  flex: 1;
  padding: 16px;
  text-decoration: none;
  color: #000;
  text-align: center;
  cursor: pointer;
  border-bottom: 3px solid transparent;
  transition: all 0.3s ease;
  border: 1px solid #000;
}

.tab:hover {
  background-color: #555;
}

.tab.active {
  background-color: #007bff;
}

.content {
  flex: 1;
  overflow-y: auto;
  width: 80%;
  margin: 0 auto;
}
</style>