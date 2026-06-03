<template>
  <div class="workflow-view">
    <!-- 顶部工具栏 -->
    <div class="workflow-toolbar">
      <div class="toolbar-left">
        <el-button type="primary" @click="handleCreateWorkflow">
          <el-icon><Plus /></el-icon>
          新建工作流
        </el-button>
        <el-select v-model="currentWorkflowId" placeholder="选择工作流" clearable style="width: 200px">
          <el-option
            v-for="item in workflowList"
            :key="item.id"
            :label="item.name"
            :value="item.id"
          />
        </el-select>
      </div>
      <div class="toolbar-right">
        <el-button @click="handleLoadTemplate">
          <el-icon><DocumentCopy /></el-icon>
          从模板创建
        </el-button>
        <el-button @click="handleRefresh">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <!-- 工作流主体 -->
    <div class="workflow-content">
      <!-- 左侧节点面板 -->
      <div class="node-panel">
        <div class="panel-header">
          <span>节点组件</span>
        </div>
        <div class="node-list">
          <div
            v-for="nodeType in nodeTypes"
            :key="nodeType.type"
            class="node-item"
            draggable
            @dragstart="handleNodeDragStart($event, nodeType)"
          >
            <el-icon><component :is="nodeType.icon" /></el-icon>
            <span>{{ nodeType.name }}</span>
          </div>
        </div>
      </div>

      <!-- 中间画布 -->
      <div class="workflow-canvas">
        <WorkflowCanvas
          ref="canvasRef"
          :nodes="nodes"
          :connections="connections"
          @node-click="handleNodeClick"
          @node-drop="handleNodeDrop"
          @connection-create="handleConnectionCreate"
          @connection-delete="handleConnectionDelete"
          @canvas-click="handleCanvasClick"
        />
      </div>

      <!-- 右侧属性面板 -->
      <div class="property-panel">
        <div v-if="selectedNode" class="node-property">
          <div class="panel-header">
            <span>节点属性</span>
            <el-button type="danger" link size="small" @click="handleDeleteNode">
              删除
            </el-button>
          </div>
          <el-form label-position="top" size="small">
            <el-form-item label="节点名称">
              <el-input v-model="selectedNode.name" @blur="handleNodeUpdate" />
            </el-form-item>
            <el-form-item label="节点类型">
              <el-tag>{{ selectedNode.type }}</el-tag>
            </el-form-item>
            <el-form-item label="描述">
              <el-input
                v-model="selectedNode.description"
                type="textarea"
                :rows="3"
                @blur="handleNodeUpdate"
              />
            </el-form-item>
            <el-form-item label="配置参数">
              <el-input
                v-model="nodeConfigJson"
                type="textarea"
                :rows="5"
                placeholder="JSON格式"
                @blur="handleNodeConfigUpdate"
              />
            </el-form-item>
          </el-form>
        </div>
        <div v-else-if="!currentWorkflowId" class="empty-hint">
          <el-empty description="请选择或创建工作流" :image-size="80" />
        </div>
        <div v-else class="empty-hint">
          <el-empty description="点击节点查看属性" :image-size="80" />
        </div>
      </div>
    </div>

    <!-- 底部实例列表 -->
    <div class="instance-panel">
      <div class="panel-header">
        <span>执行实例</span>
        <el-button type="primary" size="small" @click="handleStartInstance">
          <el-icon><VideoPlay /></el-icon>
          启动执行
        </el-button>
      </div>
      <el-table :data="instances" size="small" max-height="200">
        <el-table-column prop="id" label="实例ID" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ row.statusText }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="startTime" label="开始时间" width="160" />
        <el-table-column prop="endTime" label="结束时间" width="160" />
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleViewInstance(row)">
              查看
            </el-button>
            <el-button
              v-if="row.status === 'failed'"
              type="warning"
              link
              size="small"
              @click="handleRetryInstance(row)"
            >
              重试
            </el-button>
            <el-button
              v-if="row.status === 'running'"
              type="danger"
              link
              size="small"
              @click="handleCancelInstance(row)"
            >
              取消
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 创建工作流对话框 -->
    <el-dialog v-model="createDialogVisible" title="创建工作流" width="500px">
      <el-form ref="createFormRef" :model="createForm" :rules="createRules" label-width="100px">
        <el-form-item label="工作流名称" prop="name">
          <el-input v-model="createForm.name" placeholder="请输入工作流名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="createForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入工作流描述"
          />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="createForm.category" placeholder="请选择分类" style="width: 100%">
            <el-option label="标书生成" value="bid" />
            <el-option label="知识管理" value="knowledge" />
            <el-option label="文档处理" value="document" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmCreateWorkflow">确认创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useWorkflowStore } from '@/stores/useWorkflowStore'
