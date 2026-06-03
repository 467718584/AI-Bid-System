<template>
  <div class="outline-generator">
    <div class="panel-header">
      <span class="panel-title">目录结构</span>
      <el-button type="primary" size="small" :loading="loading" @click="handleGenerate">
        <el-icon><MagicStick /></el-icon>
        AI生成
      </el-button>
    </div>

    <div class="panel-content">
      <el-form label-position="top" class="generate-form">
        <el-form-item label="项目名称">
          <el-input v-model="form.projectName" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="招标文件要求">
          <el-select v-model="form.category" placeholder="请选择标书类型" style="width: 100%">
            <el-option label="技术标" value="technical" />
            <el-option label="商务标" value="commercial" />
            <el-option label="综合标" value="comprehensive" />
          </el-select>
        </el-form-item>
        <el-form-item label="资质要求">
          <el-input
            v-model="form.requirements"
            type="textarea"
            :rows="3"
            placeholder="请输入资质要求，多个用逗号分隔"
          />
        </el-form-item>
      </el-form>

      <el-divider content-position="left">目录章节</el-divider>

      <div v-if="outline.length === 0" class="empty-outline">
        <el-empty description="暂无目录" :image-size="60" />
      </div>

      <div v-else class="outline-tree">
        <el-tree
          :data="outlineData"
          node-key="id"
          :expand-on-click-node="false"
          :default-expand-all="true"
          draggable
          @node-drop="handleDrop"
        >
          <template #default="{ node, data }">
            <div class="tree-node">
              <el-input
                v-if="editingNodeId === data.id"
                v-model="editingTitle"
                size="small"
                class="node-title-input"
                @blur="confirmEditTitle(data.title)"
                @keyup.enter="confirmEditTitle(data.title)"
              />
              <template v-else>
                <span class="node-title">{{ data.title }}</span>
                <span v-if="data.pageCount" class="node-pages">({{ data.pageCount }}页)</span>
              </template>
              <div class="node-actions">
                <el-button
                  type="default"
                  link
                  size="small"
                  @click.stop="startEditTitle(data)"
                  title="编辑名称"
                >
                  <el-icon><EditPen /></el-icon>
                </el-button>
                <el-button
                <el-button
                  type="primary"
                  link
                  size="small"
                  @click.stop="handleGenerateContent(data)"
                >
                  生成内容
                </el-button>
                <el-button
                  type="danger"
                  link
                  size="small"
                  @click.stop="handleDeleteNode(data)"
                >
                  删除
                </el-button>
              </div>
            </div>
          </template>
        </el-tree>
      </div>

      <div class="add-chapter">
        <el-button type="dashed" style="width: 100%" @click="handleAddChapter">
          <el-icon><Plus /></el-icon>
          添加章节
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { MagicStick, Plus, EditPen } from '@element-plus/icons-vue'

const props = defineProps({
  outline: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['generate', 'update', 'generate-content'])

// 编辑状态
const editingNodeId = ref(null)
const editingTitle = ref('')
const titleInputRef = ref(null)

// 将outline数组转换为el-tree格式
const outlineData = computed(() => {
  const convert = (nodes) => {
    return nodes.map((node, index) => ({
      id: `node-${index}-${Date.now()}`,
      title: node.title,
      pageCount: node.pageCount,
      children: node.children ? convert(node.children) : []
    }))
  }
  return convert(props.outline)
})

// 开始编辑章节名称
const startEditTitle = (data) => {
  editingNodeId.value = data.id
  editingTitle.value = data.title
}

// 确认修改章节名称
const confirmEditTitle = (originalTitle) => {
  if (!editingTitle.value.trim()) {
    ElMessage.warning('章节名称不能为空')
    return
  }
  
  // 更新outline中的标题（通过原始标题匹配）
  const newOutline = props.outline.map(item => {
    if (item.title === originalTitle) {
      return { ...item, title: editingTitle.value }
    }
    // 也检查children
    if (item.children) {
      return {
        ...item,
        children: item.children.map(child => {
          if (child.title === originalTitle) {
            return { ...child, title: editingTitle.value }
          }
          return child
        })
      }
    }
    return item
  })
  
  emit('update', newOutline)
  editingNodeId.value = null
  ElMessage.success('章节名称已更新')
}

const form = reactive({
  projectName: '',
  category: 'technical',
  requirements: ''
})

const handleGenerate = () => {
  if (!form.projectName) {
    ElMessage.warning('请输入项目名称')
    return
  }
  emit('generate', {
    projectName: form.projectName,
    category: form.category,
    requirements: form.requirements
  })
}

// 生成章节内容 - 支持父章节批量生成所有子章节
const handleGenerateContent = async (data) => {
  // 如果有子章节，则逐个生成子章节内容
  if (data.children && data.children.length > 0) {
    ElMessage.info(`正在批量生成 "${data.title}" 的${data.children.length}个子章节，请等待...`)
    
    for (const child of data.children) {
      emit('generate-content', { 
        chapter: child.title, 
        pageCount: child.pageCount || 3,
        outline: props.outline 
      })
      // 等待足够时间让内容生成完成（每页至少2秒）
      const waitTime = Math.max(8000, (child.pageCount || 3) * 2000)
      await new Promise(resolve => setTimeout(resolve, waitTime))
    }
    
    ElMessage.success(`"${data.title}" 全部子章节生成完成`)
  } else {
    // 没有子章节，直接生成当前章节
    ElMessage.info(`正在生成 "${data.title}" 的内容...`)
    emit('generate-content', { 
      chapter: data.title, 
      pageCount: data.pageCount || 3,
      outline: props.outline 
    })
  }
}

const handleDeleteNode = async (data) => {
  try {
    await ElMessageBox.confirm(`确定要删除 "${data.title}" 章节吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    // TODO: 从outline中删除该节点
    ElMessage.success('删除成功')
  } catch {
    // 用户取消
  }
}

const handleDrop = (draggingNode, dropNode, dropType) => {
  // TODO: 处理拖拽排序
  console.log('拖拽:', draggingNode.data.title, dropType, dropNode.data.title)
}
</script>

<style scoped>
.outline-generator {
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

.generate-form {
  margin-bottom: var(--el-spacing-md);
}

.empty-outline {
  padding: var(--el-spacing-lg) 0;
}

.outline-tree {
  margin: var(--el-spacing-md) 0;
}

.tree-node {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding-right: 8px;
}

.node-title-input {
  width: 150px;
}

.node-title {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.node-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity var(--el-transition-fast-duration);
}

.tree-node:hover .node-actions {
  opacity: 1;
}

.add-chapter {
  margin-top: var(--el-spacing-md);
}
</style>