import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { title: '首页' }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/Index.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/bid',
    name: 'BidIndex',
    component: () => import('@/views/bid/Index.vue'),
    meta: { title: '标书列表' }
  },
  {
    path: '/bid/create',
    name: 'BidCreate',
    component: () => import('@/views/bid/Editor.vue'),
    meta: { title: '创建标书' }
  },
  {
    path: '/bid/:id',
    name: 'BidEditor',
    component: () => import('@/views/bid/Editor.vue'),
    meta: { title: '标书编辑' }
  },
  {
    path: '/bid/:id/preview',
    name: 'BidPreview',
    component: () => import('@/views/bid/Preview.vue'),
    meta: { title: '标书预览' }
  },
  // 新增：标书编辑器（整合版）
  {
    path: '/bid-editor',
    name: 'BidEditorView',
    component: () => import('@/views/BidEditorView.vue'),
    meta: { title: '标书编辑器' }
  },
  {
    path: '/bid-editor/:id',
    name: 'BidEditorViewWithId',
    component: () => import('@/views/BidEditorView.vue'),
    meta: { title: '标书编辑' }
  },
  // 工作流管理
  {
    path: '/workflow',
    name: 'Workflow',
    component: () => import('@/views/WorkflowView.vue'),
    meta: { title: '工作流管理' }
  },
  // 素材库
  {
    path: '/material',
    name: 'MaterialLibrary',
    component: () => import('@/views/MaterialLibraryView.vue'),
    meta: { title: '素材库' }
  },
  // 企业资料
  {
    path: '/enterprise',
    name: 'EnterpriseProfile',
    component: () => import('@/views/EnterpriseProfileView.vue'),
    meta: { title: '企业资料' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - AI智能投标系统` : 'AI智能投标系统'
  next()
})

export default router