import { ElMessage } from 'element-plus'
import {
  Plus,
  DocumentCopy,
  Refresh,
  VideoPlay,
  Operation,
  Document,
  Connection,
  Timer,
  User
} from '@element-plus/icons-vue'
import WorkflowCanvas from '@/components/workflow/WorkflowCanvas.vue'
import {
  createWorkflow,
  getWorkflowNodes,
  startWorkflowInstance,
  getWorkflowInstances,
  cancelWorkflowInstance,
  retryWorkflowNode
} from '@/api/workflow'

const workflowStore = useWorkflowStore()

// 状态
const canvasRef = ref(null)
const currentWorkflowId = ref(null)
const nodes = ref([])
const connections = ref([])
const selectedNode = ref(null)
const nodeConfigJson = ref('')

// 节点类型
const nodeTypes = ref([
  { type: 'start', name: '开始', icon: 'VideoPlay' },
  { type: 'end', name: '结束', icon: 'CircleCheck' },
  { type: 'ai_outline', name: 'AI目录生成', icon: 'Operation' },
  { type: 'ai_content', name: 'AI内容生成', icon: 'Document' },
  { type: 'knowledge_search', name: '知识检索', icon: 'Search' },
  { type: 'document_parse', name: '文档解析', icon: 'FolderOpened' },
  { type: 'condition', name: '条件判断', icon: 'Connection' },
  { type: 'approval', name: '审批节点', icon: 'User' },
  { type: 'delay', name: '延时节点', icon: 'Timer' }
])

// 实例列表
const instances = ref([])

// 创建工作流
const createDialogVisible = ref(false)
const createFormRef = ref(null)
const createForm = ref({
  name: '',
  description: '',
  category: 'bid'
})
const createRules = {
  name: [{ required: true, message: '请输入工作流名称', trigger: 'blur' }]
}

// ========== 生命周期 ==========

onMounted(async () => {
  await workflowStore.fetchWorkflowList()
})

// ========== 监听 ==========

watch(currentWorkflowId, async (newId) => {
  if (newId) {
    await loadWorkflowDetail(newId)
  }
})

// ========== 方法 ==========

const handleCreateWorkflow = () => {
  createForm.value = { name: '', description: '', category: 'bid' }
  createDialogVisible.value = true
}

const confirmCreateWorkflow = async () => {
  try {
    await createFormRef.value.validate()
    const res = await createWorkflow(createForm.value)
    ElMessage.success('创建成功')
    createDialogVisible.value = false
    // 从响应中获取新创建的工作流ID
    // API返回格式: { code: 200, data: { list: [...], total: N } }
    const newWorkflow = res.data?.list?.find(w => w.name === createForm.value.name)
    if (newWorkflow?.id) {
      currentWorkflowId.value = newWorkflow.id
    }
    await workflowStore.fetchWorkflowList()
  } catch (error) {
    // 表单验证失败
  }
}

const handleLoadTemplate = () => {
  ElMessage.info('从模板创建功能开发中')
}

const handleRefresh = async () => {
  await workflowStore.fetchWorkflowList()
  if (currentWorkflowId.value) {
    await loadWorkflowDetail(currentWorkflowId.value)
  }
}

const loadWorkflowDetail = async (workflowId) => {
  try {
    await workflowStore.fetchWorkflowDetail(workflowId)
    await workflowStore.fetchWorkflowNodes(workflowId)
    nodes.value = workflowStore.currentNodes
    // 加载实例列表
    const instanceRes = await getWorkflowInstances({ workflowId })
    instances.value = instanceRes.data?.list || []
  } catch (error) {
    ElMessage.error('加载工作流详情失败')
  }
}

