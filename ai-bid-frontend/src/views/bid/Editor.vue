<template>
  <div class="bid-editor">
    <div class="editor-header">
      <div class="header-left">
        <el-button @click="handleBack">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <el-input
          v-model="bidTitle"
          placeholder="请输入标书标题"
          class="title-input"
        />
      </div>
      <div class="header-right">
        <el-button @click="handlePreview">
          <el-icon><View /></el-icon>
          预览
        </el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">
          <el-icon><DocumentChecked /></el-icon>
          保存
        </el-button>
        <el-button type="success" :loading="submitting" @click="handleSubmit">
          <el-icon><Upload /></el-icon>
          提交
        </el-button>
      </div>
    </div>

    <div class="editor-content">
      <div class="outline-panel">
        <BidOutlineGenerator
          :outline="outline"
          :loading="generating"
          @generate="handleGenerateOutline"
          @update="handleUpdateOutline"
        />
      </div>
      <div class="content-panel">
        <BidContentEditor
          :content="content"
          :loading="generating"
          @update="handleUpdateContent"
        />
      </div>
      <div class="upload-panel">
        <DocumentUploader
          @upload="handleUpload"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useBidStore } from '@/stores/bid'
import { ElMessage } from 'element-plus'
import BidOutlineGenerator from '@/components/bid/BidOutlineGenerator.vue'
import BidContentEditor from '@/components/bid/BidContentEditor.vue'
import DocumentUploader from '@/components/bid/DocumentUploader.vue'
import { ArrowLeft, View, DocumentChecked, Upload } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const bidStore = useBidStore()

const bidTitle = ref('')
const saving = ref(false)
const submitting = ref(false)
const generating = ref(false)

const outline = ref([])
const content = ref('')

const handleBack = () => {
  router.push('/bid')
}

const handlePreview = () => {
  const id = route.params.id
  if (id) {
    router.push(`/bid/${id}/preview`)
  }
}

const handleSave = async () => {
  if (!bidTitle.value) {
    ElMessage.warning('请输入标书标题')
    return
  }
  saving.value = true
  try {
    // TODO: 调用保存API
    ElMessage.success('保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const handleSubmit = async () => {
  await handleSave()
  submitting.value = true
  try {
    // TODO: 调用提交API
    ElMessage.success('提交成功')
  } catch (error) {
    ElMessage.error('提交失败')
  } finally {
    submitting.value = false
  }
}

const handleGenerateOutline = async (params) => {
  generating.value = true
  try {
    await bidStore.generateOutlineAsync(params)
    outline.value = bidStore.outline
    ElMessage.success('目录生成成功')
  } catch (error) {
    ElMessage.error('目录生成失败')
  } finally {
    generating.value = false
  }
}

const handleUpdateOutline = (newOutline) => {
  outline.value = newOutline
}

const handleUpdateContent = (newContent) => {
  content.value = newContent
}

const handleUpload = (file) => {
  // TODO: 处理文件上传
  console.log('上传文件:', file)
}

onMounted(async () => {
  const id = route.params.id
  if (id) {
    // TODO: 加载标书数据
  }
})
</script>

<style scoped>
.bid-editor {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 60px - 48px);
  background: var(--el-bg-color);
  border-radius: var(--card-radius);
  overflow: hidden;
}

.editor-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--el-spacing-md) var(--el-spacing-lg);
  border-bottom: 1px solid var(--el-border-color-lighter);
  background: var(--el-bg-color);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--el-spacing-md);
}

.header-left .title-input {
  width: 300px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--el-spacing-sm);
}

.editor-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.outline-panel {
  width: 280px;
  border-right: 1px solid var(--el-border-color-lighter);
  overflow-y: auto;
}

.content-panel {
  flex: 1;
  overflow-y: auto;
}

.upload-panel {
  width: 300px;
  border-left: 1px solid var(--el-border-color-lighter);
  overflow-y: auto;
}
</style>