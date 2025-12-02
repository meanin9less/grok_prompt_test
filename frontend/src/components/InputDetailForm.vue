<script setup>
import { watch, computed } from 'vue'

const props = defineProps({
  draft: { type: Object, default: () => ({}) },
  templates: { type: Array, default: () => [] },
  hideTemplateSelector: { type: Boolean, default: false }
})

const emit = defineEmits(['changeDraft', 'openTemplateModal', 'updateTemplate'])

const selectedTemplate = computed(() => props.templates.find((t) => t.id === props.draft.templateId) || null)

watch(
  () => props.draft.templateId,
  (id) => {
    emit('updateTemplate', id)
  }
)

const handleFieldChange = (name, value) => {
  emit('changeDraft', { formData: { ...props.draft.formData, [name]: value } })
}

const handleFileChange = (name, file) => {
  if (!file) {
    handleFieldChange(name, null)
    return
  }
  const reader = new FileReader()
  reader.onload = () => {
    handleFieldChange(name, {
      filename: file.name,
      type: file.type,
      dataUrl: reader.result
    })
  }
  reader.readAsDataURL(file)
}
</script>

<template>
  <div class="form-pane">
    <div class="field" v-if="!hideTemplateSelector">
      <label>폼 템플릿</label>
      <div class="select-row">
        <select :value="draft.templateId || ''" @change="emit('changeDraft', { templateId: $event.target.value || null })">
          <option value="">템플릿 선택</option>
          <option v-for="t in templates" :key="t.id" :value="t.id">{{ t.name }}</option>
        </select>
        <button class="ghost-btn xs" @click="emit('openTemplateModal')">관리</button>
      </div>
      <p class="helper" v-if="selectedTemplate?.description">{{ selectedTemplate.description }}</p>
    </div>

    <div v-if="selectedTemplate" class="fields">
      <div v-for="field in selectedTemplate.fields" :key="field.id" class="field-row">
        <label>
          {{ field.label || field.name }}
          <span v-if="field.required" class="required">*</span>
        </label>
        <template v-if="field.type === 'select'">
          <select
            :value="draft.formData?.[field.name] || ''"
            @change="handleFieldChange(field.name, $event.target.value)"
          >
            <option value="">선택하세요</option>
            <option
              v-for="opt in field.options || []"
              :key="opt.value || opt.label"
              :value="opt.value || opt.label"
            >
              {{ opt.label || opt.value }}
            </option>
          </select>
          <p class="helper" v-if="!field.options || field.options.length === 0">옵션을 설정하세요.</p>
        </template>
        <template v-else-if="field.type === 'image'">
          <input
            type="file"
            accept="image/*"
            :required="field.required"
            @change="handleFileChange(field.name, $event.target.files?.[0] || null)"
          />
          <p class="helper" v-if="draft.formData?.[field.name]?.filename">선택됨: {{ draft.formData?.[field.name]?.filename }}</p>
        </template>
        <template v-else-if="field.type === 'audio'">
          <input
            type="file"
            accept="audio/*"
            :required="field.required"
            @change="handleFileChange(field.name, $event.target.files?.[0] || null)"
          />
          <p class="helper" v-if="draft.formData?.[field.name]?.filename">선택됨: {{ draft.formData?.[field.name]?.filename }}</p>
        </template>
        <template v-else-if="field.type === 'textarea'">
          <textarea
            :value="draft.formData?.[field.name] || ''"
            @input="handleFieldChange(field.name, $event.target.value)"
            :required="field.required"
            rows="4"
          ></textarea>
        </template>
        <template v-else-if="field.type === 'checkbox'">
          <label class="checkbox-inline">
            <input
              type="checkbox"
              :checked="Boolean(draft.formData?.[field.name])"
              @change="handleFieldChange(field.name, $event.target.checked)"
            />
            체크
          </label>
        </template>
        <template v-else-if="field.type === 'date'">
          <input
            type="date"
            :value="draft.formData?.[field.name] || ''"
            @input="handleFieldChange(field.name, $event.target.value)"
            :required="field.required"
          />
        </template>
        <template v-else-if="field.type === 'time'">
          <input
            type="time"
            :value="draft.formData?.[field.name] || ''"
            @input="handleFieldChange(field.name, $event.target.value)"
            :required="field.required"
          />
        </template>
        <template v-else-if="field.type === 'datetime'">
          <input
            type="datetime-local"
            :value="draft.formData?.[field.name] || ''"
            @input="handleFieldChange(field.name, $event.target.value)"
            :required="field.required"
          />
        </template>
        <template v-else-if="field.type === 'image'">
          <input
            type="url"
            :value="draft.formData?.[field.name] || ''"
            @input="handleFieldChange(field.name, $event.target.value)"
            :required="field.required"
            placeholder="이미지 URL을 입력하세요."
          />
        </template>
        <template v-else-if="field.type === 'audio'">
          <input
            type="url"
            :value="draft.formData?.[field.name] || ''"
            @input="handleFieldChange(field.name, $event.target.value)"
            :required="field.required"
            placeholder="오디오 URL을 입력하세요."
          />
        </template>
        <template v-else>
          <input
            :type="field.type === 'number' ? 'number' : 'text'"
            :value="draft.formData?.[field.name] || ''"
            @input="handleFieldChange(field.name, $event.target.value)"
            :required="field.required"
          />
        </template>
      </div>
    </div>

    <div v-else class="empty-form">폼 템플릿을 선택하세요.</div>
  </div>
</template>

<style scoped>
.form-pane {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field label {
  font-size: 12px;
  color: rgba(230, 236, 255, 0.7);
  letter-spacing: 0.04em;
}

.select-row {
  display: flex;
  gap: 8px;
  align-items: center;
}

.select-row select {
  flex: 1;
}

.field-row {
  display: grid;
  grid-template-columns: 1.2fr 1fr 0.8fr 0.6fr auto;
  gap: 10px;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.field-row label {
  display: block;
  margin: 0 0 6px 0;
  font-size: 12px;
  color: rgba(230, 236, 255, 0.7);
  letter-spacing: 0.04em;
}

.field-row input,
.field-row select,
.field-row textarea {
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

.field-row textarea {
  resize: vertical;
  min-height: 100px;
}

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

.required {
  color: #ffb3b3;
  margin-left: 4px;
}

.checkbox-inline {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: rgba(230, 236, 255, 0.8);
  font-size: 13px;
}

.empty-form {
  padding: 10px;
  border-radius: 10px;
  border: 1px dashed rgba(255, 255, 255, 0.2);
  color: rgba(230, 236, 255, 0.7);
}

.helper {
  margin: 0;
  color: rgba(230, 236, 255, 0.7);
  font-size: 12px;
}

.ghost-btn.xs {
  padding: 6px 8px;
  font-size: 11px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  background: rgba(255, 255, 255, 0.06);
  color: #e6ecff;
  cursor: pointer;
}

.ghost-btn.xs:hover {
  border-color: rgba(99, 179, 255, 0.7);
}

select, input {
  background: rgba(255, 255, 255, 0.05);
}
</style>
