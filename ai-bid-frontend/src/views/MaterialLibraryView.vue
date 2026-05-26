<template>
  <div class="material-library-view">
    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-input
          v-model="keyword"
          placeholder="搜索素材名称或内容"
          style="width: 240px"
          clearable
          @clear="handleSearch"
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select v-model="categoryId" placeholder="素材分类" clearable style="width: 150px">
          <el-option
            v-for="item in categories"
            :key="item.id"
            :label="item.name"
            :value="item.id"
          />
        </el-select>
        <el-select v-model="fileType" placeholder="文件类型" clearable style="width: 120px">
          <el-option label="图片" value="image" />
          <el-option label="文档" value="document" />
          <el-option label="视频" value="video" />
          <el-option label="音频" value="audio" />
        </el-select>
        <el-button type="primary" @click="handleSearch">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
      </div>
      <div class="toolbar-right">
        <el-button type="primary" @click="handleUpload">
          <el-icon><Upload /></el-icon>
          上传素材
        </el-button>
        <el-button @click="handleBatchImport">
          <el-icon><FolderOpened /></el-icon>
          批量导入
        </el-button>
      </div>
    </div>

    <!-- 素材统计 -->
    <div class="stats-cards">
      <el-row :gutter="16">
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-icon" style="background: #409eff">
              <el-icon><Folder /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.total }}</div>
              <div class="stat-label">素材总数</div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-icon" style="background: #67c23a">
              <el-icon><Picture /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.images }}</div>
              <div class="stat-label">图片素材</div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-icon" style="background: #e6a23c">
              <el-icon><Document /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.documents }}</div>
              <div class="stat-label">文档素材</div>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-card">
            <div class="stat-icon" style="background: #f56c6c">
              <el-icon><VideoCamera /></el-icon>
            </div>
            <div class="stat-content">
              <div class="stat-value">{{ stats.videos }}</div>
              <div class="stat-label">视频素材</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 素材列表/网格视图 -->
    <div class="material-content">
      <div class="view-tabs">
        <el-radio-group v-model="viewMode">
          <el-radio-button label="grid">网格视图</el-radio-button>
          <el-radio-button label="list">列表视图</el-radio-button>
        </el-radio-group>
        <el-button type="text" @click="handleManageCategory">
          <el-icon><Setting /></el-icon>
          管理分类
        </el-button>
      </div>

      <!-- 网格视图 -->
      <div v-if="viewMode === 'grid'" class="material-grid">
        <el-row :gutter="16">
          <el-col
            v-for="item in materialList"
            :key="item.id"
            :xs="24"
            :sm="12"
            :md="8"
            :lg="6"
            :xl="4"
          >
            <div class="material-card" @click="handlePreview(item)">
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
                <div class="material-overlay">
                  <el-button type="primary" circle @click.stop="handleInsert(item)">
                    <el-icon><Plus /></el-icon>
                  </el-button>
                  <el-button type="danger" circle @click.stop="handleDelete(item)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
              </div>
              <div class="material-info">
                <div class="material-name">{{ item.name }}</div>
                <div class="material-meta">
                  <el-tag size="small">{{ item.categoryName }}</el-tag>
                  <span class="material-size">{{ formatSize(item.size) }}</span>
                </div>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 列表视图 -->
      <div v-else class="material-list">
        <el-table :data="materialList" @row-click="handlePreview">
          <el-table-column label="预览" width="80">
            <template #default="{ row }">
              <el-image
                v-if="row.type === 'image'"
                :src="row.url"
                fit="cover"
                style="width: 50px; height: 50px; border-radius: 4px"
              />
              <el-icon v-else style="font-size: 24px"><Document /></el-icon>
            </template>
          </el-table-column>
          <el-table-column prop="name" label="素材名称" min-width="200" />
          <el-table-column prop="categoryName" label="分类" width="120" />
          <el-table-column prop="type" label="类型" width="80">
            <template #default="{ row }">
              <el-tag size="small">{{ getTypeName(row.type) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="size" label="大小" width="100">
            <template #default="{ row }">
              {{ formatSize(row.size) }}
            </template>
          </el-table-column>
          <el-table-column prop="updateTime" label="更新时间" width="180" />
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click.stop="handleInsert(row)">
                插入
              </el-button>
              <el-button type="danger" link size="small" @click.stop="handleDelete(row)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[12, 24, 48, 96]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </div>

    <!-- 上传对话框 -->
    <el-dialog v-model="uploadDialogVisible" title="上传素材" width="600px">
      <el-form :model="uploadForm" label-width="80px">
        <el-form-item label="素材名称">
          <el-input v-model="uploadForm.name" placeholder="请输入素材名称" />
        </el-form-item>
        <el-form-item label="素材分类">
          <el-select v-model="uploadForm.categoryId" placeholder="请选择分类" style="width: 100%">
            <el-option
              v-for="item in categories"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="素材文件">
          <el-upload
            ref="uploadRef"
            drag
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
            <template #tip>
              <div class="el-upload__tip">支持图片、文档、视频等格式，单个文件不超过50MB</div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item label="素材描述">
          <el-input
            v-model="uploadForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入素材描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="uploading" @click="confirmUpload">上传</el-button>
      </template>
    </el-dialog>

    <!-- 素材预览对话框 -->
    <el-dialog v-model="previewDialogVisible" :title="previewItem?.name" width="800px">
      <div class="preview-content">
        <el-image
          v-if="previewItem?.type === 'image'"
          :src="previewItem?.url"
          style="max-width: 100%"
          fit="contain"
        />
        <div v-else class="preview-placeholder">
          <el-icon style="font-size: 80px"><Document /></el-icon>
          <div>暂不支持预览</div>
        </div>
      </div>
    </el-dialog>

    <!-- 管理分类对话框 -->
    <el-dialog v-model="categoryDialogVisible" title="管理分类" width="500px">
      <div class="category-management">
        <el-button type="primary" size="small" @click="handleAddCategory">
          <el-icon><Plus /></el-icon>
          新增分类
        </el-button>
        <el-table :data="categories" size="small" style="margin-top: 16px">
          <el-table-column prop="name" label="分类名称" />
          <el-table-column prop="count" label="素材数量" width="100" />
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="handleEditCategory(row)">
                编辑
              </el-button>
              <el-button type="danger" link size="small" @click="handleDeleteCategory(row)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search,
  Upload,
  FolderOpened,
  Folder,
  Picture,
  Document,
  VideoCamera,
  Setting,
  Plus,
  Delete,
  UploadFilled
} from '@element-plus/icons-vue'
import { getMaterialList, getMaterialCategory, uploadMaterial, deleteMaterial } from '@/api/material'

// 状态
const keyword = ref('')
const categoryId = ref('')
const fileType = ref('')
const viewMode = ref('grid')
const currentPage = ref(1)
const pageSize = ref(12)
const total = ref(0)
const materialList = ref([])
const categories = ref([])

// 统计
const stats = ref({
  total: 0,
  images: 0,
  documents: 0,
  videos: 0
})

// 上传
const uploadDialogVisible = ref(false)
const uploading = ref(false)
const uploadRef = ref(null)
const uploadForm = ref({
  name: '',
  categoryId: '',
  description: '',
  file: null
})

// 预览
const previewDialogVisible = ref(false)
const previewItem = ref(null)

// 分类管理
const categoryDialogVisible = ref(false)

// ========== 生命周期 ==========

onMounted(async () => {
  await loadCategories()
  await loadMaterialList()
})

// ========== 方法 ==========

const loadCategories = async () => {
  try {
    const res = await getMaterialCategory()
    categories.value = res.data || []
  } catch (error) {
    ElMessage.error('加载分类失败')
  }
}

const loadMaterialList = async () => {
  try {
    const res = await getMaterialList({
      keyword: keyword.value,
      categoryId: categoryId.value,
      type: fileType.value,
      page: currentPage.value,
      pageSize: pageSize.value
    })
    materialList.value = res.data?.list || []
    total.value = res.data?.total || 0
  } catch (error) {
    ElMessage.error('加载素材列表失败')
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadMaterialList()
}

const handleSizeChange = () => {
  currentPage.value = 1
  loadMaterialList()
}

const handlePageChange = () => {
  loadMaterialList()
}

const handleUpload = () => {
  uploadForm.value = {
    name: '',
    categoryId: '',
    description: '',
    file: null
  }
  uploadDialogVisible.value = true
}

const handleFileChange = (file) => {
  uploadForm.value.file = file.raw
  if (!uploadForm.value.name) {
    uploadForm.value.name = file.name.replace(/\.[^.]+$/, '')
  }
}

const handleFileRemove = () => {
  uploadForm.value.file = null
}

const confirmUpload = async () => {
  if (!uploadForm.value.file) {
    ElMessage.warning('请选择文件')
    return
  }
  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', uploadForm.value.file)
    if (uploadForm.value.name) formData.append('name', uploadForm.value.name)
    if (uploadForm.value.categoryId) formData.append('categoryId', uploadForm.value.categoryId)
    if (uploadForm.value.description) formData.append('description', uploadForm.value.description)
    await uploadMaterial(formData)
    ElMessage.success('上传成功')
    uploadDialogVisible.value = false
    await loadMaterialList()
  } catch (error) {
    ElMessage.error('上传失败')
  } finally {
    uploading.value = false
  }
}

const handleBatchImport = () => {
  ElMessage.info('批量导入功能开发中')
}

const handlePreview = (item) => {
  previewItem.value = item
  previewDialogVisible.value = true
}

const handleInsert = (item) => {
  // 将素材插入到标书
  ElMessage.success(`已选择素材: ${item.name}`)
}

const handleDelete = async (item) => {
  try {
    await ElMessageBox.confirm(`确定要删除素材 "${item.name}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteMaterial(item.id)
    ElMessage.success('删除成功')
    await loadMaterialList()
  } catch {
    // 取消
  }
}

const handleManageCategory = () => {
  categoryDialogVisible.value = true
}

const handleAddCategory = () => {
  ElMessage.info('新增分类功能开发中')
}

const handleEditCategory = (row) => {
  ElMessage.info('编辑分类功能开发中')
}

const handleDeleteCategory = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除分类 "${row.name}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    ElMessage.success('删除成功')
  } catch {
    // 取消
  }
}

const formatSize = (bytes) => {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  let index = 0
  let size = bytes
  while (size >= 1024 && index < units.length - 1) {
    size /= 1024
    index++
  }
  return `${size.toFixed(1)} ${units[index]}`
}

const getTypeName = (type) => {
  const map = {
    image: '图片',
    document: '文档',
    video: '视频',
    audio: '音频'
  }
  return map[type] || type
}
</script>

<style scoped>
.material-library-view {
  display: flex;
  flex-direction: column;
  gap: var(--el-spacing-md);
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--el-spacing-md);
  background: var(--el-bg-color);
  border-radius: var(--card-radius);
}

.toolbar-left,
.toolbar-right {
  display: flex;
  align-items: center;
  gap: var(--el-spacing-md);
}

.stats-cards {
  padding: 0;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: var(--el-spacing-md);
  padding: var(--el-spacing-lg);
  background: var(--el-bg-color);
  border-radius: var(--card-radius);
}

.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 8px;
  color: #fff;
  font-size: 24px;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.stat-label {
  font-size: var(--el-font-size-sm);
  color: var(--el-text-color-secondary);
}

.material-content {
  flex: 1;
  background: var(--el-bg-color);
  border-radius: var(--card-radius);
  padding: var(--el-spacing-md);
  overflow-y: auto;
}

.view-tabs {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--el-spacing-md);
}

.material-grid {
  min-height: 400px;
}

.material-card {
  cursor: pointer;
  border-radius: var(--card-radius);
  overflow: hidden;
  background: var(--el-bg-color-page);
  transition: all var(--el-transition-fast-duration);
  margin-bottom: var(--el-spacing-md);
}

.material-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--el-box-shadow-light);
}

.material-thumb {
  position: relative;
  height: 160px;
  background: var(--el-fill-color-light);
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
  font-size: 48px;
  color: var(--el-text-color-placeholder);
}

.material-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--el-spacing-sm);
  background: rgba(0, 0, 0, 0.5);
  opacity: 0;
  transition: opacity var(--el-transition-fast-duration);
}

.material-card:hover .material-overlay {
  opacity: 1;
}

.material-info {
  padding: var(--el-spacing-md);
}

.material-name {
  font-size: var(--el-font-size-base);
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: var(--el-spacing-sm);
}

.material-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.material-size {
  font-size: var(--el-font-size-sm);
  color: var(--el-text-color-secondary);
}

.material-list {
  min-height: 400px;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: var(--el-spacing-md);
}

.preview-content {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

.preview-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--el-spacing-md);
  color: var(--el-text-color-secondary);
}
</style>