<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  items: { type: Array, default: () => [] },
  prompts: { type: Array, default: () => [] },
  selectedId: { type: String, default: null }
})

const emit = defineEmits(['select', 'create'])

const filterType = ref('all') // all | text | form

const filteredItems = computed(() => {
  if (filterType.value === 'all') return props.items
  return props.items.filter((item) => (item.inputType || 'text') === filterType.value)
})

const promptTitle = (promptId) => {
  const found = props.prompts.find((p) => p.id === promptId)
  return found?.title || '미선택'
}
</script>

<template>
  <div class="list-pane">
    <div class="list-pane-header">
      <div>
        <p class="eyebrow">입력정보</p>
        <h3>저장된 입력</h3>
      </div>
      <div class="list-actions">
        <button class="ghost-btn xs" @click="emit('create')">+ 새 입력</button>
      </div>
    </div>

    <div class="filters">
      <button :class="['filter-btn', { active: filterType === 'all' }]" @click="filterType = 'all'">전체</button>
      <button :class="['filter-btn', { active: filterType === 'text' }]" @click="filterType = 'text'">텍스트</button>
      <button :class="['filter-btn', { active: filterType === 'form' }]" @click="filterType = 'form'">폼</button>
    </div>

    <div class="list">
        <div
          v-for="input in filteredItems"
          :key="input.id"
          class="list-item"
          :class="{ active: selectedId === input.id }"
          @click="emit('select', input.id)"
        >
          <div class="list-top">
            <p class="title">{{ input.title }}</p>
            <div class="pills">
              <span class="pill mini">{{ input.model }}</span>
              <span class="pill mini type" :class="input.inputType === 'form' ? 'form' : 'text'">
                {{ input.inputType === 'form' ? '폼' : '텍스트' }}
              </span>
            </div>
          </div>
          <p class="meta">{{ input.version }}</p>
          <p class="meta light">프롬프트: {{ promptTitle(input.promptId) }}</p>
        </div>
      <div v-if="filteredItems.length === 0" class="empty">리스트가 없습니다.</div>
    </div>
  </div>
</template>

<style scoped>
.list-pane {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 12px;
  padding: 10px;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.list-pane-header {
  padding: 4px 2px 8px;
  min-width: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.list-pane-header h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: -0.15px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.list-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.filters {
  display: flex;
  gap: 6px;
  margin: 6px 0 10px;
}

.filter-btn {
  padding: 6px 10px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  background: rgba(255, 255, 255, 0.06);
  color: #e6ecff;
  cursor: pointer;
  font-size: 11px;
}

.filter-btn.active {
  border-color: rgba(99, 179, 255, 0.7);
  background: rgba(99, 179, 255, 0.14);
}

.list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
  overflow-y: auto;
  box-sizing: border-box;
}

.list-item {
  padding: 10px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.04);
  cursor: pointer;
  transition: border-color 0.2s ease, transform 0.2s ease;
}

.list-item:hover {
  border-color: rgba(99, 179, 255, 0.6);
}

.list-item.active {
  border-color: rgba(99, 179, 255, 0.9);
  background: rgba(99, 179, 255, 0.12);
}

.title {
  margin: 0;
  font-weight: 700;
  font-size: 13px;
  text-overflow: ellipsis;
  white-space: nowrap;
  overflow: hidden;
}

.list-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 6px;
}

.pills {
  display: flex;
  gap: 4px;
  align-items: center;
}

.meta {
  margin: 4px 0 0;
  font-size: 12px;
  color: rgba(230, 236, 255, 0.8);
}

.meta.light {
  color: rgba(230, 236, 255, 0.65);
}

.pill {
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  background: rgba(255, 255, 255, 0.08);
  color: #e6ecff;
  font-size: 12px;
  letter-spacing: 0.02em;
  flex-shrink: 0;
}

.pill.mini {
  padding: 4px 8px;
  font-size: 11px;
}

.pill.mini.type {
  border-color: rgba(255, 255, 255, 0.2);
}

.pill.mini.type.form {
  background: rgba(99, 255, 211, 0.16);
  border-color: rgba(99, 255, 211, 0.4);
}

.pill.mini.type.text {
  background: rgba(99, 179, 255, 0.16);
  border-color: rgba(99, 179, 255, 0.4);
}

.ghost-btn {
  padding: 8px 10px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  background: rgba(255, 255, 255, 0.06);
  color: #e6ecff;
  cursor: pointer;
  font-size: 12px;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.ghost-btn.xs {
  padding: 6px 8px;
  font-size: 11px;
}

.ghost-btn:hover {
  border-color: rgba(99, 179, 255, 0.7);
  box-shadow: 0 6px 18px rgba(99, 179, 255, 0.2);
}

.empty {
  text-align: center;
  color: rgba(230, 236, 255, 0.6);
  padding: 12px;
  font-size: 12px;
}

.eyebrow {
  margin: 0;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  font-size: 11px;
  color: #8fb5ff;
  font-weight: 600;
}
</style>
