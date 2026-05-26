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
          :data="outline"
          node-key="id"
          :expand-on-click-node="false"
          :default-expand-all="true"
          draggable
          @node-drop="handleDrop"
        >
          <template #default="{ node, data }">
            <div class="tree-node">
              <span class="node-title">{{ data.title }}</span>
              <div class="node-actions">
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
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { MagicStick, Plus } from '@element-plus/icons-vue'

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

const emit = defineEmits(['generate', 'update'])

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

const handleAddChapter = () => {
  const newNode = {
    id: `node-${Date.now()}`,
    title: '新章节',
    children: []
  }
  const newOutline = [...props.outline, newNode]
  emit('update', newOutline)
}

const handleGenerateContent = (data) => {
  ElMessage.info(`正在生成 "${data.title}" 的内容...`)
  // TODO: 调用AI生成内容API
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