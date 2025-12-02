<script setup>
const props = defineProps({
  open: { type: Boolean, default: false },
  prompts: { type: Array, default: () => [] },
  selectedPromptId: { type: String, default: null },
  promptDraft: { type: Object, default: () => ({ title: '', text: '' }) },
  promptMode: { type: String, default: 'view' }
})

const emit = defineEmits([
  'close',
  'startCreate',
  'select',
  'startEdit',
  'cancel',
  'save',
  'delete',
  'apply',
  'changeDraft'
])

const onDraftChange = (partial) => emit('changeDraft', partial)
</script>

<template>
  <teleport to="body">
    <div class="prompt-modal" v-if="open">
      <div class="prompt-modal-content">
        <div class="modal-header">
          <div>
            <p class="eyebrow template-title">프롬프트 관리</p>
            <h4>{{ promptMode === 'create' ? '새 프롬프트 추가' : '프롬프트 선택' }}</h4>
          </div>
          <div class="header-actions">
            <button class="ghost-btn" @click="emit('startCreate')">+ 프롬프트 추가</button>
            <button class="ghost-btn" @click="emit('close')">닫기</button>
          </div>
        </div>
        <div class="template-layout">
          <div class="template-list">
            <div
              v-for="p in prompts"
              :key="p.id"
              class="template-item"
              :class="{ active: selectedPromptId === p.id }"
              @click="emit('select', p.id)"
            >
              <p class="title">{{ p.title }}</p>
              <p class="meta">본문 {{ p.text.length }}자</p>
            </div>
            <div v-if="prompts.length === 0" class="empty">프롬프트가 없습니다.</div>
          </div>
          <div class="template-detail">
            <div class="field">
              <label>제목</label>
              <input
                :value="promptDraft.title"
                :disabled="promptMode === 'view'"
                @input="onDraftChange({ title: $event.target.value })"
                placeholder="프롬프트 제목"
              />
            </div>
            <div class="field">
              <label>내용</label>
              <textarea
                :value="promptDraft.text"
                rows="8"
                :disabled="promptMode === 'view'"
                @input="onDraftChange({ text: $event.target.value })"
                placeholder="프롬프트 내용을 입력하세요."
              ></textarea>
            </div>
            <div class="actions">
              <button
                class="ghost-btn"
                v-if="promptMode === 'view' && selectedPromptId"
                @click="emit('startEdit')"
              >
                수정
              </button>
              <button class="ghost-btn" v-else @click="emit('cancel')">취소</button>
              <button
                class="ghost-btn danger"
                v-if="promptMode !== 'create' && selectedPromptId"
                @click="emit('delete')"
              >
                삭제
              </button>
              <button
                v-if="promptMode !== 'view'"
                :class="['primary-btn', { 'save-btn': promptMode !== 'view' }]"
                @click="emit('save')"
              >
                저장
              </button>
              <button
                class="ghost-btn apply-btn"
                @click="emit('apply')"
                :disabled="!selectedPromptId || promptMode !== 'view'"
                v-if="promptMode === 'view'"
              >
                적용
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </teleport>
</template>

<style scoped>
.prompt-modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 120;
  padding: 20px;
}

.prompt-modal-content {
  background: linear-gradient(135deg, rgba(12, 18, 32, 0.95), rgba(15, 23, 42, 0.95));
  border: 1px solid rgba(99, 179, 255, 0.2);
  border-radius: 16px;
  padding: 20px;
  width: 100%;
  max-width: 760px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  gap: 14px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  overflow: auto;
  box-sizing: border-box;
}

.template-layout {
  display: grid;
  grid-template-columns: 0.65fr 1.35fr;
  gap: 12px;
  min-height: 0;
  height: 100%;
  min-width: 0;
}

.template-list {
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow-y: auto;
  min-width: 0;
}

.template-item {
  padding: 10px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.04);
  cursor: pointer;
  color: #e6ecff;
}

.template-item.active {
  border-color: rgba(99, 179, 255, 0.9);
  background: rgba(99, 179, 255, 0.12);
}

.template-item .meta {
  margin: 4px 0 0;
  font-size: 11px;
  color: rgba(230, 236, 255, 0.8);
}

.template-detail {
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  overflow: auto;
  color: #e6ecff;
  min-height: 320px;
  max-height: 70vh;
  min-width: 0;
}

.template-detail .actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: nowrap;
}

.template-detail .actions .apply-btn {
  margin-left: auto;
}

.template-detail .actions .save-btn {
  margin-left: auto;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid rgba(99, 179, 255, 0.2);
  padding-bottom: 10px;
  margin-bottom: 6px;
}

.modal-header h4 {
  margin: 4px 0 0;
  color: #ffffff;
}

.template-title {
  color: #ffffff;
}

.field label {
  display: block;
  margin: 0 0 6px 0;
  font-size: 12px;
  color: rgba(230, 236, 255, 0.7);
  letter-spacing: 0.04em;
}

.field input,
.field textarea {
  width: 100%;
  min-width: 0;
  box-sizing: border-box;
  border-radius: 10px;
  border: 1px solid rgba(99, 179, 255, 0.2);
  background: rgba(255, 255, 255, 0.05);
  color: #e6ecff;
  padding: 10px;
  font-size: 13px;
  outline: none;
  font-family: inherit;
}

.actions .ghost-btn,
.actions .primary-btn {
  flex-shrink: 0;
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

.ghost-btn.danger {
  border-color: rgba(255, 99, 99, 0.5);
  color: #ffcaca;
}

.primary-btn {
  padding: 10px 16px;
  border: none;
  border-radius: 10px;
  background: linear-gradient(135deg, #63b3ff 0%, #63ffdd 100%);
  color: #0b1221;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  font-family: inherit;
}

.primary-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(99, 179, 255, 0.3);
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

@media (max-width: 900px) {
  .template-layout {
    grid-template-columns: 1fr;
  }
}
</style>
