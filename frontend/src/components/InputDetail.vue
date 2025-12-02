<script setup>
import { computed } from 'vue'
import InputDetailText from './InputDetailText.vue'
import InputDetailForm from './InputDetailForm.vue'

const props = defineProps({
  mode: { type: String, default: 'idle' },
  draft: { type: Object, default: () => ({}) },
  selectedInput: { type: Object, default: null },
  prompts: { type: Array, default: () => [] },
  templates: { type: Array, default: () => [] },
  modelFamilies: { type: Array, default: () => [] },
  currentModelVersions: { type: Array, default: () => [] },
  viewModelVersions: { type: Array, default: () => [] },
  detailTitle: { type: String, default: '' },
  detailEyebrow: { type: String, default: '' }
})

const emit = defineEmits([
  'changeDraft',
  'save',
  'cancel',
  'startEdit',
  'delete',
  'openPromptModal',
  'openTemplateModal',
  'updateSelectedModel',
  'updateSelectedVersion',
  'updateSelectedPrompt',
  'updateTemplate',
  'updateFormData',
  'updateTemplateView'
])

const onDraftChange = (partial) => emit('changeDraft', partial)

const promptPreview = (id) => props.prompts.find((p) => p.id === id)?.text || ''

const selectedTemplate = computed(() => props.templates.find((t) => t.id === (props.selectedInput?.templateId || props.draft?.templateId)) || null)

const displayValue = (val) => {
  if (val && typeof val === 'object') {
    if (val.filename) return val.filename
    return JSON.stringify(val)
  }
  return val
}
</script>

<template>
  <div class="detail-pane">
    <div class="detail-header">
      <div>
        <p class="eyebrow" v-if="detailEyebrow">{{ detailEyebrow }}</p>
        <h3>{{ detailTitle }}</h3>
      </div>
    </div>

    <div class="detail-body">
      <template v-if="mode === 'create' || mode === 'edit'">
        <div class="grid-two">
          <div class="field">
            <label>모델</label>
            <select :value="draft.model" @change="onDraftChange({ model: $event.target.value })">
              <option v-for="family in modelFamilies" :key="family.id" :value="family.id">
                {{ family.label }}
              </option>
            </select>
          </div>
          <div class="field">
            <label>버전</label>
            <select :value="draft.version" @change="onDraftChange({ version: $event.target.value })">
              <option v-for="sub in currentModelVersions" :key="sub" :value="sub">
                {{ sub }}
              </option>
            </select>
          </div>
        </div>

        <div class="field">
          <label>프롬프트</label>
          <div class="select-row">
            <select :value="draft.promptId || ''" @change="onDraftChange({ promptId: $event.target.value })">
              <option value="">프롬프트 선택 안 함</option>
              <option v-for="p in prompts" :key="p.id" :value="p.id">
                {{ p.title }}
              </option>
            </select>
            <button class="ghost-btn xs" @click="emit('openPromptModal')">관리</button>
          </div>
          <p class="helper" v-if="draft.promptId">
            미리보기: {{ promptPreview(draft.promptId).slice(0, 120) }}
          </p>
        </div>

        <div class="grid-two">
          <div class="field">
            <label>입력정보 이름</label>
            <input :value="draft.title" @input="onDraftChange({ title: $event.target.value })" placeholder="입력정보 이름을 입력하세요." />
          </div>
          <div class="field">
            <label>입력 형태</label>
            <div class="segmented">
              <button :class="{ active: draft.inputType === 'text' }" @click="onDraftChange({ inputType: 'text' })">텍스트</button>
              <button :class="{ active: draft.inputType === 'form' }" @click="onDraftChange({ inputType: 'form' })">폼</button>
            </div>
          </div>
        </div>

        <div class="field" v-if="draft.inputType === 'form'">
          <label>폼 템플릿</label>
          <div class="select-row">
            <select :value="draft.templateId || ''" @change="onDraftChange({ templateId: $event.target.value || null })">
              <option value="">템플릿 선택</option>
              <option v-for="t in templates" :key="t.id" :value="t.id">{{ t.name }}</option>
            </select>
            <button class="ghost-btn xs" @click="emit('openTemplateModal')">관리</button>
          </div>
          <p class="helper" v-if="draft.templateId">{{ templates.find((t) => t.id === draft.templateId)?.description }}</p>
        </div>

        <div class="field">
          <label>입력 값</label>
          <InputDetailText
            v-if="draft.inputType === 'text'"
            :text="draft.text"
            @update:text="(val) => onDraftChange({ text: val })"
          />
          <InputDetailForm
            v-else
            :draft="draft"
            :templates="templates"
            :hide-template-selector="true"
            @change-draft="onDraftChange"
            @open-template-modal="emit('openTemplateModal')"
            @update-template="emit('updateTemplate', $event)"
          />
        </div>

        <div class="actions">
          <button class="ghost-btn" @click="emit('cancel')">취소</button>
          <button class="primary-btn" @click="emit('save')">저장</button>
        </div>
      </template>

      <template v-else-if="selectedInput">
        <div class="info-grid">
          <div class="field">
            <label>모델 / 버전</label>
            <div class="inline-pair">
              <select :value="selectedInput.model" @change="emit('updateSelectedModel', $event.target.value)">
                <option v-for="family in modelFamilies" :key="family.id" :value="family.id">
                  {{ family.label }}
                </option>
              </select>
              <select :value="selectedInput.version" @change="emit('updateSelectedVersion', $event.target.value)">
                <option v-for="sub in viewModelVersions" :key="sub" :value="sub">
                  {{ sub }}
                </option>
              </select>
            </div>
          </div>
          <div class="field">
            <label>프롬프트</label>
            <div class="select-row">
              <select :value="selectedInput.promptId || ''" @change="emit('updateSelectedPrompt', $event.target.value)">
                <option value="">프롬프트 선택 안 함</option>
                <option v-for="p in prompts" :key="p.id" :value="p.id">
                  {{ p.title }}
                </option>
              </select>
              <button class="ghost-btn xs" @click="emit('openPromptModal')">관리</button>
            </div>
          </div>
          <div class="field">
            <label>입력정보 이름</label>
            <div class="detail-card">{{ selectedInput.title }}</div>
          </div>
        </div>

        <div class="field" v-if="(selectedInput.inputType || 'text') === 'form'">
          <label>폼 템플릿</label>
          <div class="inline-pair">
            <select :value="selectedInput.templateId || ''" @change="emit('updateTemplateView', $event.target.value)">
              <option value="">템플릿 선택 안 함</option>
              <option v-for="t in templates" :key="t.id" :value="t.id">
                {{ t.name }}
              </option>
            </select>
            <button class="ghost-btn xs" @click="emit('openTemplateModal')">템플릿 관리</button>
          </div>
        </div>

        <div class="field">
          <label>입력 값</label>
          <template v-if="(selectedInput.inputType || 'text') === 'form'">
            <InputDetailForm
              :draft="selectedInput"
              :templates="templates"
              @change-draft="emit('updateFormData', $event)"
              @open-template-modal="emit('openTemplateModal')"
              @update-template="emit('updateTemplateView', $event)"
            />
          </template>
          <div class="detail-card" v-else>
            <pre>{{ selectedInput.text }}</pre>
          </div>
        </div>

        <div class="actions right" v-if="selectedInput">
          <button class="ghost-btn xs" @click="emit('startEdit')">수정</button>
          <button class="ghost-btn xs danger" @click="emit('delete')">삭제</button>
        </div>

      </template>

      <div v-else class="empty-detail">
        좌측에서 입력정보를 선택하거나 추가하세요.
      </div>
    </div>
  </div>
