import api from './index'

// 获取素材分类列表
export const getMaterialCategory = () => api.get('/material/category')

// 获取素材列表
export const getMaterialList = (params) => api.get('/material/list', { params })

// 上传素材
export const uploadMaterial = (formData) => api.post('/material/upload', formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
})

// 删除素材
export const deleteMaterial = (id) => api.delete(`/material/${id}`)

// 获取素材详情
export const getMaterialDetail = (id) => api.get(`/material/${id}`)