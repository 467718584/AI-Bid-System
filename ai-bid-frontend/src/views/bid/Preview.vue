<template>
  <div class="bid-preview">
    <div class="preview-header">
      <el-button @click="handleBack">
        <el-icon><ArrowLeft /></el-icon>
        返回
      </el-button>
      <h2>{{ bidTitle }}</h2>
      <div class="header-actions">
        <el-select v-model="selectedTemplate" placeholder="选择模板" style="width: 140px; margin-right: 8px;">
          <el-option label="标准政府投标" value="standard" />
          <el-option label="技术标专用" value="technical" />
          <el-option label="商务标专用" value="commercial" />
          <el-option label="专业工程类" value="professional" />
          <el-option label="简洁版" value="simple" />
        </el-select>
        <el-button type="primary" @click="handleExport">
          <el-icon><Download /></el-icon>
          导出Word
        </el-button>
      </div>
    </div>
    <div class="preview-content">
      <BidPreview :content="content" :outline="outline" :template="selectedTemplate" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import BidPreview from '@/components/bid/BidPreview.vue'
import { ArrowLeft, Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getBidDetail, exportHtmlToWordTemplate } from '@/api/bid'

const router = useRouter()
const route = useRoute()

const bidTitle = ref('标书预览')
const content = ref('')
const outline = ref([])
const selectedTemplate = ref('standard')

const handleBack = () => {
  router.push(`/bid/${route.params.id}`)
}

const handleExport = async () => {
  if (!content.value) {
    ElMessage.warning('没有内容可导出')
    return
  }
  try {
    await exportHtmlToWordTemplate(content.value, bidTitle.value || '标书', selectedTemplate.value)
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('Export failed:', error)
    ElMessage.error('导出失败')
  }
}

onMounted(async () => {
  const id = route.params.id
  if (id) {
    try {
      const res = await getBidDetail(String(id))
      bidTitle.value = res.data?.title || '标书预览'
      content.value = res.data?.content || ''
      outline.value = res.data?.outline || []
    } catch (error) {
      ElMessage.error('加载标书详情失败')
    }
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
  flex: 1;
}

.header-actions {
  display: flex;
  align-items: center;
}

.preview-content {
  padding: var(--el-spacing-lg);
}
</style>