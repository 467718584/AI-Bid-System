<template>
  <div class="knowledge-view">
    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-input
          v-model="keyword"
          placeholder="搜索文档内容"
          style="width: 280px"
          clearable
          @clear="handleSearch"
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select v-model="categoryId" placeholder="文档分类" clearable style="width: 150px">
          <el-option
            v-for="item in categories"
            :key="item.id"
            :label="item.name"
            :value="item.id"
          />
        </el-select>
        <el-button type="primary" @click="handleSearch">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
      </div>
      <div class="toolbar-right">
        <el-button type="primary" @click="handleUpload">
          <el-icon><Upload /></el-icon>
          上传文档
        </el-button>
        <el-button @click="handleBatchImport">
          <el-icon><FolderOpened /></el-icon>
          批量导入
        </el-button>
      </div>
    </div>

    <!-- 搜索结果 -->
    <div v-if="searchMode" class="search-results">
      <div class="search-header">
        <span>搜索到 {{ searchResults.length }} 条结果</span>
        <el-button text @click="searchMode = false">清除搜索</el-button>
      </div>
      <div class="result-list">
        <div
          v-for="item in searchResults"
          :key="item.id"
          class="result-item"
          @click="handleViewDoc(item)"
        >
          <div class="result-title">{{ item.title }}</div>
          <div class="result-snippet">{{ item.snippet || item.content?.substring(0, 200) }}</div>
          <div class="result-meta">
            <el-tag size="small">{{ item.category }}</el-tag>
            <span class="date">{{ item.updatedAt }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 文档列表 -->
    <div v-else class="doc-list">
      <el-table :data="documents" style="width: 100%">
        <el-table-column prop="title" label="文档标题" min-width="200" />
        <el-table-column prop="category" label="分类" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ row.category || '未分类' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="fileType" label="类型" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="getFileType(row.fileType)">{{ row.fileType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="updatedAt" label="更新时间" width="160" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleViewDoc(row)">
              查看
            </el-button>
            <el-button type="primary" link size="small" @click="handleEditDoc(row)">
              编辑
            </el-button>
            <el-button type="danger" link size="small" @click="handleDeleteDoc(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="!documents.length" class="empty-state">
        <el-empty description="暂无文档">
          <el-button type="primary" @click="handleUpload">上传文档</el-button>
        </el-empty>
      </div>
    </div>

    <!-- 上传对话框 -->
    <el-dialog v-model="uploadDialogVisible" title="上传知识文档" width="500px">
      <el-form :model="uploadForm" label-width="100px">
        <el-form-item label="文档标题">
          <el-input v-model="uploadForm.title" placeholder="请输入文档标题" />
        </el-form-item>
        <el-form-item label="文档分类">
          <el-select v-model="uploadForm.category" placeholder="请选择分类" style="width: 100%">
            <el-option
              v-for="item in categories"
              :key="item.id"
              :label="item.name"
              :value="item.name"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="上传文件">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            drag
          >
            <el-icon><Upload /></el-icon>
            <span>将文件拖到此处，或 <em>点击上传</em></span>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleUploadSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 查看对话框 -->
    <el-dialog v-model="viewDialogVisible" title="文档详情" width="700px">
      <div class="doc-content" v-html="currentDoc.content"></div>
      <template #footer>
        <el-button @click="viewDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Upload, FolderOpened } from '@element-plus/icons-vue'
import {
  getKnowledgeDocuments,
  getKnowledgeCategories,
  searchKnowledge,
  uploadKnowledgeDocument,
  deleteKnowledgeDocument
} from '@/api/knowledge'

const keyword = ref('')
const categoryId = ref('')
const searchMode = ref(false)
const searchResults = ref([])
const documents = ref([])
const categories = ref([])

const uploadDialogVisible = ref(false)
const viewDialogVisible = ref(false)
const currentDoc = ref({})
const uploadForm = ref({
  title: '',
  category: '',
  file: null
})
const uploadRef = ref(null)

const getFileType = (type) => {
  const map = { pdf: 'danger', docx: 'primary', doc: 'primary', txt: 'info' }
  return map[type] || 'info'
}

const handleSearch = async () => {
  if (!keyword.value && !categoryId.value) {
    loadDocuments()
    return
  }
  try {
    const res = await searchKnowledge({ keyword: keyword.value, categoryId: categoryId.value })
    searchResults.value = res.data || []
    searchMode.value = true
  } catch (error) {
    ElMessage.error('搜索失败')
  }
}

const handleUpload = () => {
  uploadDialogVisible.value = true
}

const handleBatchImport = () => {
  ElMessage.info('批量导入功能开发中')
}

const handleFileChange = (file) => {
  uploadForm.value.file = file.raw
}

const handleUploadSubmit = async () => {
  if (!uploadForm.value.title) {
    ElMessage.warning('请输入文档标题')
    return
  }
  if (!uploadForm.value.file) {
    ElMessage.warning('请选择文件')
    return
  }
  try {
    const formData = new FormData()
    formData.append('file', uploadForm.value.file)
    formData.append('title', uploadForm.value.title)
    formData.append('category', uploadForm.value.category)
    await uploadKnowledgeDocument(formData)
    ElMessage.success('上传成功')
    uploadDialogVisible.value = false
    loadDocuments()
  } catch (error) {
    ElMessage.error('上传失败')
  }
}

const handleViewDoc = (doc) => {
  currentDoc.value = doc
  viewDialogVisible.value = true
}

const handleEditDoc = (doc) => {
  ElMessage.info('编辑功能开发中')
}

const handleDeleteDoc = async (doc) => {
  try {
    await ElMessageBox.confirm('确定要删除该文档吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteKnowledgeDocument(doc.id)
    ElMessage.success('删除成功')
    loadDocuments()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const loadDocuments = async () => {
  try {
    const [docRes, catRes] = await Promise.all([
      getKnowledgeDocuments({ page: 1, pageSize: 100 }),
      getKnowledgeCategories()
    ])
    documents.value = docRes.data?.list || []
    categories.value = catRes.data || []
  } catch (error) {
    // 使用空数据
  }
}

onMounted(() => {
  loadDocuments()
})
</script>

<style scoped>
.knowledge-view {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #fff;
  border-radius: 8px;
}

.toolbar-left {
  display: flex;
  gap: 12px;
  align-items: center;
}

.toolbar-right {
  display: flex;
  gap: 8px;
}

.search-results {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
}

.search-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  color: #666;
}

.result-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.result-item {
  padding: 16px;
  border: 1px solid #e6e6e6;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.result-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
}

.result-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.result-snippet {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  margin-bottom: 8px;
}

.result-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.result-meta .date {
  font-size: 12px;
  color: #999;
}

.doc-list,
.search-results {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
}

.empty-state {
  display: flex;
  justify-content: center;
  padding: 60px 0;
}

.doc-content {
  line-height: 1.8;
  color: #333;
}
</style>