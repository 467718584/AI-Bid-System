import api from './index'

// 获取项目列表
export const getProjectList = (params) => api.get('/project/list', { params })

// 获取项目详情
export const getProjectDetail = (id) => api.get(`/project/${id}`)

// 创建项目
export const createProject = (data) => api.post('/project', data)

// 更新项目
export const updateProject = (id, data) => api.put(`/project/${id}`, data)

// 删除项目
export const deleteProject = (id) => api.delete(`/project/${id}`)