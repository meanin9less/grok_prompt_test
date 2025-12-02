<script setup>
import { computed, provide, ref, watch } from 'vue'
import PromptManagerPanel from './components/PromptManagerPanel.vue'
import ResponseStreamPanel from './components/ResponseStreamPanel.vue'
import MetaDrawer from './components/MetaDrawer.vue'

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
const g_metaOpen = ref(false)
const g_metaData = ref(null)

const modelFamilies = [
  {
    id: 'gpt',
    label: 'ChatGPT',
    subModels: ['gpt-5.1', 'gpt-5.1-codex', 'gpt-5-mini', 'gpt-5-nano', 'gpt-4.1', 'gpt-4.1-mini', 'gpt-4o', 'gpt-3.5-turbo']
  },
  {
    id: 'gemini',
    label: 'Gemini',
    subModels: ['gemini-3-pro-preview', 'gemini-2.5-pro', 'gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-1.5-pro']
  },
  {
    id: 'grok',
    label: 'Grok',
    subModels: ['grok-4-1-fast-reasoning', 'grok-4-1-fast-non-reasoning', 'grok-3']
  }
]

provide('g_isStreaming', g_isStreaming)

const responsePanelRef = ref(null)

const providerApiPath = computed(() => '/api/chat/prompt-chat')

const subModelOptions = computed(() => {
  const family = modelFamilies.find((item) => item.id === g_selectedProvider.value)
  return family?.subModels || []
})

watch(
  () => g_selectedProvider.value,
  () => {
    const available = subModelOptions.value
    if (!available.includes(g_selectedModel.value)) {
      g_selectedModel.value = available[0] || ''
    }
  },
  { immediate: true }
)

const readyForRun = computed(() => Boolean(g_selectedInputPrompt.value))

const handleExecute = () => {
  if (!readyForRun.value || !responsePanelRef.value) return

  const systemPrompt =
    g_selectedSystemPrompt.value ||
    (g_generationOptions.value.systemOverride && g_generationOptions.value.systemOverride.trim()
      ? { content: g_generationOptions.value.systemOverride }
      : null)

  responsePanelRef.value.runExecution(
    systemPrompt,
    g_selectedInputPrompt.value,
    g_generationOptions.value
  )
}

const handleStreamState = (isStreaming) => {
  g_isStreaming.value = isStreaming
}

const handleUpdateInput = (prompt) => {
  g_selectedInputPrompt.value = prompt
}

const handleMetaToggle = (payload) => {
  if (typeof payload === 'object' && payload !== null) {
    g_metaOpen.value = Boolean(payload.open)
    g_metaData.value = payload.run || g_metaData.value
  } else {
    g_metaOpen.value = Boolean(payload)
  }
}
</script>

<template>
  <div class="app-shell">
    <header class="studio-header">
      <div class="header-content">
        <h1>프롬프트 테스트</h1>
        <p class="subhead">입력정보와 프롬프트를 구성하고 실행해 결과를 확인하세요.</p>
      </div>
      <div class="status-chip" :class="{ live: g_isStreaming }">
        <span class="dot"></span>
        {{ g_isStreaming ? '생성 중' : '대기 중' }}
      </div>
    </header>

    <main class="studio-layout">
      <section class="panel left-panel" :class="{ locked: g_isStreaming, covered: g_metaOpen }">
        <div class="panel-header">
          <div class="panel-title">
            <h2>입력 정보 & 프롬프트 설정</h2>
          </div>
          <div class="model-selects">
            <span class="model-select-label">모델 선택</span>
            <select v-model="g_selectedProvider">
              <option v-for="family in modelFamilies" :key="family.id" :value="family.id">
                {{ family.label }}
              </option>
            </select>
            <select v-model="g_selectedModel">
              <option v-for="sub in subModelOptions" :key="sub" :value="sub">
                {{ sub }}
              </option>
            </select>
          </div>
        </div>

        <div class="left-body">
          <PromptManagerPanel @update:input="handleUpdateInput" @update:system="(p) => (g_selectedSystemPrompt = p)" />
        </div>
        <MetaDrawer
          v-if="g_metaOpen"
          :title="g_metaData?.title"
          :model="g_metaData?.modelVersion"
          :input-preview="g_metaData?.userPreview"
          :prompt-content="g_metaData?.promptContent"
          :input-type="g_metaData?.inputType"
          @close="handleMetaToggle({ open: false })"
        />
      </section>

      <section class="panel center-panel" :class="{ locked: g_isStreaming }">
        <button
          class="run-button center-only"
          :disabled="g_isStreaming || !readyForRun"
          @click="handleExecute"
        >
          <span>AI</span>
          <span>답변</span>
          <span>시작 ➜</span>
        </button>
      </section>

      <section class="panel right-panel">
        <ResponseStreamPanel
          ref="responsePanelRef"
          :api-path="providerApiPath"
          :model="g_selectedProvider"
          :model-version="g_selectedModel"
          :system-prompt="g_selectedSystemPrompt"
          :input-prompt="g_selectedInputPrompt"
          @stream-state-change="handleStreamState"
          @meta-toggle="handleMetaToggle"
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
  padding: 32px;
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
  grid-template-columns: 1fr 0.2fr 1fr;
  gap: 12px;
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

