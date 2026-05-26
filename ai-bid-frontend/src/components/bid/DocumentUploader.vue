<template>
  <div class="document-uploader">
    <div class="panel-header">
      <span class="panel-title">文档上传</span>
    </div>

    <div class="panel-content">
      <el-upload
        ref="uploadRef"
        class="uploader"
        drag
        :action="uploadUrl"
        :headers="headers"
        :before-upload="handleBeforeUpload"
        :on-success="handleSuccess"
        :on-error="handleError"
        :on-remove="handleRemove"
        :file-list="fileList"
        accept=".pdf,.doc,.docx,.txt"
        multiple
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          拖拽文件到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持 PDF、Word、TXT 格式，单文件不超过 10MB
          </div>
        </template>
      </el-upload>

      <el-divider content-position="left">已上传文档</el-divider>

      <div v-if="fileList.length === 0" class="empty-files">
        <el-empty description="暂无上传文档" :image-size="60" />
      </div>

      <div v-else class="file-list">
        <div v-for="file in fileList" :key="file.uid || file.id" class="file-item">
          <div class="file-icon">
            <el-icon><Document /></el-icon>
          </div>
          <div class="file-info">
            <span class="file-name">{{ file.name }}</span>
            <span class="file-size">{{ formatFileSize(file.size) }}</span>
          </div>
          <div class="file-actions">
            <el-tooltip content="解析文档" placement="top">
              <el-button
                type="primary"
                link
                size="small"
                :loading="file.parsing"
                @click="handleParse(file)"
              >
                解析
              </el-button>
            </el-tooltip>
            <el-tooltip content="下载" placement="top">
              <el-button
                type="default"
                link
                size="small"
                @click="handleDownload(file)"
              >
                <el-icon><Download /></el-icon>
              </el-button>
            </el-tooltip>
            <el-tooltip content="删除" placement="top">
              <el-button
                type="danger"
                link
                size="small"
                @click="handleDelete(file)"
              >
                <el-icon><Delete /></el-icon>
              </el-button>
            </el-tooltip>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled, Document, Download, Delete } from '@element-plus/icons-vue'

const emit = defineEmits(['upload'])

const uploadRef = ref(null)
const uploadUrl = '/api/material/upload'
const fileList = ref([])

const headers = computed(() => ({
  Authorization: `Bearer ${localStorage.getItem('token') || ''}`
}))

const formatFileSize = (size) => {
  if (!size) return ''
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${(size / (1024 * 1024)).toFixed(1)} MB`
}

const handleBeforeUpload = (file) => {
  const isLt10M = file.size / 1024 / 1024 < 10
  const isValidType = ['.pdf', '.doc', '.docx', '.txt'].some(ext =>
    file.name.toLowerCase().endsWith(ext)
  )

  if (!isValidType) {
    ElMessage.error('仅支持 PDF、Word、TXT 格式')
    return false
  }
  if (!isLt10M) {
    ElMessage.error('单文件大小不能超过 10MB')
    return false
  }
  return true
}

const handleSuccess = (response, file) => {
  file.id = response.data.id
  ElMessage.success(`${file.name} 上传成功`)
  emit('upload', file)
}

const handleError = (error) => {
  ElMessage.error('上传失败，请重试')
  console.error('上传失败:', error)
}

const handleRemove = (file, files) => {
  fileList.value = files
}

const handleParse = async (file) => {
  file.parsing = true
  try {
    // TODO: 调用文档解析API
    await new Promise((resolve) => setTimeout(resolve, 2000))
    ElMessage.success(`${file.name} 解析完成`)
  } catch (error) {
    ElMessage.error('解析失败')
  } finally {
    file.parsing = false
  }
}

const handleDownload = (file) => {
  ElMessage.info(`正在下载 ${file.name}...`)
  // TODO: 调用下载API
}

const handleDelete = (file) => {
  ElMessage.info(`删除 ${file.name}`)
  fileList.value = fileList.value.filter((f) => f !== file)
  uploadRef.value?.handleRemove(file)
}
</script>

<style scoped>
.document-uploader {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--el-spacing-md);
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.panel-title {
  font-weight: 500;
  font-size: var(--el-font-size-base);
}

.panel-content {
  flex: 1;
  overflow-y: auto;
  padding: var(--el-spacing-md);
}

.uploader {
  margin-bottom: var(--el-spacing-md);
}

.empty-files {
  padding: var(--el-spacing-lg) 0;
}

.file-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.file-item {
  display: flex;
  align-items: center;
  padding: var(--el-spacing-sm);
  background: var(--el-fill-color-light);
  border-radius: var(--el-border-radius-base);
  gap: 12px;
}

.file-icon {
  font-size: 24px;
  color: var(--el-color-primary);
}

.file-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.file-name {
  font-size: var(--el-font-size-sm);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  font-size: var(--el-font-size-xs);
  color: var(--el-text-color-secondary);
}

.file-actions {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>