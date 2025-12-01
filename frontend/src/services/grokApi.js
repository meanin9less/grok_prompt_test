const BACKEND_URL = 'http://localhost:8000'

export async function sendMessage(message, onChunk, apiPath = '/api/chat/prompt-chat', history = [], model = null, prompt = null, modelVersion = null, inputTitle = '') {
  const body = { message, history }
  if (model) {
    body.model = model
  }
  if (prompt) {
    body.prompt = prompt
  }
  if (modelVersion) {
    body.model_version = modelVersion
  }
  if (inputTitle) {
    body.input_title = inputTitle
  }
  console.log('Sending message with model:', model || 'auto', 'model_version:', modelVersion || 'default', 'prompt:', prompt ? prompt.slice(0, 60) + '...' : 'none', 'Body:', body)

  const response = await fetch(`${BACKEND_URL}${apiPath}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  })

  if (!response.ok) {
    throw new Error(`API Error: ${response.status} ${response.statusText}`)
  }

  let hasChunk = false

  // 스트리밍이 불가능한 경우 텍스트로 한번에 처리
  if (!response.body) {
    const text = await response.text()
    if (text) {
      hasChunk = true
      onChunk(text)
    }
    return
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let sseBuffer = ''

  const decodeChunk = (raw) => {
    // JSON 라인이면 content/message 필드 추출, 아니면 이스케이프된 개행 복원
    try {
      const parsed = JSON.parse(raw)
      const text = parsed.content || parsed.message || ''
      if (text) return text
    } catch (err) {
      // not json, fall through
    }
    return String(raw || '').replace(/\\n/g, '\n')
  }

  try {
    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const decoded = decoder.decode(value, { stream: true })
      if (!decoded) continue

      // SSE 형식이면 파싱, 아니면 그대로 전달
      if (decoded.includes('data:')) {
        sseBuffer += decoded
        const parts = sseBuffer.split('\n\n')
        sseBuffer = parts.pop() || ''

        for (const part of parts) {
          const lines = part.split('\n')
          for (const line of lines) {
            if (!line.startsWith('data:')) continue
            const data = line.slice(5).trim()
            if (!data || data === '[DONE]') continue
            hasChunk = true
            onChunk(decodeChunk(data))
          }
        }
      } else {
        hasChunk = true
        onChunk(decodeChunk(decoded.trim()))
      }
    }

    // 남은 SSE 버퍼 처리
    if (sseBuffer.trim()) {
      const lines = sseBuffer.split('\n')
      for (const line of lines) {
        if (!line.startsWith('data:')) continue
        const data = line.slice(5).trim()
        if (!data || data === '[DONE]') continue
        hasChunk = true
        onChunk(decodeChunk(data))
      }
    }
  } finally {
    reader.releaseLock()
  }

  // 스트림 파싱에서 아무것도 읽지 못했을 때를 대비한 최종 안전망
  if (!hasChunk) {
    try {
      const fallbackText = await response.clone().text()
      if (fallbackText) onChunk(fallbackText)
    } catch (err) {
      console.warn('Fallback read failed', err)
    }
  }
}

export async function healthCheck() {
  try {
    const response = await fetch(`${BACKEND_URL}/api/grok/health`)
    return response.ok
  } catch (error) {
    console.error('Health check failed:', error)
    return false
  }
}
