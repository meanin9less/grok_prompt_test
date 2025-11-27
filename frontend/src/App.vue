<script setup>
import { computed, provide, ref } from 'vue'
import PromptManagerPanel from './components/PromptManagerPanel.vue'
import ModelControlPanel from './components/ModelControlPanel.vue'
import ResponseStreamPanel from './components/ResponseStreamPanel.vue'

const g_selectedSystemPrompt = ref(null)
const g_selectedInputPrompt = ref(null)
const g_selectedProvider = ref('grok')
const g_selectedModel = ref('grok-4-1-fast-reasoning')
const g_isStreaming = ref(false)
const g_generationOptions = ref({
  temperature: 0.7,
  maxTokens: 1024,
  topP: 0.95,
  systemOverride: ''
})

provide('g_isStreaming', g_isStreaming)

const responsePanelRef = ref(null)

const providerApiPath = computed(() => {
  if (g_selectedProvider.value === 'gpt' || g_selectedProvider.value === 'gpt-o1') return '/api/openai/prompt-chat'
  if (g_selectedProvider.value === 'gemini' || g_selectedProvider.value === 'gemini-flash') return '/api/gemini/prompt-chat'
  return '/api/grok/prompt-chat'
})

const readyForRun = computed(() => {
  // 입력 프롬프트만 필수 (좌측 패널)
  return Boolean(g_selectedInputPrompt.value)
})

const systemPromptLabel = computed(() => g_selectedSystemPrompt.value?.title || '')
const inputPromptLabel = computed(() => g_selectedInputPrompt.value?.title || '')

const handleExecute = () => {
  if (!readyForRun.value || !responsePanelRef.value) return

  // 시스템 프롬프트: 페르소나 설정이 있으면 사용, 아니면 좌측 패널의 시스템 프롬프트 사용
  const systemPrompt = g_generationOptions.value.systemOverride
    ? { id: 'persona', content: g_generationOptions.value.systemOverride }
    : g_selectedSystemPrompt.value

  responsePanelRef.value.runExecution(
    systemPrompt,
    g_selectedInputPrompt.value,
    g_generationOptions.value
  )
}

const handleStreamState = (isStreaming) => {
  g_isStreaming.value = isStreaming
}
</script>

<template>
  <div class="app-shell">
    <header class="studio-header">
      <div class="header-content">
        <p class="tagline">모델 출력 비교</p>
        <h1>모델 출력 비교</h1>
        <p class="subhead">프롬프트 선택 → 모델 실행 → 응답 비교까지 한눈에.</p>
      </div>
      <div class="status-chip" :class="{ live: g_isStreaming }">
        <span class="dot"></span>
        {{ g_isStreaming ? '생성 중' : '대기 중' }}
      </div>
    </header>

    <main class="studio-layout">
      <!-- 좌측: 프롬프트 선택/관리 -->
      <section class="panel left-panel" :class="{ locked: g_isStreaming }">
        <div class="panel-header">
          <div>
            <h2>1. 입력 값 설정</h2>
            <p class="eyebrow">모델에 전송 할 입력 값을 설정하세요</p>
          </div>
        </div>

        <PromptManagerPanel
          @update:system="(p) => (g_selectedSystemPrompt = p)"
          @update:input="(p) => (g_selectedInputPrompt = p)"
        />
      </section>

      <!-- 중앙: 모델 선택 + 옵션 + 실행 -->
      <section class="panel center-panel" :class="{ locked: g_isStreaming }">
        <ModelControlPanel
          :system-prompt-label="systemPromptLabel"
          :input-prompt-label="inputPromptLabel"
          :selected-provider="g_selectedProvider"
          :selected-model="g_selectedModel"
          :disabled="g_isStreaming"
          :ready-for-run="readyForRun"
          @update:provider="(p) => (g_selectedProvider = p)"
          @update:model="(m) => (g_selectedModel = m)"
          @update:options="(opts) => (g_generationOptions = opts)"
          @execute="handleExecute"
        />
      </section>

      <!-- 우측: 응답 스트리밍 + 비교 -->
      <section class="panel right-panel">
        <ResponseStreamPanel
          ref="responsePanelRef"
          :api-path="providerApiPath"
          :selected-model="g_selectedModel"
          :system-prompt="g_selectedSystemPrompt"
          :input-prompt="g_selectedInputPrompt"
          @stream-state-change="handleStreamState"
        />
      </section>
    </main>
  </div>
</template>

