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
          BasicGrok
        </router-link>
        <router-link
          to="/about"
          class="tab"
          :class="{ active: route.path === '/about' }"
        >
          PromptGrok
        </router-link>
        <router-link
          to="/contact"
          class="tab"
          :class="{ active: route.path === '/contact' }"
        >
          PromptGpt
        </router-link>
        <router-link
          to="/promptlikegpt"
          class="tab"
          :class="{ active: route.path === '/promptlikegpt' }"
        >
          PromptLikeGpt
        </router-link>
      </nav>
    </header>
    <main class="content">
      <router-view />
    </main>
  </div>
</template>

<style scoped>

.header {
  padding: 0;
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
}

.tab:hover {
  background-color: #555;
}

.tab.active {
  background-color: #007bff;
  border-bottom-color: #007bff;
}

.content {
  flex: 1;
  overflow-y: auto;
}
</style>