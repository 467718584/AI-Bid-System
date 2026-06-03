<template>
  <div class="bid-editor-view">
    <!-- 顶部工具栏 -->
    <div class="editor-toolbar">
      <div class="toolbar-left">
        <el-button @click="handleBack">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <el-input
          v-model="bidTitle"
          placeholder="请输入标书标题"
          class="title-input"
          @blur="handleTitleChange"
        />
        <el-tag v-if="bidId" type="info" size="small">ID: {{ bidId }}</el-tag>
      </div>
      <div class="toolbar-center">
        <el-button-group>
          <el-button :type="activePanel === 'outline' ? 'primary' : ''" @click="activePanel = 'outline'">
            <el-icon><List /></el-icon>
            目录
          </el-button>
          <el-button :type="activePanel === 'content' ? 'primary' : ''" @click="activePanel = 'content'">
            <el-icon><Edit /></el-icon>
            正文
          </el-button>
          <el-button :type="activePanel === 'preview' ? 'primary' : ''" @click="activePanel = 'preview'">
            <el-icon><View /></el-icon>
            预览
          </el-button>
        </el-button-group>
      </div>
      <div class="toolbar-right">
        <el-button @click="handleKnowledgeSearch">
          <el-icon><Search /></el-icon>
          知识检索
        </el-button>
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          导出
        </el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">
          <el-icon><DocumentChecked /></el-icon>
          保存
        </el-button>
        <el-button type="success" :loading="submitting" @click="handleSubmit">
          <el-icon><Promotion /></el-icon>
          提交
        </el-button>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="editor-main">
      <!-- 左侧目录面板 -->
      <div v-show="activePanel === 'outline' || activePanel === 'content'" class="outline-panel">
        <BidOutlineGenerator
          :outline="outline"
          :loading="generating"
          @generate="handleGenerateOutline"
          @update="handleUpdateOutline"
          @select-chapter="handleSelectChapter"
        />
      </div>

      <!-- 中间正文编辑区 -->
      <div v-show="activePanel === 'content' || activePanel === 'preview'" class="content-panel">
        <!-- 编辑模式 -->
        <div v-if="activePanel === 'content'" class="content-editor">
          <BidContentEditor
            :content="content"
            :chapter-title="currentChapterTitle"
            :loading="generating"
            @update="handleUpdateContent"
          />
        </div>
        <!-- 预览模式 -->
        <div v-else class="content-preview">
          <BidPreview
            :bid-title="bidTitle"
            :outline="outline"
            :content="content"
          />
        </div>
      </div>

      <!-- 右侧素材面板 -->
      <div v-show="activePanel === 'content'" class="material-panel">
        <DocumentUploader @upload="handleUpload" />
        <div class="material-divider" />
        <MaterialPanel @insert-material="handleInsertMaterial" />
      </div>
    </div>

    <!-- 知识检索抽屉 -->
    <KnowledgeDrawer
      v-model="knowledgeDrawerVisible"
      @select="handleKnowledgeSelect"
    />

    <!-- 导出设置对话框 -->
    <el-dialog v-model="exportDialogVisible" title="导出标书" width="400px">
      <el-form label-width="80px">
        <el-form-item label="导出格式">
          <el-select v-model="exportFormat" style="width: 100%">
            <el-option label="Word文档 (.docx)" value="docx" />
            <el-option label="PDF文档 (.pdf)" value="pdf" />
            <el-option label="Markdown (.md)" value="md" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="exportDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="exporting" @click="confirmExport">确认导出</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useBidStore } from '@/stores/bid'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getBidDetail, createBid, updateBid, submitBid, exportBid } from '@/api/bid'
import {
  ArrowLeft,
  List,
  Edit,
  View,
  Search,
  Download,
  DocumentChecked,
  Promotion
} from '@element-plus/icons-vue'
import BidOutlineGenerator from '@/components/bid/BidOutlineGenerator.vue'
import BidContentEditor from '@/components/bid/BidContentEditor.vue'
import BidPreview from '@/components/bid/BidPreview.vue'
import DocumentUploader from '@/components/bid/DocumentUploader.vue'
import MaterialPanel from '@/components/material/MaterialPanel.vue'
import KnowledgeDrawer from '@/components/knowledge/KnowledgeDrawer.vue'

const router = useRouter()
const route = useRoute()
const bidStore = useBidStore()

// 路由参数
const bidId = computed(() => route.params.id)

// 编辑状态
const bidTitle = ref('')
const activePanel = ref('outline')
const outline = ref([])
const content = ref('')
const currentChapterTitle = ref('')

// 操作状态
const saving = ref(false)
const submitting = ref(false)
const generating = ref(false)
const exporting = ref(false)
const exportFormat = ref('docx')
const exportDialogVisible = ref(false)
const knowledgeDrawerVisible = ref(false)

