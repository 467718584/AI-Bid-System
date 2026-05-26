import api from './index'

// ========== 知识库检索 ==========

// 搜索知识库
export const searchKnowledge = (params) => api.get('/knowledge/search', { params })

// 获取知识分类
export const getKnowledgeCategories = () => api.get('/knowledge/categories')

// 获取知识文档列表
export const getKnowledgeDocuments = (params) => api.get('/knowledge/documents', { params })

// 获取知识文档详情
export const getKnowledgeDocument = (id) => api.get(`/knowledge/documents/${id}`)

// 添加知识文档
export const addKnowledgeDocument = (data) => api.post('/knowledge/documents', data)

// 更新知识文档
export const updateKnowledgeDocument = (id, data) => api.put(`/knowledge/documents/${id}`, data)

// 删除知识文档
export const deleteKnowledgeDocument = (id) => api.delete(`/knowledge/documents/${id}`)

// 上传知识文档（解析）
export const uploadKnowledgeDocument = (formData) => api.post('/knowledge/upload', formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
})

// ========== RAG检索 ==========

// 向量检索
export const vectorSearch = (params) => api.post('/knowledge/vector/search', params)

// 混合检索（关键词+向量）
export const hybridSearch = (params) => api.post('/knowledge/hybrid/search', params)

// 获取相关片段
export const getRelatedChunks = (params) => api.post('/knowledge/chunks/related', params)

// ========== 知识库管理 ==========

// 获取知识库统计
export const getKnowledgeStats = () => api.get('/knowledge/stats')

// 重建向量索引
export const rebuildVectorIndex = () => api.post('/knowledge/rebuild-index')

// 批量导入知识
export const batchImportKnowledge = (formData) => api.post('/knowledge/batch-import', formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
})

// 导出知识
export const exportKnowledge = (params) => api.get('/knowledge/export', {
  params,
  responseType: 'blob'
})