const BACKEND_URL = 'http://localhost:8000'

export async function sendMessage(req, onChunk, apiPath = '/api/ai_hub/get_prompt_res_text') {
  const body = req || {}
  

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
  let handshakeReceived = false

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
    // JSON 라인이면 handshake(result_code 등)와 payload(ai_output 등)를 구분
    try {
      const parsed = JSON.parse(raw)
      if (Object.prototype.hasOwnProperty.call(parsed, 'result_code')) {
        return { handshake: parsed }
      }
      const text = parsed.ai_output || parsed.content || parsed.message || ''
      return { text: text ? String(text) : '' }
    } catch (err) {
      // not json, fall through
    }
    return { text: String(raw || '').replace(/\\n/g, '\n') }
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
            const { handshake, text } = decodeChunk(data)
            if (handshake) {
              handshakeReceived = true
              if (handshake.result_code !== 0) {
                throw new Error(handshake.result_msg || 'Request rejected by server')
              }
              continue
            }
            if (text) {
              hasChunk = true
              onChunk(text)
            }
          }
        }
      } else {
        const { handshake, text } = decodeChunk(decoded.trim())
        if (handshake) {
          handshakeReceived = true
          if (handshake.result_code !== 0) {
            throw new Error(handshake.result_msg || 'Request rejected by server')
          }
        } else if (text) {
          hasChunk = true
          onChunk(text)
        }
      }
    }

    // 남은 SSE 버퍼 처리
    if (sseBuffer.trim()) {
      const lines = sseBuffer.split('\n')
      for (const line of lines) {
        if (!line.startsWith('data:')) continue
        const data = line.slice(5).trim()
        if (!data || data === '[DONE]') continue
        const { handshake, text } = decodeChunk(data)
        if (handshake) {
          handshakeReceived = true
          if (handshake.result_code !== 0) {
            throw new Error(handshake.result_msg || 'Request rejected by server')
          }
          continue
        }
        if (text) {
          hasChunk = true
          onChunk(text)
        }
      }
    }
  } finally {
    reader.releaseLock()
  }

  if (handshakeReceived === false) {
    console.warn('No handshake received from server; proceeding with parsed chunks only')
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

export async function submitForm(req, onChunk, apiPath = '/api/forms/submit') {
  return sendMessage(req, onChunk, apiPath)
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
