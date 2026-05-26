import api from './index'

// 获取用户信息
export const getUserInfo = () => api.get('/user/info')

// 用户登录
export const login = (data) => api.post('/user/login', data)

// 用户登出
export const logout = () => api.post('/user/logout')

// 修改密码
export const changePassword = (data) => api.post('/user/change-password', data)