</template>

<style scoped>
.detail-pane {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 12px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  min-width: 0;
  min-height: 0;
  overflow: hidden;
}

.detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  flex-wrap: nowrap;
}

.detail-header > div:first-child {
  flex: 1 1 0;
  min-width: 0;
}

.detail-header h3 {
  margin: 2px 0 0;
  flex: 1 1 200px;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: nowrap;
  justify-content: flex-end;
  flex-shrink: 0;
  white-space: nowrap;
}

.detail-body {
  flex: 1;
  overflow: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 12px;
  min-height: 0;
  padding-bottom: 14px;
}

.grid-two {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 10px;
}

.inline-pair {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.inline-pair select {
  width: 100%;
}

.segmented {
  display: inline-flex;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 10px;
  overflow: hidden;
}

.segmented button {
  border: none;
  background: transparent;
  color: #e6ecff;
  padding: 8px 10px;
  cursor: pointer;
  font-size: 12px;
}

.segmented button.active {
  background: rgba(99, 179, 255, 0.16);
  color: #cfe7ff;
}

.select-row {
  display: flex;
  gap: 8px;
  align-items: center;
}

.select-row select {
  flex: 1;
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

.field textarea {
  resize: vertical;
  min-height: 120px;
}

.detail-card {
  padding: 12px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.04);
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 13px;
}

.detail-card pre {
  margin: 0;
  white-space: pre-wrap;
  font-family: inherit;
}

.form-preview {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.preview-row {
  display: grid;
  grid-template-columns: 0.4fr 1.6fr;
  gap: 8px;
  padding: 6px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.preview-row:last-child {
  border-bottom: none;
}

.preview-label {
  color: rgba(230, 236, 255, 0.8);
  font-weight: 600;
  font-size: 12px;
}

.preview-value {
  color: #e6ecff;
  font-size: 13px;
  word-break: break-word;
  white-space: pre-wrap;
}

.actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  align-items: center;
}

.actions.right {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
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

.helper {
  margin: 6px 0 0;
  color: rgba(230, 236, 255, 0.7);
  font-size: 12px;
}

.empty-detail {
  padding: 14px;
  border: 1px dashed rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  color: rgba(230, 236, 255, 0.7);
  text-align: center;
}

.read-only-form .readonly-box {
  padding: 10px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.04);
  color: #e6ecff;
  font-size: 13px;
}

.template-name {
  margin: 0 0 8px 0;
  font-size: 12px;
  color: rgba(230, 236, 255, 0.8);
}

.eyebrow {
  margin: 0;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  font-size: 11px;
  color: #8fb5ff;
  font-weight: 600;
}

@media (max-width: 1100px) {
  .grid-two {
    grid-template-columns: 1fr;
  }
}
</style>
