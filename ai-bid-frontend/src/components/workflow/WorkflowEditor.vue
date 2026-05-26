<template>
  <div class="workflow-editor">
    <div class="editor-header">
      <div class="header-left">
        <el-input
          v-model="workflowName"
          placeholder="请输入工作流名称"
          class="name-input"
        />
        <el-tag :type="isSaved ? 'success' : 'warning'" size="small">
          {{ isSaved ? '已保存' : '未保存' }}
        </el-tag>
      </div>
      <div class="header-right">
        <el-button @click="handleSave" :loading="saving">
          <el-icon><DocumentChecked /></el-icon>
          保存
        </el-button>
        <el-button type="primary" @click="handleExecute">
          <el-icon><VideoPlay /></el-icon>
          执行工作流
        </el-button>
      </div>
    </div>

    <div class="editor-body">
      <!-- 左侧节点库 -->
      <div class="node-library">
        <div class="section-title">节点组件</div>
        <WorkflowNodes @drag-start="handleNodeDragStart" />
      </div>

      <!-- 中间画布 -->
      <div class="canvas-container">
        <WorkflowCanvas
          ref="canvasRef"
          :nodes="nodes"
          :connections="connections"
          @node-click="handleNodeClick"
          @node-drop="handleNodeDrop"
          @connection-create="handleConnectionCreate"
          @canvas-click="handleCanvasClick"
        />
      </div>

      <!-- 右侧属性面板 -->
      <div class="property-panel">
        <div v-if="selectedNode" class="node-properties">
          <div class="section-title">节点属性</div>

          <el-form label-position="top" size="small">
            <el-form-item label="节点名称">
              <el-input v-model="selectedNode.name" @change="handleNodeUpdate" />
            </el-form-item>

            <el-form-item label="节点类型">
              <el-tag>{{ getNodeTypeName(selectedNode.type) }}</el-tag>
            </el-form-item>

            <el-form-item label="描述">
              <el-input
                v-model="selectedNode.description"
                type="textarea"
                :rows="2"
                @change="handleNodeUpdate"
              />
            </el-form-item>

            <el-divider content-position="left">配置参数</el-divider>

            <!-- AI节点配置 -->
            <template v-if="selectedNode.type.startsWith('ai_')">
              <el-form-item label="模型选择">
                <el-select v-model="selectedNode.config.model" style="width: 100%">
                  <el-option label="GPT-4" value="gpt-4" />
                  <el-option label="GPT-3.5" value="gpt-3.5" />
                  <el-option label="Claude" value="claude" />
                </el-select>
              </el-form-item>

              <el-form-item label="温度参数">
                <el-slider
                  v-model="selectedNode.config.temperature"
                  :min="0"
                  :max="1"
                  :step="0.1"
                  show-input
                />
              </el-form-item>

              <el-form-item label="最大Token">
                <el-input-number
                  v-model="selectedNode.config.maxTokens"
                  :min="100"
                  :max="4000"
                  :step="100"
                  style="width: 100%"
                />
              </el-form-item>
            </template>

            <!-- 知识检索配置 -->
            <template v-else-if="selectedNode.type === 'knowledge_search'">
              <el-form-item label="检索数量">
                <el-input-number
                  v-model="selectedNode.config.topK"
                  :min="1"
                  :max="20"
                  style="width: 100%"
                />
              </el-form-item>

              <el-form-item label="相似度阈值">
                <el-slider
                  v-model="selectedNode.config.threshold"
                  :min="0"
                  :max="1"
                  :step="0.05"
                  show-input
                />
              </el-form-item>
            </template>

            <!-- 条件判断配置 -->
            <template v-else-if="selectedNode.type === 'condition'">
              <el-form-item label="条件表达式">
                <el-input
                  v-model="selectedNode.config.expression"
                  type="textarea"
                  :rows="3"
                  placeholder="例如: input.status === 'approved'"
                />
              </el-form-item>

              <el-form-item label="为真时分支">
                <el-input v-model="selectedNode.config.trueBranch" placeholder="分支名称" />
              </el-form-item>

              <el-form-item label="为假时分支">
                <el-input v-model="selectedNode.config.falseBranch" placeholder="分支名称" />
              </el-form-item>
            </template>

            <!-- 审批节点配置 -->
            <template v-else-if="selectedNode.type === 'approval'">
              <el-form-item label="审批人">
                <el-select v-model="selectedNode.config.approver" style="width: 100%">
                  <el-option label="指定用户" value="user" />
                  <el-option label="角色" value="role" />
                  <el-option label="任意" value="any" />
                </el-select>
              </el-form-item>

              <el-form-item label="超时时间(分钟)">
                <el-input-number
                  v-model="selectedNode.config.timeout"
                  :min="0"
                  :step="30"
                  style="width: 100%"
                />
              </el-form-item>
            </template>

            <!-- 延时节点配置 -->
            <template v-else-if="selectedNode.type === 'delay'">
              <el-form-item label="延时时间(秒)">
                <el-input-number
                  v-model="selectedNode.config.duration"
                  :min="1"
                  :max="3600"
                  style="width: 100%"
                />
              </el-form-item>
            </template>
          </el-form>

          <div class="node-actions">
            <el-button type="danger" @click="handleDeleteNode">
              <el-icon><Delete /></el-icon>
              删除节点
            </el-button>
          </div>
        </div>

        <div v-else class="empty-properties">
          <el-empty description="点击节点查看和编辑属性" :image-size="60" />
        </div>
      </div>
    </div>

    <!-- 执行日志 -->
    <el-drawer v-model="logDrawerVisible" title="执行日志" size="400px" direction="rtl">
      <div class="execution-log">
        <div v-for="(log, index) in executionLogs" :key="index" class="log-item">
          <el-tag :type="getLogType(log.level)" size="small">{{ log.level }}</el-tag>
          <span class="log-time">{{ log.time }}</span>
          <span class="log-message">{{ log.message }}</span>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { DocumentChecked, VideoPlay, Delete } from '@element-plus/icons-vue'
