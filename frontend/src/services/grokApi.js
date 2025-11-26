const BACKEND_URL = 'http://localhost:8000'

export async function sendMessage(message, onChunk, apiPath = '/api/grok/chat', history = [], model = null) {
  const body = { message, history }
  if (model) {
    body.model = model
  }
  console.log('Sending message with model:', model || 'default', 'Body:', body)

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

export async function getPromptsList() {
  try {
    const response = await fetch(`${BACKEND_URL}/api/prompts/list`)
    if (!response.ok) throw new Error('Failed to fetch prompts list')
    return await response.json()
  } catch (error) {
    console.error('Error fetching prompts list:', error)
    return { prompts: [], total: 0 }
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
