const BACKEND_URL = 'http://localhost:8000'

export async function sendMessage(message, onChunk, apiPath = '/api/grok/chat', history = [], model = null, promptKey = 'prompt') {
  const body = { message, history }
  if (model) {
    body.model = model
  }
  if (promptKey) {
    body.prompt_key = promptKey
  }
  console.log('Sending message with model:', model || 'default', 'prompt_key:', promptKey, 'Body:', body)

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

  const reader = response.body.getReader()
  const decoder = new TextDecoder()

  try {
    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value, { stream: true })
      if (chunk) {
        onChunk(chunk)
      }
    }
  } finally {
    reader.releaseLock()
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