import WorkflowCanvas from './WorkflowCanvas.vue'
import WorkflowNodes from './WorkflowNodes.vue'

const props = defineProps({
  workflow: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['save', 'execute'])

const canvasRef = ref(null)

// 工作流状态
const workflowName = ref('')
const nodes = ref([])
const connections = ref([])
const selectedNode = ref(null)
const isSaved = ref(false)
const saving = ref(false)
const logDrawerVisible = ref(false)
const executionLogs = ref([])

// 节点类型名称映射
const nodeTypeNames = {
  start: '开始',
  end: '结束',
  ai_outline: 'AI目录生成',
  ai_content: 'AI内容生成',
  ai_polish: 'AI润色',
  knowledge_search: '知识检索',
  document_parse: '文档解析',
  condition: '条件判断',
  approval: '审批节点',
  delay: '延时节点',
  merge: '合并节点',
  export: '导出文档'
}

// ========== 方法 ==========

const getNodeTypeName = (type) => {
  return nodeTypeNames[type] || type
}

const handleNodeDragStart = (event, nodeType) => {
  // 开始拖拽
}

const handleNodeClick = (node) => {
  selectedNode.value = node
}

const handleNodeDrop = (newNode) => {
  nodes.value.push(newNode)
  selectedNode.value = newNode
  isSaved.value = false
}

const handleConnectionCreate = (connection) => {
  connections.value.push(connection)
  isSaved.value = false
}

const handleCanvasClick = () => {
  selectedNode.value = null
}

const handleNodeUpdate = () => {
  const index = nodes.value.findIndex(n => n.id === selectedNode.value.id)
  if (index !== -1) {
    nodes.value[index] = { ...selectedNode.value }
  }
  isSaved.value = false
}

const handleDeleteNode = () => {
  nodes.value = nodes.value.filter(n => n.id !== selectedNode.value.id)
  connections.value = connections.value.filter(
    c => c.sourceId !== selectedNode.value.id && c.targetId !== selectedNode.value.id
  )
  selectedNode.value = null
  isSaved.value = false
}

const handleSave = async () => {
  if (!workflowName.value) {
    ElMessage.warning('请输入工作流名称')
    return
  }
  saving.value = true
  try {
    emit('save', {
      name: workflowName.value,
      nodes: nodes.value,
      connections: connections.value
    })
    isSaved.value = true
    ElMessage.success('保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const handleExecute = async () => {
  if (nodes.value.length === 0) {
    ElMessage.warning('请添加节点后再执行')
    return
  }
  logDrawerVisible.value = true
  executionLogs.value = []
  emit('execute', {
    nodes: nodes.value,
    connections: connections.value
  })
}

const addLog = (level, message) => {
  executionLogs.value.push({
    level,
    message,
    time: new Date().toLocaleTimeString()
  })
}

const getLogType = (level) => {
  const map = {
    info: '',
    success: 'success',
    warning: 'warning',
    error: 'danger'
  }
  return map[level] || ''
}

// 暴露方法给父组件
defineExpose({
  addLog
})
</script>

<style scoped>
.workflow-editor {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.editor-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--el-spacing-md);
  background: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--el-spacing-md);
}

.name-input {
  width: 300px;
}

.header-right {
  display: flex;
  gap: var(--el-spacing-md);
}

.editor-body {
  display: flex;
  flex: 1;
  min-height: 0;
}

.node-library {
  width: 220px;
  background: var(--el-bg-color);
  border-right: 1px solid var(--el-border-color-lighter);
  padding: var(--el-spacing-md);
  overflow-y: auto;
}

.canvas-container {
  flex: 1;
  min-width: 0;
}

.property-panel {
  width: 320px;
  background: var(--el-bg-color);
  border-left: 1px solid var(--el-border-color-lighter);
  overflow-y: auto;
}

.section-title {
  font-weight: 600;
  margin-bottom: var(--el-spacing-md);
  padding-bottom: var(--el-spacing-sm);
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.node-properties {
  padding: var(--el-spacing-md);
}

.node-actions {
  margin-top: var(--el-spacing-lg);
  padding-top: var(--el-spacing-md);
  border-top: 1px solid var(--el-border-color-lighter);
}

.empty-properties {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: var(--el-spacing-lg);
}

.execution-log {
  display: flex;
  flex-direction: column;
  gap: var(--el-spacing-sm);
}

.log-item {
  display: flex;
  align-items: flex-start;
  gap: var(--el-spacing-sm);
  padding: var(--el-spacing-sm);
  background: var(--el-fill-color-light);
  border-radius: var(--el-border-radius-base);
}

.log-time {
  color: var(--el-text-color-secondary);
  font-size: var(--el-font-size-xs);
}

.log-message {
  flex: 1;
  font-size: var(--el-font-size-sm);
}
</style>