import { marked } from 'marked'
import DOMPurify from 'dompurify'

marked.setOptions({
  gfm: true,
  breaks: true
})

export function useChatMarkdown() {
  const parseMarkdown = (text) => {
    const safe = String(text ?? '')
    try {
      const html = marked.parse(safe)
      return DOMPurify.sanitize(html)
    } catch (err) {
      console.error('Markdown parse error:', err)
      // 파싱 실패 시 줄바꿈만 유지한 기본 HTML 반환
      return safe.replace(/\n/g, '<br>')
    }
  }

  return {
    parseMarkdown
  }
}
