import { marked } from 'marked'
import DOMPurify from 'dompurify'

export function useChatMarkdown() {
  const parseMarkdown = (text) => {
    const html = marked(text)
    return DOMPurify.sanitize(html)
  }

  return {
    parseMarkdown
  }
}
