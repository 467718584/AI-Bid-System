<template>
  <div
    ref="canvasRef"
    class="workflow-canvas"
    @click="handleCanvasClick"
    @dragover.prevent="handleDragOver"
    @drop="handleDrop"
  >
    <!-- 网格背景 -->
    <svg class="canvas-grid" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
          <circle cx="1" cy="1" r="1" fill="#ddd" />
        </pattern>
      </defs>
      <rect width="100%" height="100%" fill="url(#grid)" />
    </svg>

    <!-- 连接线 -->
    <svg class="canvas-connections" xmlns="http://www.w3.org/2000/svg">
      <g v-for="conn in connections" :key="conn.id">
        <path
          :d="getConnectionPath(conn)"
          fill="none"
          stroke="#409eff"
          stroke-width="2"
          marker-end="url(#arrowhead)"
          :class="{ 'connection-selected': selectedConnectionId === conn.id }"
          @click.stop="handleConnectionClick(conn)"
        />
      </g>
      <defs>
        <marker
          id="arrowhead"
          markerWidth="10"
          markerHeight="10"
          refX="9"
          refY="5"
          orient="auto"
        >
          <polygon points="0 0, 10 5, 0 10" fill="#409eff" />
        </marker>
      </defs>
    </svg>

    <!-- 节点 -->
    <div
      v-for="node in nodes"
      :key="node.id"
      class="canvas-node"
      :class="{
        'node-selected': selectedNodeId === node.id,
        'node-running': node.status === 'running',
        'node-completed': node.status === 'completed',
        'node-failed': node.status === 'failed'
      }"
      :style="{ left: node.x + 'px', top: node.y + 'px' }"
      @mousedown="handleNodeMouseDown($event, node)"
      @click.stop="handleNodeClick(node)"
    >
      <div class="node-icon">
        <el-icon><component :is="getNodeIcon(node.type)" /></el-icon>
      </div>
      <div class="node-label">{{ node.name }}</div>
      <div v-if="node.status" class="node-status">
        <el-tag :type="getNodeStatusType(node.status)" size="small">
          {{ getNodeStatusText(node.status) }}
        </el-tag>
      </div>
    </div>

    <!-- 拖拽预览 -->
    <div
      v-if="dragPreview"
      class="drag-preview"
      :style="{ left: dragPreview.x + 'px', top: dragPreview.y + 'px' }"
    >
      <el-icon><component :is="getNodeIcon(dragPreview.type)" /></el-icon>
      <span>{{ dragPreview.name }}</span>
    </div>

    <!-- 空状态提示 -->
    <div v-if="nodes.length === 0" class="empty-canvas">
      <el-empty description="拖拽节点组件到此处构建工作流" :image-size="100" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { VideoPlay, CircleCheck, Document, Operation, Search, FolderOpened } from '@element-plus/icons-vue'

