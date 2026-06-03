import { defineStore } from 'pinia'
import { ref } from 'vue'
import { generateOutline, generateContent } from '@/api/ai'

export const useBidStore = defineStore('bid', () => {
  const currentDocument = ref(null)
  const outline = ref([])
  const content = ref('')
  const isGenerating = ref(false)

  const setOutline = (data) => { outline.value = data }
  const setContent = (text) => { content.value = text }
  const setDocument = (doc) => { currentDocument.value = doc }
  const setGenerating = (val) => { isGenerating.value = val }

  const generateOutlineAsync = async (params) => {
    setGenerating(true)
    try {
      const res = await generateOutline(params)
      let outlineData = res.data.outline
      if (!outlineData && res.data.raw_response) {
        try {
          const raw = res.data.raw_response
          // Extract JSON from raw_response by finding balanced braces
          let jsonStr = raw
          if (typeof raw === 'string') {
            // Find the first { and start from there
            const firstBrace = raw.indexOf('{')
            if (firstBrace !== -1) {
              jsonStr = raw.substring(firstBrace)
              // Find the last } that balances the first {
              let braces = 0
              let end = -1
              for (let i = 0; i < jsonStr.length; i++) {
                if (jsonStr[i] === '{') braces++
                if (jsonStr[i] === '}') braces--
                if (braces === 0) { end = i + 1; break }
              }
              if (end > 0) {
                jsonStr = jsonStr.substring(0, end)
              }
            }
          }
          const parsed = JSON.parse(jsonStr)
          // Handle both {title, children} and {outline: [...]} formats
          outlineData = parsed.children || parsed.outline || parsed
          // If outlineData is still an object with title/children, use it directly
          if (outlineData.title && outlineData.children) {
            outlineData = outlineData.children
          }
        } catch (e) {
          console.error('解析outline失败:', e)
        }
      }
      setOutline(outlineData || [])
      return res
    } finally {
      setGenerating(false)
    }
  }

  const generateContentAsync = async (params) => {
    setGenerating(true)
    try {
      const res = await generateContent(params)
      setContent(res.data.content)
      return res
    } finally {
      setGenerating(false)
    }
  }

  const clearBid = () => {
    currentDocument.value = null
    outline.value = []
    content.value = ''
  }

  return {
    currentDocument,
    outline,
    content,
    isGenerating,
    setOutline,
    setContent,
    setDocument,
    setGenerating,
    generateOutlineAsync,
    generateContentAsync,
    clearBid
  }
})