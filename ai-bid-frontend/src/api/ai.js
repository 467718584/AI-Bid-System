import api from './index'

// 生成标书目录 (baseURL已经是/api，所以路径不要/api前缀)
export const generateOutline = (data) => api.post('/ai/generate/outline', data)

// 生成标书内容
export const generateContent = (data) => api.post('/ai/generate/content', data)

// 智能润色
export const polishContent = (data) => api.post('/ai/rewrite', data)

// 语法检查
export const checkGrammar = (data) => api.post('/ai/check/compliance', data)

// 知识库检索
export const searchKnowledge = (params) => api.get('/knowledge/search', { params })

// 上传文件并解析
export const parseDocument = (formData) => api.post('/ai/document/parse', formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
})