const props = defineProps({
  nodes: {
    type: Array,
    default: () => []
  },
  connections: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['node-click', 'node-drop', 'connection-create', 'connection-delete', 'canvas-click'])

const canvasRef = ref(null)
const selectedNodeId = ref(null)
const selectedConnectionId = ref(null)
const draggingNode = ref(null)
const dragOffset = ref({ x: 0, y: 0 })
const dragPreview = ref(null)

// ========== 节点图标映射 ==========

const getNodeIcon = (type) => {
  const iconMap = {
    start: 'VideoPlay',
    end: 'CircleCheck',
    ai_outline: 'Operation',
    ai_content: 'Document',
    knowledge_search: 'Search',
    document_parse: 'FolderOpened',
    condition: 'Connection',
    approval: 'User',
    delay: 'Timer'
  }
  return iconMap[type] || 'Document'
}

// ========== 节点状态 ==========

const getNodeStatusType = (status) => {
  const map = {
    pending: 'info',
    running: 'primary',
    completed: 'success',
    failed: 'danger',
    skipped: 'warning'
  }
  return map[status] || 'info'
}

const getNodeStatusText = (status) => {
  const map = {
    pending: '待执行',
    running: '执行中',
    completed: '已完成',
    failed: '失败',
    skipped: '跳过'
  }
  return map[status] || status
}

// ========== 连接线路径 ==========

const getConnectionPath = (conn) => {
  const sourceNode = props.nodes.find(n => n.id === conn.sourceId)
  const targetNode = props.nodes.find(n => n.id === conn.targetId)
  if (!sourceNode || !targetNode) return ''

  const sourceX = sourceNode.x + 80
  const sourceY = sourceNode.y + 30
  const targetX = targetNode.x
  const targetY = targetNode.y + 30

  const midX = (sourceX + targetX) / 2

  return `M ${sourceX} ${sourceY} C ${midX} ${sourceY}, ${midX} ${targetY}, ${targetX} ${targetY}`
}

// ========== 事件处理 ==========

const handleCanvasClick = () => {
  selectedNodeId.value = null
  selectedConnectionId.value = null
  emit('canvas-click')
}

const handleNodeClick = (node) => {
  selectedNodeId.value = node.id
  emit('node-click', node)
}

const handleNodeMouseDown = (event, node) => {
  if (event.button !== 0) return

  draggingNode.value = node
  selectedNodeId.value = node.id

  const rect = canvasRef.value.getBoundingClientRect()
  dragOffset.value = {
    x: event.clientX - rect.left - node.x,
    y: event.clientY - rect.top - node.y
  }

  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}

const handleMouseMove = (event) => {
  if (!draggingNode.value) return

  const rect = canvasRef.value.getBoundingClientRect()
  const newX = event.clientX - rect.left - dragOffset.value.x
  const newY = event.clientY - rect.top - dragOffset.value.y

  // 更新节点位置
  const node = props.nodes.find(n => n.id === draggingNode.value.id)
  if (node) {
    node.x = Math.max(0, newX)
    node.y = Math.max(0, newY)
  }
}

const handleMouseUp = () => {
  draggingNode.value = null
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
}

const handleDragOver = (event) => {
  const rect = canvasRef.value.getBoundingClientRect()
  dragPreview.value = {
    x: event.clientX - rect.left,
    y: event.clientY - rect.top
  }
}

const handleDrop = (event) => {
  event.preventDefault()
  const nodeTypeData = event.dataTransfer.getData('nodeType')
  if (!nodeTypeData) return

  const nodeType = JSON.parse(nodeTypeData)
  const rect = canvasRef.value.getBoundingClientRect()
  const x = event.clientX - rect.left - 40
  const y = event.clientY - rect.top - 30

  const newNode = {
    id: `node-${Date.now()}`,
    type: nodeType.type,
    name: nodeType.name,
    x: Math.max(0, x),
    y: Math.max(0, y),
    config: {},
    status: 'pending'
  }

  emit('node-drop', newNode)
  dragPreview.value = null
  ElMessage.success(`已添加节点: ${nodeType.name}`)
}

const handleConnectionClick = (conn) => {
  selectedConnectionId.value = conn.id
}
</script>

<style scoped>
.workflow-canvas {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  background: var(--el-fill-color-light);
}

.canvas-grid,
.canvas-connections {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.canvas-connections path {
  pointer-events: stroke;
  cursor: pointer;
}

.canvas-connections path:hover {
  stroke-width: 3;
}

.connection-selected {
  stroke: #f56c6c !important;
  stroke-width: 3;
}

.canvas-node {
  position: absolute;
  width: 80px;
  padding: 8px;
  background: var(--el-bg-color);
  border: 2px solid var(--el-border-color);
  border-radius: 8px;
  cursor: move;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  transition: box-shadow var(--el-transition-fast-duration);
  user-select: none;
}

.canvas-node:hover {
  box-shadow: var(--el-box-shadow);
}

.node-selected {
  border-color: var(--el-color-primary);
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.node-running {
  border-color: var(--el-color-primary);
  animation: pulse 2s infinite;
}

.node-completed {
  border-color: var(--el-color-success);
}

.node-failed {
  border-color: var(--el-color-danger);
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(64, 158, 255, 0.4);
  }
  50% {
    box-shadow: 0 0 0 8px rgba(64, 158, 255, 0);
  }
}

.node-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--el-fill-color);
  border-radius: 50%;
  font-size: 16px;
  color: var(--el-color-primary);
}

.node-label {
  font-size: 12px;
  text-align: center;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 70px;
}

.node-status {
  position: absolute;
  top: -20px;
  left: 50%;
  transform: translateX(-50%);
}

.drag-preview {
  position: absolute;
  width: 80px;
  padding: 8px;
  background: rgba(64, 158, 255, 0.1);
  border: 2px dashed var(--el-color-primary);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  pointer-events: none;
  z-index: 100;
}

.empty-canvas {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  pointer-events: none;
}
</style>