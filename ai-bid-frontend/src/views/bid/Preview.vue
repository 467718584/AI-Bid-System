<template>
  <div class="bid-preview">
    <div class="preview-header">
      <el-button @click="handleBack">
        <el-icon><ArrowLeft /></el-icon>
        返回
      </el-button>
      <h2>{{ bidTitle }}</h2>
      <el-button type="primary" @click="handleExport">
        <el-icon><Download /></el-icon>
        导出Word
      </el-button>
    </div>
    <div class="preview-content">
      <BidPreview :content="content" :outline="outline" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import BidPreview from '@/components/bid/BidPreview.vue'
import { ArrowLeft, Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()

const bidTitle = ref('标书预览')
const content = ref('')
const outline = ref([])

const handleBack = () => {
  router.push(`/bid/${route.params.id}`)
}

const handleExport = () => {
  ElMessage.info('导出功能开发中')
}

onMounted(async () => {
  const id = route.params.id
  if (id) {
    // TODO: 加载标书数据
  }
})
</script>

<style scoped>
.bid-preview {
  min-height: 100%;
  background: var(--el-bg-color);
  border-radius: var(--card-radius);
}

.preview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--el-spacing-md) var(--el-spacing-lg);
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.preview-header h2 {
  margin: 0;
  font-size: var(--el-font-size-lg);
}

.preview-content {
  padding: var(--el-spacing-lg);
}
</style>