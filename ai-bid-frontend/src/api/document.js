import api from './index'

// 获取文档列表
export const getDocumentList = (params) => api.get('/document/list', { params })

// 获取文档详情
export const getDocumentDetail = (id) => api.get(`/document/${id}`)

// 创建文档
export const createDocument = (data) => api.post('/document', data)

// 更新文档
export const updateDocument = (id, data) => api.put(`/document/${id}`, data)

// 删除文档
export const deleteDocument = (id) => api.delete(`/document/${id}`)

// 下载文档
export const downloadDocument = (id) => api.get(`/document/${id}/download`, { responseType: 'blob' })