const handleNodeDragStart = (event, nodeType) => {
  event.dataTransfer.setData('nodeType', JSON.stringify(nodeType))
}

const handleNodeClick = (node) => {
  selectedNode.value = node
  nodeConfigJson.value = JSON.stringify(node.config || {}, null, 2)
}

const handleNodeDrop = (data) => {
  nodes.value.push(data)
}

const handleConnectionCreate = (connection) => {
  connections.value.push(connection)
}

const handleConnectionDelete = (connectionId) => {
  connections.value = connections.value.filter(c => c.id !== connectionId)
}

const handleCanvasClick = () => {
  selectedNode.value = null
}

const handleNodeUpdate = () => {
  const index = nodes.value.findIndex(n => n.id === selectedNode.value.id)
  if (index !== -1) {
    nodes.value[index] = { ...selectedNode.value }
  }
}

const handleNodeConfigUpdate = () => {
  try {
    const config = JSON.parse(nodeConfigJson.value)
    selectedNode.value.config = config
    handleNodeUpdate()
  } catch {
    ElMessage.error('JSON格式错误')
  }
}

const handleDeleteNode = async () => {
  nodes.value = nodes.value.filter(n => n.id !== selectedNode.value.id)
  selectedNode.value = null
}

const handleStartInstance = async () => {
  if (!currentWorkflowId.value) {
    ElMessage.warning('请选择工作流')
    return
  }
  try {
    const res = await startWorkflowInstance(currentWorkflowId.value, {
      nodes: nodes.value,
      connections: connections.value
    })
    ElMessage.success('启动成功')
    await handleRefresh()
  } catch (error) {
    ElMessage.error('启动失败')
  }
}

const handleViewInstance = (instance) => {
  // 跳转到实例详情页
  console.log('查看实例:', instance)
}

const handleRetryInstance = async (instance) => {
  try {
    await retryWorkflowNode(instance.id, instance.failedNodeId)
    ElMessage.success('重试成功')
    await handleRefresh()
  } catch (error) {
    ElMessage.error('重试失败')
  }
}

const handleCancelInstance = async (instance) => {
  try {
    await cancelWorkflowInstance(instance.id)
    ElMessage.success('取消成功')
    await handleRefresh()
  } catch (error) {
    ElMessage.error('取消失败')
  }
}

const getStatusType = (status) => {
  const map = {
    pending: 'info',
    running: 'primary',
    completed: 'success',
    failed: 'danger',
    cancelled: 'warning'
  }
  return map[status] || 'info'
}
</script>

<style scoped>
.workflow-view {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 60px - 48px);
  gap: var(--el-spacing-md);
}

.workflow-toolbar {
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

.workflow-content {
  display: flex;
  flex: 1;
  min-height: 0;
  gap: var(--el-spacing-md);
}

.node-panel {
  width: 200px;
  background: var(--el-bg-color);
  border-radius: var(--card-radius);
  overflow: hidden;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--el-spacing-md);
  border-bottom: 1px solid var(--el-border-color-lighter);
  font-weight: 500;
}

.node-list {
  padding: var(--el-spacing-md);
  display: flex;
  flex-direction: column;
  gap: var(--el-spacing-sm);
}

.node-item {
  display: flex;
  align-items: center;
  gap: var(--el-spacing-sm);
  padding: var(--el-spacing-sm) var(--el-spacing-md);
  background: var(--el-fill-color-light);
  border-radius: var(--el-border-radius-base);
  cursor: move;
  transition: all var(--el-transition-fast-duration);
}

.node-item:hover {
  background: var(--el-fill-color);
}

.workflow-canvas {
  flex: 1;
  background: var(--el-bg-color);
  border-radius: var(--card-radius);
  overflow: hidden;
}

.property-panel {
  width: 300px;
  background: var(--el-bg-color);
  border-radius: var(--card-radius);
  overflow: hidden;
}

.node-property {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.empty-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: var(--el-spacing-lg);
}

.instance-panel {
  background: var(--el-bg-color);
  border-radius: var(--card-radius);
  overflow: hidden;
}
</style>