.center-panel {
  align-self: center;
  justify-self: center;
  width: 100%;
  max-width: 90px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  box-shadow: none;
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
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: nowrap;
}

.panel-title h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 800;
  letter-spacing: -0.2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

.panel-title {
  flex: 1 1 240px;
  min-width: 0;
}

.model-selects {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: nowrap;
  justify-content: flex-end;
  min-width: 0;
}

.model-select-label {
  font-size: 13px;
  color: rgba(230, 236, 255, 0.78);
  white-space: nowrap;
  font-weight: 600;
}

.model-selects select {
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  background: rgba(255, 255, 255, 0.05);
  color: #e6ecff;
  font-size: 13px;
  outline: none;
}

.model-selects select:focus {
  border-color: rgba(99, 179, 255, 0.8);
}

.eyebrow {
  margin: 0 0 4px 0;
  color: #8fb5ff;
  letter-spacing: 0.1em;
  font-size: 12px;
  text-transform: uppercase;
  font-weight: 700;
}

.left-panel {
  padding: 0;
  min-width: 280px;
  position: relative;
}

.left-panel.hidden {
  display: none;
}

.left-body {
  padding: 16px;
  height: 100%;
  flex: 1;
  min-height: 0;
  overflow: auto;
  padding-bottom: 22px;
  box-sizing: border-box;
}

.center-panel {
  align-self: center;
  justify-self: center;
  width: 100%;
  max-width: 90px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.run-button {
  padding: 10px 10px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  background: linear-gradient(160deg, #63b3ff 0%, #63ffdd 100%);
  color: #0b1221;
  font-weight: 800;
  font-size: 13px;
  letter-spacing: 0.04em;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  text-align: center;
  line-height: 1.15;
  min-height: 90px;
  box-shadow: 0 12px 30px rgba(99, 179, 255, 0.35);
}

.run-button span {
  display: block;
  padding: 1px 0;
}

.run-button span:last-child {
  font-size: 12px;
}

.run-button.center-only {
  max-width: 120px;
}

.run-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(99, 179, 255, 0.4);
}

.run-button:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.right-panel {
  padding: 0;
  min-height: 0;
  min-width: 280px;
}

.left-panel :deep(.prompt-manager) {
  padding: 14px;
  height: 100%;
}

.left-panel.covered {
  overflow: hidden;
}

.left-panel.covered .left-body,
.left-panel.covered .panel-header {
  opacity: 0.25;
  pointer-events: none;
  filter: blur(1px);
}

.left-panel.covered::after {
  content: '';
  position: absolute;
  inset: 0;
  background: rgba(5, 8, 18, 0.4);
  z-index: 1;
  pointer-events: none;
}

.studio-layout.drawer-open {
  grid-template-columns: 0px 0.2fr 1fr;
}

@media (max-width: 1200px) {
  .studio-layout {
    grid-template-columns: 1fr;
  }

  .center-panel,
  .right-panel,
  .left-panel {
    grid-column: 1;
  }

  .left-body {
    grid-template-columns: 1fr;
  }
}
</style>