// ========== 生命周期 ==========

onMounted(async () => {
  if (bidId.value) {
    await loadBidDetail(String(bidId.value))
  }
})

// ========== 数据加载 ==========

const loadBidDetail = async (id) => {
  try {
    const res = await getBidDetail(id)
    bidTitle.value = res.data?.title || ''
    outline.value = res.data?.outline || []
    content.value = res.data?.content || ''
    bidStore.setDocument(res.data)
  } catch (error) {
    ElMessage.error('加载标书详情失败')
  }
}

// ========== 事件处理 ==========

const handleBack = () => {
  router.push('/bid')
}

const handleTitleChange = () => {
  // 标题变更处理
}

const handleGenerateOutline = async (params) => {
  generating.value = true
  try {
    // 转换前端字段到后端需要的格式
    const backendParams = {
      projectName: params.projectName,
      projectType: params.category === 'technical' ? '技术标' : params.category === 'commercial' ? '商务标' : '综合标',
      bidRequirements: params.requirements || '',
      scoringCriteria: '技术方案完整性',
      pageCount: 10
    }
    const res = await bidStore.generateOutlineAsync(backendParams)
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

const handleSelectChapter = (chapter) => {
  currentChapterTitle.value = chapter.title
  activePanel.value = 'content'
}

const handleUpdateContent = (newContent) => {
  content.value = newContent
}

const handleUpload = (file) => {
  console.log('上传文件:', file)
}

const handleInsertMaterial = (material) => {
  // 将素材插入到正文中
  const insertText = `\n[素材: ${material.name}]\n${material.content}\n[/素材]\n`
  content.value += insertText
}

const handleKnowledgeSearch = () => {
  knowledgeDrawerVisible.value = true
}

const handleKnowledgeSelect = (item) => {
  // 将选中的知识插入到正文中
  const insertText = `\n[参考资料: ${item.title}]\n${item.content}\n[/参考资料]\n`
  content.value += insertText
  knowledgeDrawerVisible.value = false
}

const handleSave = async () => {
  if (!bidTitle.value) {
    ElMessage.warning('请输入标书标题')
    return
  }
  saving.value = true
  try {
    const data = {
      title: bidTitle.value,
      outline: outline.value,
      content: content.value
    }
    if (bidId.value) {
      await updateBid(bidId.value, data)
    } else {
      const res = await createBid(data)
      // 跳转到新创建的标书
      router.replace(`/bid/${res.data.id}`)
    }
    ElMessage.success('保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const handleSubmit = async () => {
  try {
    await ElMessageBox.confirm('提交后将无法继续编辑，确定要提交吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await handleSave()
    submitting.value = true
    if (bidId.value) {
      await submitBid(bidId.value)
    }
    ElMessage.success('提交成功')
    router.push('/bid')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('提交失败')
    }
  } finally {
    submitting.value = false
  }
}

const handleExport = () => {
  exportDialogVisible.value = true
}

const confirmExport = async () => {
  if (!bidId.value) {
    ElMessage.warning('请先保存标书后再导出')
    exportDialogVisible.value = false
    return
  }
  exporting.value = true
  try {
    const blob = await exportBid(bidId.value, exportFormat.value)
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${bidTitle.value || '标书'}.${exportFormat.value}`
    link.click()
    URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
    exportDialogVisible.value = false
  } catch (error) {
    ElMessage.error('导出失败')
  } finally {
    exporting.value = false
  }
}
</script>

<style scoped>
.bid-editor-view {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 60px - 48px);
  background: var(--el-bg-color);
  border-radius: var(--card-radius);
  overflow: hidden;
}

.editor-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--el-spacing-md) var(--el-spacing-lg);
  border-bottom: 1px solid var(--el-border-color-lighter);
  background: var(--el-bg-color);
  gap: var(--el-spacing-lg);
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: var(--el-spacing-md);
}

.title-input {
  width: 300px;
}

.toolbar-center {
  flex: 1;
  display: flex;
  justify-content: center;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: var(--el-spacing-sm);
}

.editor-main {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.outline-panel {
  width: 280px;
  border-right: 1px solid var(--el-border-color-lighter);
  overflow-y: auto;
  background: var(--el-bg-color-page);
}

.content-panel {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.content-editor {
  flex: 1;
  padding: var(--el-spacing-lg);
}

.content-preview {
  flex: 1;
  padding: var(--el-spacing-lg);
  background: var(--el-bg-color-page);
}

.material-panel {
  width: 320px;
  border-left: 1px solid var(--el-border-color-lighter);
  overflow-y: auto;
  background: var(--el-bg-color-page);
  padding: var(--el-spacing-md);
}

.material-divider {
  margin: var(--el-spacing-md) 0;
}
</style>