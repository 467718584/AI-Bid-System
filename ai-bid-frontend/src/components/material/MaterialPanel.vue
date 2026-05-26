<template>
  <div class="material-panel">
    <div class="panel-header">
      <span class="panel-title">素材库</span>
      <el-button type="text" size="small" @click="handleRefresh">
        <el-icon><Refresh /></el-icon>
      </el-button>
    </div>

    <div class="panel-search">
      <el-input
        v-model="keyword"
        placeholder="搜索素材"
        clearable
        size="small"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
    </div>

    <div class="panel-content">
      <div v-if="loading" class="loading-state">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>加载中...</span>
      </div>

      <div v-else-if="materials.length === 0" class="empty-state">
        <el-empty description="暂无素材" :image-size="40" />
      </div>

      <div v-else class="material-list">
        <div
          v-for="item in materials"
          :key="item.id"
          class="material-item"
          @click="handleInsert(item)"
        >
          <div class="material-thumb">
            <el-image
              v-if="item.type === 'image'"
              :src="item.url"
              fit="cover"
              class="thumb-image"
            >
              <template #error>
                <div class="thumb-placeholder">
                  <el-icon><Picture /></el-icon>
                </div>
              </template>
            </el-image>
            <div v-else class="thumb-placeholder">
              <el-icon><Document /></el-icon>
            </div>
          </div>
          <div class="material-info">
            <div class="material-name">{{ item.name }}</div>
            <div class="material-type">{{ getTypeName(item.type) }}</div>
          </div>
        </div>
      </div>
    </div>

    <div class="panel-footer">
      <el-button type="primary" size="small" @click="handleNavigate">
        <el-icon><FolderOpened /></el-icon>
        素材库
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Refresh, Search, Loading, Picture, Document, FolderOpened } from '@element-plus/icons-vue'
import { getMaterialList } from '@/api/material'

const emit = defineEmits(['insert-material'])

const router = useRouter()

const keyword = ref('')
const loading = ref(false)
const materials = ref([])

onMounted(async () => {
  await loadMaterials()
})

const loadMaterials = async () => {
  loading.value = true
  try {
    const res = await getMaterialList({
      page: 1,
      pageSize: 20
    })
    materials.value = res.data?.list || []
  } catch (error) {
    materials.value = []
  } finally {
    loading.value = false
  }
}

const handleRefresh = async () => {
  await loadMaterials()
  ElMessage.success('刷新成功')
}

const handleInsert = (item) => {
  emit('insert-material', item)
}

const handleNavigate = () => {
  router.push('/material')
}

const getTypeName = (type) => {
  const map = {
    image: '图片',
    document: '文档',
    video: '视频',
    audio: '音频'
  }
  return map[type] || '其他'
}
</script>

<style scoped>
.material-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--el-spacing-sm) 0;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.panel-title {
  font-weight: 500;
  font-size: var(--el-font-size-sm);
}

.panel-search {
  padding: var(--el-spacing-sm) 0;
}

.panel-content {
  flex: 1;
  overflow-y: auto;
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--el-spacing-sm);
  padding: var(--el-spacing-lg);
  color: var(--el-text-color-secondary);
  font-size: var(--el-font-size-sm);
}

.material-list {
  display: flex;
  flex-direction: column;
  gap: var(--el-spacing-sm);
}

.material-item {
  display: flex;
  align-items: center;
  gap: var(--el-spacing-sm);
  padding: var(--el-spacing-sm);
  background: var(--el-fill-color-light);
  border-radius: var(--el-border-radius-base);
  cursor: pointer;
  transition: all var(--el-transition-fast-duration);
}

.material-item:hover {
  background: var(--el-fill-color);
}

.material-thumb {
  width: 40px;
  height: 40px;
  border-radius: 4px;
  overflow: hidden;
  flex-shrink: 0;
  background: var(--el-fill-color);
}

.thumb-image {
  width: 100%;
  height: 100%;
}

.thumb-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  color: var(--el-text-color-placeholder);
  font-size: 18px;
}

.material-info {
  flex: 1;
  overflow: hidden;
}

.material-name {
  font-size: var(--el-font-size-sm);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.material-type {
  font-size: var(--el-font-size-xs);
  color: var(--el-text-color-secondary);
}

.panel-footer {
  padding-top: var(--el-spacing-sm);
  border-top: 1px solid var(--el-border-color-lighter);
  text-align: center;
}
</style>