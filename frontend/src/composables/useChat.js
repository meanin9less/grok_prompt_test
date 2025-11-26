import { ref, nextTick } from 'vue'
import { sendMessage } from '../services/grokApi'

export function useChat(apiPath, saveHistoryCallback, scrollToBottomCallback) {
  const messages = ref([])
  const inputMessage = ref('')
  const isLoading = ref(false)
  const messagesContainer = ref(null)
  const textareaRef = ref(null)
  const isComposing = ref(false)

  const handleCompositionStart = () => {
    isComposing.value = true
  }

  const handleCompositionEnd = () => {
    isComposing.value = false
  }

  const handleSendMessage = async () => {
    const message = inputMessage.value.trim()
    if (!message) return

    const userMessage = {
      id: Date.now(),
      text: message,
      sender: 'user',
      timestamp: new Date()
    }
    messages.value.push(userMessage)
    inputMessage.value = ''
    isLoading.value = true
    await scrollToBottomCallback()
    saveHistoryCallback()

    try {
      const assistantMessageId = Date.now() + 1
      const assistantMessage = {
        id: assistantMessageId,
        text: '',
        sender: 'assistant',
        timestamp: new Date()
      }
      messages.value.push(assistantMessage)
      await scrollToBottomCallback()

      // 히스토리 구성: user와 assistant 메시지만 필터링
      const history = messages.value
        .filter(msg => msg.id !== assistantMessageId) // 방금 추가한 assistant 메시지 제외
        .filter(msg => msg.id !== userMessage.id) // 방금 추가한 user 메시지 제외
        .map(msg => ({
          role: msg.sender === 'user' ? 'user' : 'assistant',
          content: msg.text
        }))

      await sendMessage(message, (chunk) => {
        const assistantMsg = messages.value.find(msg => msg.id === assistantMessageId)
        if (assistantMsg) {
          assistantMsg.text += chunk
        }
      }, apiPath, history)

      saveHistoryCallback()
      await scrollToBottomCallback()
    } catch (error) {
      console.error('Error sending message:', error)
      messages.value.push({
        id: Date.now() + 2,
        text: `Error: ${error.message || 'Failed to get response from server'}`,
        sender: 'assistant',
        timestamp: new Date()
      })
      saveHistoryCallback()
    } finally {
      isLoading.value = false
      await scrollToBottomCallback()
    }
  }

  const handleKeyDown = async (e) => {
    if (e.key === 'Enter' && !e.shiftKey && !isLoading.value) {
      e.preventDefault()

      if (isComposing.value) {
        // 조합을 강제로 종료시키기 위한 트릭
        textareaRef.value.blur()
        await nextTick()
        textareaRef.value.focus()
      }

      handleSendMessage()
    }
  }

  return {
    messages,
    inputMessage,
    isLoading,
    messagesContainer,
    textareaRef,
    isComposing,
    handleCompositionStart,
    handleCompositionEnd,
    handleSendMessage,
    handleKeyDown
  }
}
