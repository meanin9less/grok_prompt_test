import { ref } from 'vue'

export function useChatHistory(apiPath) {
  const getStorageKey = () => `chat_history_${apiPath}`

  const loadHistory = (messages) => {
    const key = getStorageKey()
    const saved = localStorage.getItem(key)
    if (saved) {
      try {
        const parsed = JSON.parse(saved)
        // timestamp를 Date 객체로 변환
        messages.value = parsed.map(msg => ({
          ...msg,
          timestamp: new Date(msg.timestamp)
        }))
      } catch (e) {
        console.error('Failed to load chat history:', e)
      }
    }
  }

  const saveHistory = (messages) => {
    const key = getStorageKey()
    localStorage.setItem(key, JSON.stringify(messages.value))
  }

  const clearHistory = (messages) => {
    messages.value = []
    const key = getStorageKey()
    localStorage.removeItem(key)
  }

  return {
    getStorageKey,
    loadHistory,
    saveHistory,
    clearHistory
  }
}
