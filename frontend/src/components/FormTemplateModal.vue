<script setup>
const props = defineProps({
  open: { type: Boolean, default: false },
  templates: { type: Array, default: () => [] },
  selectedTemplateId: { type: String, default: null },
  templateDraft: { type: Object, default: () => ({ name: '', description: '', fields: [] }) },
  templateMode: { type: String, default: 'view' }
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
  'addField',
  'updateField',
  'removeField',
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
            <p class="eyebrow template-title">폼 템플릿 관리</p>
            <h4>{{ templateMode === 'create' ? '새 템플릿 추가' : '템플릿 선택' }}</h4>
          </div>
          <div class="header-actions">
            <button class="ghost-btn" @click="emit('startCreate')">+ 템플릿 추가</button>
            <button class="ghost-btn" @click="emit('close')">닫기</button>
          </div>
        </div>
        <div class="template-layout">
          <div class="template-list">
            <div
              v-for="t in templates"
              :key="t.id"
              class="template-item"
              :class="{ active: selectedTemplateId === t.id }"
              @click="emit('select', t.id)"
            >
              <p class="title">{{ t.name }}</p>
              <p class="meta">필드 {{ t.fields?.length || 0 }}개</p>
            </div>
            <div v-if="templates.length === 0" class="empty">템플릿이 없습니다.</div>
          </div>
          <div class="template-detail">
            <div class="field">
              <label>이름</label>
              <input
                :value="templateDraft.name"
                :disabled="templateMode === 'view'"
                @input="onDraftChange({ name: $event.target.value })"
                placeholder="템플릿 이름"
              />
            </div>
            <div class="field">
              <label>설명</label>
              <textarea
                :value="templateDraft.description"
                :disabled="templateMode === 'view'"
                @input="onDraftChange({ description: $event.target.value })"
                rows="3"
                placeholder="설명을 입력하세요."
              ></textarea>
            </div>

            <div class="field">
                <div class="fields-header">
                  <label>필드 목록</label>
                  <button
                    v-if="templateMode !== 'view'"
                    class="ghost-btn xs"
                    @click="emit('addField')"
                  >
                    + 필드 추가
                  </button>
                </div>
              <div class="field-list" v-if="(templateDraft.fields || []).length">
                <div class="field-header">
                  <span>라벨</span>
                  <span>필드명</span>
                  <span>형식</span>
                  <span>필수</span>
                  <span></span>
                </div>
                <div v-for="f in templateDraft.fields" :key="f.id" class="field-row">
                  <input
                    :value="f.label"
                    :disabled="templateMode === 'view'"
                    @input="emit('updateField', f.id, { label: $event.target.value })"
                    placeholder="라벨"
                  />
                  <input
                    :value="f.name"
                    :disabled="templateMode === 'view'"
                    @input="emit('updateField', f.id, { name: $event.target.value })"
                    placeholder="필드 이름"
                  />
                  <select
                    :value="f.type"
                    :disabled="templateMode === 'view'"
                    @change="emit('updateField', f.id, { type: $event.target.value })"
                  >
                    <option value="text">텍스트</option>
                    <option value="textarea">멀티라인</option>
                    <option value="number">숫자</option>
                    <option value="select">선택</option>
                    <option value="checkbox">체크박스</option>
                    <option value="date">날짜</option>
                    <option value="time">시간</option>
                    <option value="datetime">날짜/시간</option>
                    <option value="image">이미지(업로드)</option>
                    <option value="audio">오디오(업로드)</option>
                  </select>
                  <label class="checkbox">
                    <input
                      type="checkbox"
                      :checked="f.required"
                      :disabled="templateMode === 'view'"
                      @change="emit('updateField', f.id, { required: $event.target.checked })"
                    />
                  </label>
                  <button
                    v-if="templateMode !== 'view'"
                    class="ghost-btn xs danger"
                    @click="emit('removeField', f.id)"
                  >
                    삭제
                  </button>
                  <div v-if="f.type === 'select'" class="options-row">
                    <div class="options-header">
                      <span class="branch">└</span>
                      <span class="label">
                        {{ f.label || f.name || '옵션' }}
                        <small>옵션 (줄바꿈 또는 쉼표로 구분)</small>
                      </span>
                    </div>
                    <textarea
                      :disabled="templateMode === 'view'"
                      :value="f.optionsInput ?? (f.options || []).join('\n')"
                      @input="emit('updateField', f.id, { optionsInput: $event.target.value, options: $event.target.value.split(/\n|,/).map((o) => o.trim()).filter(Boolean) })"
                      rows="3"
                      placeholder="예:\n1학년\n2학년\n3학년"
                    ></textarea>
                  </div>
                </div>
              </div>
              <div v-else class="empty">필드를 추가하세요.</div>
            </div>

            <div class="actions">
              <button
                class="ghost-btn"
                v-if="templateMode === 'view' && selectedTemplateId"
                @click="emit('startEdit')"
              >
                수정
              </button>
              <button class="ghost-btn" v-else @click="emit('cancel')">취소</button>
              <button
                class="ghost-btn danger"
                v-if="templateMode !== 'create' && selectedTemplateId"
                @click="emit('delete')"
              >
                삭제
              </button>
              <button
                v-if="templateMode !== 'view'"
                :class="['primary-btn', { 'save-btn': templateMode !== 'view' }]"
                @click="emit('save')"
              >
                저장
              </button>
              <button
                class="ghost-btn apply-btn"
                @click="emit('apply')"
                :disabled="!selectedTemplateId || templateMode !== 'view'"
                v-if="templateMode === 'view'"
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
  max-width: 860px;
  height: 80vh;
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
  grid-template-columns: 0.55fr 1.45fr;
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
.field textarea,
.field select {
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

.fields-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.field-row {
  display: grid;
  grid-template-columns: 1.2fr 1fr 0.8fr 0.6fr auto;
  gap: 6px;
  align-items: center;
  padding: 6px 0;
}

.field-row .checkbox {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: rgba(230, 236, 255, 0.8);
}

.options-row {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.02);
  margin-left: 8px;
}

.options-header {
  display: flex;
  align-items: center;
  gap: 8px;
  color: rgba(230, 236, 255, 0.8);
  font-size: 12px;
}

.options-header .branch {
  color: rgba(230, 236, 255, 0.4);
  font-weight: 700;
}

.options-header .label small {
  margin-left: 6px;
  color: rgba(230, 236, 255, 0.6);
  font-weight: 400;
}

.options-row label {
  font-size: 12px;
  color: rgba(230, 236, 255, 0.8);
}

.options-row input {
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

.options-row textarea {
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
  resize: vertical;
}

.field-list {
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-header {
  display: grid;
  grid-template-columns: 1.2fr 1fr 0.8fr 0.6fr auto;
  gap: 6px;
  padding: 4px 0 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.12);
  color: rgba(230, 236, 255, 0.7);
  font-size: 12px;
}

.options-row {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 6px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.03);
}

.options-row label {
  font-size: 12px;
  color: rgba(230, 236, 255, 0.8);
}

.options-row input {
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

.ghost-btn.xs {
  padding: 6px 8px;
  font-size: 11px;
}

.ghost-btn:hover {
  border-color: rgba(99, 179, 255, 0.7);
  box-shadow: 0 6px 18px rgba(99, 179, 255, 0.2);
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
  .field-row {
    grid-template-columns: 1fr;
  }
}
</style>
