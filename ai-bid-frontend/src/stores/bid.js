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
      setOutline(res.data.outline)
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