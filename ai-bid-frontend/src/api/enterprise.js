import api from './index'

// ========== 企业资料 ==========

// 获取企业信息
export const getEnterpriseInfo = () => api.get('/enterprise/info')

// 更新企业信息
export const updateEnterpriseInfo = (data) => api.put('/enterprise/info', data)

// 上传企业资质
export const uploadEnterpriseQualification = (formData) => api.post('/enterprise/qualifications', formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
})

// 获取企业资质列表
export const getEnterpriseQualifications = (params) => api.get('/enterprise/qualifications', { params })

// 删除企业资质
export const deleteEnterpriseQualification = (id) => api.delete(`/enterprise/qualifications/${id}`)

// ========== 资质管理 ==========

// 获取资质类型列表
export const getQualificationTypes = () => api.get('/enterprise/qualification-types')

// 获取资质详情
export const getQualificationDetail = (id) => api.get(`/enterprise/qualifications/${id}`)

// 更新资质信息
export const updateQualification = (id, data) => api.put(`/enterprise/qualifications/${id}`, data)

// ========== 业绩管理 ==========

// 获取项目业绩列表
export const getProjectExperiences = (params) => api.get('/enterprise/experiences', { params })

// 获取项目业绩详情
export const getProjectExperienceDetail = (id) => api.get(`/enterprise/experiences/${id}`)

// 添加项目业绩
export const addProjectExperience = (data) => api.post('/enterprise/experiences', data)

// 更新项目业绩
export const updateProjectExperience = (id, data) => api.put(`/enterprise/experiences/${id}`, data)

// 删除项目业绩
export const deleteProjectExperience = (id) => api.delete(`/enterprise/experiences/${id}`)

// ========== 财务数据 ==========

// 获取财务数据
export const getFinancialData = () => api.get('/enterprise/financial')

// 更新财务数据
export const updateFinancialData = (data) => api.put('/enterprise/financial', data)

// ========== 企业资料完整性检查 ==========

// 检查资料完整性
export const checkEnterpriseCompleteness = () => api.get('/enterprise/completeness')

// 获取完善建议
export const getCompletenessSuggestions = () => api.get('/enterprise/suggestions')