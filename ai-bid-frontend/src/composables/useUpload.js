/**
 * 文件上传组合式函数
 */
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'

export function useUpload(options = {}) {
  const {
    accept = '.pdf,.doc,.docx,.txt',
    maxSize = 10 * 1024 * 1024, // 10MB
    maxFiles = 10,
    onSuccess = null,
    onError = null
  } = options

  const uploadRef = ref(null)
  const fileList = ref([])
  const uploading = ref(false)
  const uploadProgress = ref(0)

  const headers = computed(() => ({
    Authorization: `Bearer ${localStorage.getItem('token') || ''}`
  }))

  const formatFileSize = (size) => {
    if (size < 1024) return `${size} B`
    if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`
    return `${(size / (1024 * 1024)).toFixed(1)} MB`
  }

  const validateFile = (file) => {
    // 验证文件类型
    const ext = '.' + file.name.split('.').pop().toLowerCase()
    const acceptTypes = accept.split(',').map((t) => t.trim().toLowerCase())
    if (!acceptTypes.includes(ext)) {
      ElMessage.error(`不支持 ${ext} 格式，请上传 ${accept} 格式的文件`)
      return false
    }

    // 验证文件大小
    if (file.size > maxSize) {
      ElMessage.error(`文件大小不能超过 ${formatFileSize(maxSize)}`)
      return false
    }

    // 验证文件数量
    if (fileList.value.length >= maxFiles) {
      ElMessage.error(`最多只能上传 ${maxFiles} 个文件`)
      return false
    }

    return true
  }

  const handleBeforeUpload = (file) => {
    return validateFile(file)
  }

  const handleSuccess = (response, file) => {
    file.id = response.data?.id
    ElMessage.success(`${file.name} 上传成功`)
    onSuccess?.(file, response)
  }

  const handleError = (error, file) => {
    ElMessage.error(`${file.name} 上传失败`)
    onError?.(error, file)
  }

  const handleRemove = (file, files) => {
    fileList.value = files
  }

  const clearFiles = () => {
    fileList.value = []
    uploadRef.value?.clearFiles()
  }

  return {
    uploadRef,
    fileList,
    uploading,
    uploadProgress,
    headers,
    formatFileSize,
    handleBeforeUpload,
    handleSuccess,
    handleError,
    handleRemove,
    clearFiles
  }
}