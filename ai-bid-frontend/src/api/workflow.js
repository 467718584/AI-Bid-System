import api from './index'

// ========== 工作流定义 ==========

// 获取工作流列表
export const getWorkflowList = (params) => api.get('/workflow/list', { params })

// 获取工作流详情
export const getWorkflowDetail = (id) => api.get(`/workflow/${id}`)

// 创建工作流
export const createWorkflow = (data) => api.post('/workflow', data)

// 更新工作流
export const updateWorkflow = (id, data) => api.put(`/workflow/${id}`, data)

// 删除工作流
export const deleteWorkflow = (id) => api.delete(`/workflow/${id}`)

// 复制工作流
export const duplicateWorkflow = (id) => api.post(`/workflow/${id}/duplicate`)

// 启用/禁用工作流
export const toggleWorkflowStatus = (id, enabled) => api.post(`/workflow/${id}/toggle`, { enabled })

// ========== 工作流节点 ==========

// 获取工作流节点
export const getWorkflowNodes = (workflowId) => api.get(`/workflow/${workflowId}/nodes`)

// 创建工作流节点
export const createWorkflowNode = (workflowId, data) => api.post(`/workflow/${workflowId}/nodes`, data)

// 更新工作流节点
export const updateWorkflowNode = (workflowId, nodeId, data) => api.put(`/workflow/${workflowId}/nodes/${nodeId}`, data)

// 删除工作流节点
export const deleteWorkflowNode = (workflowId, nodeId) => api.delete(`/workflow/${workflowId}/nodes/${nodeId}`)

// 重新排序节点
export const reorderWorkflowNodes = (workflowId, data) => api.post(`/workflow/${workflowId}/nodes/reorder`, data)

// ========== 工作流执行 ==========

// 启动工作流实例
export const startWorkflowInstance = (workflowId, data) => api.post(`/workflow/${workflowId}/instances`, data)

// 获取工作流实例列表
export const getWorkflowInstances = (params) => api.get('/workflow/instances', { params })

// 获取工作流实例详情
export const getWorkflowInstanceDetail = (instanceId) => api.get(`/workflow/instances/${instanceId}`)

// 获取工作流实例状态
export const getWorkflowInstanceStatus = (instanceId) => api.get(`/workflow/instances/${instanceId}/status`)

// 取消工作流实例
export const cancelWorkflowInstance = (instanceId) => api.post(`/workflow/instances/${instanceId}/cancel`)

// 重试工作流节点
export const retryWorkflowNode = (instanceId, nodeId) => api.post(`/workflow/instances/${instanceId}/nodes/${nodeId}/retry`)

// 获取工作流执行日志
export const getWorkflowExecutionLogs = (instanceId, params) => api.get(`/workflow/instances/${instanceId}/logs`, { params })

// ========== 工作流模板 ==========

// 获取工作流模板列表
export const getWorkflowTemplates = () => api.get('/workflow/templates')

// 从模板创建工作流
export const createWorkflowFromTemplate = (templateId, data) => api.post(`/workflow/templates/${templateId}/create`, data)

// ========== 工作流统计 ==========

// 获取工作流统计
export const getWorkflowStats = () => api.get('/workflow/stats')

// 获取工作流节点类型
export const getWorkflowNodeTypes = () => api.get('/workflow/node-types')