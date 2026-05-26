import api from './index'

// 生成标书目录
export const generateOutline = (data) => api.post('/ai/bid/outline', data)

// 生成标书内容
export const generateContent = (data) => api.post('/ai/bid/content', data)

// 智能润色
export const polishContent = (data) => api.post('/ai/bid/polish', data)

// 语法检查
export const checkGrammar = (data) => api.post('/ai/bid/grammar', data)

// 知识库检索
export const searchKnowledge = (params) => api.get('/ai/knowledge/search', { params })

// 上传文件并解析
export const parseDocument = (formData) => api.post('/ai/document/parse', formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
})