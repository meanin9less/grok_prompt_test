<script setup>
const props = defineProps({
  title: String,
  model: String,
  inputPreview: String,
  promptContent: String,
  inputType: String
})

const emit = defineEmits(['close'])
</script>

<template>
  <div class="meta-drawer">
    <div class="drawer-header">
      <div>
        <p class="eyebrow">입력/프롬프트</p>
        <h4>{{ props.title || '선택된 실행 없음' }}</h4>
        <p class="status">{{ props.inputType === 'form' ? '폼 입력' : '텍스트 입력' }}</p>
      </div>
      <button class="ghost-btn xs" @click="emit('close')">닫기</button>
    </div>
    <div class="drawer-body two-col">
      <section class="drawer-section">
        <p class="eyebrow">사용된 입력</p>
        <div class="drawer-box">
          <div class="drawer-text">{{ props.inputPreview || '입력정보 없음' }}</div>
        </div>
      </section>
      <section class="drawer-section">
        <p class="eyebrow">프롬프트 내용</p>
        <div class="drawer-box">
          <div class="drawer-text long">{{ props.promptContent || '프롬프트가 비어 있습니다.' }}</div>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.meta-drawer {
  position: absolute;
  inset: 0;
  background: rgba(10, 12, 20, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 14px;
  padding: 16px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 12px;
  z-index: 5;
  animation: slideIn 0.2s ease;
}

.drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.drawer-body {
  flex: 1;
  overflow: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.drawer-body.two-col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  min-height: 0;
  align-items: stretch;
}

.drawer-section {
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.02);
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 0;
  flex: 1;
}

.drawer-text {
  margin: 4px 0 0;
  color: rgba(230, 236, 255, 0.86);
  white-space: pre-wrap;
  word-break: break-word;
  flex: 1;
  overflow: auto;
  max-height: none;
}

.drawer-box {
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.03);
  padding: 8px;
  min-height: 200px;
  flex: 1;
  min-height: 0;
  max-height: none;
  overflow: auto;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}

.eyebrow {
  margin: 0;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  font-size: 11px;
  color: #8fb5ff;
  font-weight: 600;
}

.status {
  margin: 4px 0 0;
  color: rgba(230, 236, 255, 0.7);
  font-size: 12px;
}

.ghost-btn.xs {
  padding: 6px 8px;
  font-size: 11px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  background: rgba(255, 255, 255, 0.06);
  color: #e6ecff;
  cursor: pointer;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-8px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@media (max-width: 960px) {
  .drawer-body.two-col {
    grid-template-columns: 1fr;
  }
  .drawer-box {
    min-height: 160px;
  }
}
</style>
