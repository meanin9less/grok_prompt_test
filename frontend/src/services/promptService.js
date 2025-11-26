const BACKEND_URL = 'http://localhost:8000'

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

export async function getPromptContent(promptKey) {
  try {
    const response = await fetch(`${BACKEND_URL}/api/prompts/${promptKey}`)
    if (!response.ok) throw new Error(`Failed to fetch prompt: ${promptKey}`)
    return await response.json()
  } catch (error) {
    console.error(`Error fetching prompt content for ${promptKey}:`, error)
    return { key: promptKey, content: '', error: error.message }
  }
}