import { ref } from 'vue'

const STORAGE_KEY = 'saved_prompts'

export function useSavedPrompts() {
  const prompts = ref([])

  // localStorage에서 프롬프트 로드
  const loadPrompts = () => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      prompts.value = stored ? JSON.parse(stored) : []
    } catch (error) {
      console.error('Error loading prompts:', error)
      prompts.value = []
    }
  }

  // localStorage에 프롬프트 저장
  const savePrompts = () => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(prompts.value))
    } catch (error) {
      console.error('Error saving prompts:', error)
    }
  }

  // 새 프롬프트 생성
  const createPrompt = (title, content) => {
    if (!title.trim() || !content.trim()) return null

    const promptId = `prompt-${Date.now()}`
    const newPrompt = {
      id: promptId,
      title: title.trim(),
      content: content.trim(),
      createdAt: new Date().toISOString()
    }
    prompts.value.push(newPrompt)
    savePrompts()
    return promptId
  }

  // 프롬프트 삭제
  const deletePrompt = (promptId) => {
    prompts.value = prompts.value.filter(p => p.id !== promptId)
    savePrompts()
    return true
  }

  // 프롬프트 수정
  const updatePrompt = (promptId, title, content) => {
    const prompt = prompts.value.find(p => p.id === promptId)
    if (!prompt) return false

    if (title.trim()) prompt.title = title.trim()
    if (content.trim()) prompt.content = content.trim()

    savePrompts()
    return true
  }

  // 프롬프트 조회
  const getPrompt = (promptId) => {
    return prompts.value.find(p => p.id === promptId)
  }

  // 초기화
  loadPrompts()

  return {
    prompts,
    loadPrompts,
    createPrompt,
    deletePrompt,
    updatePrompt,
    getPrompt
  }
}