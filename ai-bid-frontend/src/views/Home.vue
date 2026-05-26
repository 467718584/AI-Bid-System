<template>
  <div class="home-container">
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <h1 class="logo">AI智能投标系统</h1>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-icon><User /></el-icon>
              <span>{{ userStore.userInfo?.name || '用户' }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item command="settings">系统设置</el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-container>
        <el-aside width="220px">
          <el-menu
            :default-active="activeMenu"
            router
            class="sidebar-menu"
          >
            <el-menu-item index="/">
              <el-icon><HomeFilled /></el-icon>
              <span>首页</span>
            </el-menu-item>
            <el-menu-item index="/bid">
              <el-icon><Document /></el-icon>
              <span>标书管理</span>
            </el-menu-item>
            <el-menu-item index="/project">
              <el-icon><Folder /></el-icon>
              <span>项目管理</span>
            </el-menu-item>
            <el-menu-item index="/material">
              <el-icon><FolderOpened /></el-icon>
              <span>素材库</span>
            </el-menu-item>
            <el-menu-item index="/knowledge">
              <el-icon><Collection /></el-icon>
              <span>知识库</span>
            </el-menu-item>
            <el-menu-item index="/workflow">
              <el-icon><Operation /></el-icon>
              <span>工作流</span>
            </el-menu-item>
            <el-menu-item index="/enterprise">
              <el-icon><OfficeBuilding /></el-icon>
              <span>企业资料</span>
            </el-menu-item>
          </el-menu>
        </el-aside>
        <el-main class="main-content">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessageBox } from 'element-plus'
import { User, ArrowDown, HomeFilled, Document, Folder, FolderOpened, Collection, Operation, OfficeBuilding } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const activeMenu = computed(() => route.path)

const handleCommand = async (command) => {
  switch (command) {
    case 'logout':
      await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
      await userStore.logout()
      router.push('/login')
      break
    case 'profile':
      break
    case 'settings':
      break
  }
}
</script>

<style scoped>
.home-container {
  width: 100%;
  height: 100vh;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color-lighter);
  padding: 0 var(--el-spacing-lg);
}

.header-left .logo {
  font-size: var(--el-font-size-xl);
  font-weight: 600;
  color: var(--el-color-primary);
  margin: 0;
}

.header-right .user-info {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: var(--el-border-radius-base);
  transition: background var(--el-transition-fast-duration);
}

.header-right .user-info:hover {
  background: var(--el-fill-color);
}

.sidebar-menu {
  height: calc(100vh - 60px);
  border-right: none;
}

.main-content {
  background: var(--el-bg-color-page);
  padding: var(--el-spacing-lg);
  overflow-y: auto;
}
</style>