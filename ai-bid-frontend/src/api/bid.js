import api from './index'

// ========== 标书管理 ==========

// 获取标书列表
export const getBidList = (params) => api.get('/bid/list', { params })

// 获取标书详情
export const getBidDetail = (id) => api.get(`/bid/${id}`)

// 创建标书
export const createBid = (data) => api.post('/bid', data)

// 更新标书
export const updateBid = (id, data) => api.put(`/bid/${id}`, data)

// 删除标书
export const deleteBid = (id) => api.delete(`/bid/${id}`)

// 提交标书
export const submitBid = (id) => api.post(`/bid/${id}/submit`)

// 导出标书
export const exportBid = (id, format = 'docx') => api.get(`/bid/${id}/export`, {
  params: { format },
  responseType: 'blob'
})

// ========== 技术标生成 ==========

// 生成目录
export const generateBidOutline = (data) => api.post('/ai/bid/outline', data)

// 生成正文内容
export const generateBidContent = (data) => api.post('/ai/bid/content', data)

// 智能润色
export const polishBidContent = (data) => api.post('/ai/bid/polish', data)

// 语法检查
export const checkBidGrammar = (data) => api.post('/ai/bid/grammar', data)

// 全文生成流水线
export const runBidPipeline = (data) => api.post('/ai/bid/pipeline', data)

// 获取流水线状态
export const getPipelineStatus = (bidId) => api.get(`/ai/bid/pipeline/${bidId}/status`)

// ========== 标书版本 ==========

// 获取版本列表
export const getBidVersions = (bidId) => api.get(`/bid/${bidId}/versions`)

// 获取指定版本
export const getBidVersion = (bidId, versionId) => api.get(`/bid/${bidId}/versions/${versionId}`)

// 回滚版本
export const rollbackBidVersion = (bidId, versionId) => api.post(`/bid/${bidId}/versions/${versionId}/rollback`)

// ========== 标书协作 ==========

// 获取协作成员
export const getBidCollaborators = (bidId) => api.get(`/bid/${bidId}/collaborators`)

// 添加协作成员
export const addBidCollaborator = (bidId, data) => api.post(`/bid/${bidId}/collaborators`, data)

// 移除协作成员
export const removeBidCollaborator = (bidId, userId) => api.delete(`/bid/${bidId}/collaborators/${userId}`)

// 获取协作记录
export const getBidActivities = (bidId, params) => api.get(`/bid/${bidId}/activities`, { params })