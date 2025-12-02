<script setup>
import { onMounted, ref, watch, nextTick } from 'vue'

const props = defineProps({
  text: { type: String, default: '' }
})
const emit = defineEmits(['update:text'])

const textareaRef = ref(null)

const autoResize = () => {
  const el = textareaRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = `${el.scrollHeight}px`
}

onMounted(() => {
  autoResize()
})

watch(
  () => props.text,
  () => nextTick(autoResize)
)
</script>

<template>
  <textarea
    ref="textareaRef"
    :value="props.text"
    @input="emit('update:text', $event.target.value)"
    placeholder="보낼 텍스트를 작성하세요."
  ></textarea>
</template>

<style scoped>
textarea {
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
  resize: none;
  min-height: 220px;
  overflow: hidden;
}
</style>