<style scoped>
.app-shell {
  display: flex;
  flex-direction: column;
  height: 100vh;
  min-height: 100vh;
  overflow: hidden;
  background: radial-gradient(circle at 20% 20%, #1e2638, #0a0f1d 60%);
  color: #e5e9f5;
  padding: 24px;
  box-sizing: border-box;
}

.studio-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 28px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.header-content {
  flex: 1;
}

.tagline {
  margin: 0 0 6px 0;
  color: #63ffdd;
  letter-spacing: 0.12em;
  font-size: 11px;
  text-transform: uppercase;
  font-weight: 600;
}

.studio-header h1 {
  margin: 0 0 8px 0;
  font-size: 32px;
  font-weight: 800;
  letter-spacing: -0.5px;
  background: linear-gradient(135deg, #ffffff 0%, #c7e5ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subhead {
  margin: 0;
  color: rgba(229, 233, 245, 0.7);
  font-size: 14px;
  letter-spacing: 0.02em;
}

.status-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  font-weight: 600;
  letter-spacing: 0.03em;
  font-size: 13px;
  white-space: nowrap;
}

.status-chip .dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #7dd3fc;
  box-shadow: 0 0 0 6px rgba(125, 211, 252, 0.2);
  animation: pulse-blue 2s ease-in-out infinite;
}

.status-chip.live .dot {
  background: #fbbf24;
  box-shadow: 0 0 0 6px rgba(251, 191, 36, 0.3);
  animation: pulse-gold 1.2s ease-in-out infinite;
}

@keyframes pulse-blue {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

@keyframes pulse-gold {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.studio-layout {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  grid-template-rows: 1fr;
  gap: 20px;
  flex: 1;
  height: 100%;
  min-height: 0;
  width: 100%;
  align-items: stretch;
  overflow: hidden;
}

.panel {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  backdrop-filter: blur(12px);
  position: relative;
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
  min-width: 0;
  box-sizing: border-box;
  overflow: hidden;
}

.panel.locked {
  opacity: 0.6;
  pointer-events: none;
}

.panel.locked::after {
  content: '생성 중에는 수정이 제한됩니다';
  position: absolute;
  inset: 0;
  background: rgba(8, 11, 20, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #e5e9f5;
  font-weight: 700;
  z-index: 10;
  border-radius: 16px;
}

.panel-header {
  padding: 18px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  background: rgba(255, 255, 255, 0.02);
}

.panel-header h2 {
  margin: 4px 0 0;
  font-size: 18px;
  font-weight: 700;
  letter-spacing: -0.2px;
}

.eyebrow {
  margin: 0 0 4px 0;
  color: #8fb5ff;
  letter-spacing: 0.1em;
  font-size: 14px;
  text-transform: uppercase;
  font-weight: 600;
}

.left-panel {
  grid-column: 1;
  padding: 0;
  align-self: stretch;
  min-width: 200px;
}

.arrow-container {
  grid-column: 2;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 0;
  height: 100%;
}

.next-step-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px 14px;
  background: linear-gradient(135deg, rgba(99, 255, 221, 0.15), rgba(99, 179, 255, 0.15));
  border: 1px solid rgba(99, 255, 221, 0.4);
  border-radius: 12px;
  width: auto;
  height: 48px;
  box-sizing: border-box;
}

.arrow-placeholder {
  width: 43.84px;
  height: 48px;
  box-sizing: border-box;
}

.center-panel {
  grid-column: 2;
  padding: 0;
  align-self: center;
  justify-self: center;
  width: fit-content;
  height: fit-content;
}

.right-panel {
  grid-column: 3;
  padding: 0;
  align-self: stretch;
  min-height: 0;
  min-width: 200px;
}

.left-panel :deep(.prompt-manager) {
  padding: 18px;
  height: 100%;
}

.indicator-text {
  margin: 0;
  font-size: 12px;
  font-weight: 600;
}

.arrow-icon {
  font-size: 16px;
  font-weight: 700;
  color: #63b3ff;
}

.arrow-pop-enter-active,
.arrow-pop-leave-active {
  transition: all 0.3s ease;
}

.arrow-pop-enter-from,
.arrow-pop-leave-to {
  opacity: 0;
  transform: translateY(8px);
}

@media (max-width: 1200px) {
  .studio-layout {
    grid-template-columns: 1fr 1fr;
  }

  .center-panel {
    grid-column: 1 / span 2;
    width: 100%;
  }

  .right-panel {
    grid-column: 1 / span 2;
  }

  .panel {
    min-height: auto;
  }
}

@media (max-width: 960px) {
  .studio-layout {
    grid-template-columns: 1fr;
  }

  .center-panel {
    grid-column: 1;
    width: 100%;
  }

  .right-panel {
    grid-column: 1;
  }

  .studio-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .studio-header h1 {
    font-size: 24px;
  }
}
</style>
