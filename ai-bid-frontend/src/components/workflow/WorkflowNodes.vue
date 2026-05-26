<template>
  <div class="workflow-nodes">
    <div
      v-for="nodeType in availableNodes"
      :key="nodeType.type"
      class="node-item"
      :class="{ 'node-disabled': nodeType.disabled }"
      draggable
      @dragstart="handleDragStart($event, nodeType)"
    >
      <div class="node-header">
        <el-icon class="node-icon" :style="{ color: nodeType.color }">
          <component :is="nodeType.icon" />
        </el-icon>
        <span class="node-name">{{ nodeType.name }}</span>
      </div>
      <div class="node-description">{{ nodeType.description }}</div>
      <div class="node-tags">
        <el-tag v-for="tag in nodeType.tags" :key="tag" size="small" type="info">
          {{ tag }}
        </el-tag>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  // 可选：限制可用的节点类型
  availableTypes: {
    type: Array,
    default: null
  },
  // 可选：排除的节点类型
  excludeTypes: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['drag-start'])

// 所有可用的节点类型
const allNodes = [
  {
    type: 'start',
    name: '开始',
    icon: 'VideoPlay',
    color: '#67c23a',
    description: '工作流入口节点',
    tags: ['系统', '入口'],
    disabled: false
  },
  {
    type: 'end',
    name: '结束',
    icon: 'CircleCheck',
    color: '#f56c6c',
    description: '工作流结束节点',
    tags: ['系统', '出口'],
    disabled: false
  },
  {
    type: 'ai_outline',
    name: 'AI目录生成',
    icon: 'Operation',
    color: '#409eff',
    description: '使用AI生成标书目录结构',
    tags: ['AI', '标书'],
    disabled: false
  },
  {
    type: 'ai_content',
    name: 'AI内容生成',
    icon: 'Document',
    color: '#409eff',
    description: '使用AI生成标书正文内容',
    tags: ['AI', '标书'],
    disabled: false
  },
  {
    type: 'ai_polish',
    name: 'AI润色',
    icon: 'Edit',
    color: '#409eff',
    description: '对标书内容进行智能润色',
    tags: ['AI', '标书'],
    disabled: false
  },
  {
    type: 'knowledge_search',
    name: '知识检索',
    icon: 'Search',
    color: '#e6a23c',
    description: '从知识库检索相关内容',
    tags: ['知识库', '检索'],
    disabled: false
  },
  {
    type: 'document_parse',
    name: '文档解析',
    icon: 'FolderOpened',
    color: '#909399',
    description: '解析上传的招标文件',
    tags: ['文档', '解析'],
    disabled: false
  },
  {
    type: 'condition',
    name: '条件判断',
    icon: 'Connection',
    color: '#f56c6c',
    description: '根据条件选择执行分支',
    tags: ['逻辑', '分支'],
    disabled: false
  },
  {
    type: 'approval',
    name: '审批节点',
    icon: 'User',
    color: '#9c27b0',
    description: '人工审批确认环节',
    tags: ['人工', '审批'],
    disabled: false
  },
  {
    type: 'delay',
    name: '延时节点',
    icon: 'Timer',
    color: '#909399',
    description: '延时等待一段时间',
    tags: ['时间', '延时'],
    disabled: false
  },
  {
    type: 'merge',
    name: '合并节点',
    icon: 'Connection',
    color: '#607d8b',
    description: '合并多个执行分支',
    tags: ['逻辑', '合并'],
    disabled: false
  },
  {
    type: 'export',
    name: '导出文档',
    icon: 'Download',
    color: '#4caf50',
    description: '导出生成好的标书文档',
    tags: ['导出', '文档'],
    disabled: false
  }
]

const availableNodes = computed(() => {
  let nodes = allNodes

  if (props.availableTypes) {
    nodes = nodes.filter(n => props.availableTypes.includes(n.type))
  }

  if (props.excludeTypes.length > 0) {
    nodes = nodes.filter(n => !props.excludeTypes.includes(n.type))
  }

  return nodes
})

const handleDragStart = (event, nodeType) => {
  event.dataTransfer.setData('nodeType', JSON.stringify(nodeType))
  emit('drag-start', event, nodeType)
}
</script>

<style scoped>
.workflow-nodes {
  display: flex;
  flex-direction: column;
  gap: var(--el-spacing-sm);
}

.node-item {
  padding: var(--el-spacing-sm) var(--el-spacing-md);
  background: var(--el-fill-color-light);
  border: 1px solid var(--el-border-color-lighter);
  border-radius: var(--el-border-radius-base);
  cursor: move;
  transition: all var(--el-transition-fast-duration);
}

.node-item:hover:not(.node-disabled) {
  background: var(--el-fill-color);
  border-color: var(--el-border-color);
}

.node-item.node-disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.node-header {
  display: flex;
  align-items: center;
  gap: var(--el-spacing-sm);
  margin-bottom: 4px;
}

.node-icon {
  font-size: 16px;
}

.node-name {
  font-size: var(--el-font-size-sm);
  font-weight: 500;
}

.node-description {
  font-size: var(--el-font-size-xs);
  color: var(--el-text-color-secondary);
  margin-bottom: 4px;
}

.node-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
</style>