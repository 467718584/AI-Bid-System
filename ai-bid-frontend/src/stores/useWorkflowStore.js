import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  getWorkflowList,
  getWorkflowDetail,
  getWorkflowNodes,
  getWorkflowInstances,
  getWorkflowInstanceStatus,
  getWorkflowStats
} from '@/api/workflow'

export const useWorkflowStore = defineStore('workflow', () => {
  // 工作流列表
  const workflowList = ref([])
  const workflowTotal = ref(0)

  // 当前工作流
  const currentWorkflow = ref(null)
  const currentNodes = ref([])

  // 工作流实例
  const workflowInstances = ref([])
  const instanceTotal = ref(0)
  const currentInstance = ref(null)
  const instanceStatus = ref(null)

  // 统计数据
  const workflowStats = ref(null)

  // 加载状态
  const loading = ref(false)
  const executing = ref(false)

  // ========== 工作流列表 ==========

  const fetchWorkflowList = async (params) => {
    loading.value = true
    try {
      const res = await getWorkflowList(params)
      workflowList.value = res.data?.list || []
      workflowTotal.value = res.data?.total || 0
      return res
    } finally {
      loading.value = false
    }
  }

  const fetchWorkflowDetail = async (id) => {
    loading.value = true
    try {
      const res = await getWorkflowDetail(id)
      currentWorkflow.value = res.data
      return res
    } finally {
      loading.value = false
    }
  }

  // ========== 工作流节点 ==========

  const fetchWorkflowNodes = async (workflowId) => {
    loading.value = true
    try {
      const res = await getWorkflowNodes(workflowId)
      currentNodes.value = res.data || []
      return res
    } finally {
      loading.value = false
    }
  }

  const setCurrentNodes = (nodes) => {
    currentNodes.value = nodes
  }

  const addNode = (node) => {
    currentNodes.value.push(node)
  }

  const updateNode = (nodeId, data) => {
    const index = currentNodes.value.findIndex(n => n.id === nodeId)
    if (index !== -1) {
      currentNodes.value[index] = { ...currentNodes.value[index], ...data }
    }
  }

  const removeNode = (nodeId) => {
    currentNodes.value = currentNodes.value.filter(n => n.id !== nodeId)
  }

  const reorderNodes = (newOrder) => {
    currentNodes.value = newOrder
  }

  // ========== 工作流实例 ==========

  const fetchWorkflowInstances = async (params) => {
    loading.value = true
    try {
      const res = await getWorkflowInstances(params)
      workflowInstances.value = res.data?.list || []
      instanceTotal.value = res.data?.total || 0
      return res
    } finally {
      loading.value = false
    }
  }

  const fetchInstanceStatus = async (instanceId) => {
    executing.value = true
    try {
      const res = await getWorkflowInstanceStatus(instanceId)
      instanceStatus.value = res.data
      return res
    } finally {
      executing.value = false
    }
  }

  const setCurrentInstance = (instance) => {
    currentInstance.value = instance
  }

  // ========== 统计 ==========

  const fetchWorkflowStats = async () => {
    loading.value = true
    try {
      const res = await getWorkflowStats()
      workflowStats.value = res.data
      return res
    } finally {
      loading.value = false
    }
  }

  // ========== 状态管理 ==========

  const setLoading = (val) => {
    loading.value = val
  }

  const setExecuting = (val) => {
    executing.value = val
  }

  const clearWorkflow = () => {
    currentWorkflow.value = null
    currentNodes.value = []
    currentInstance.value = null
    instanceStatus.value = null
  }

  return {
    // 状态
    workflowList,
    workflowTotal,
    currentWorkflow,
    currentNodes,
    workflowInstances,
    instanceTotal,
    currentInstance,
    instanceStatus,
    workflowStats,
    loading,
    executing,
    // 方法
    fetchWorkflowList,
    fetchWorkflowDetail,
    fetchWorkflowNodes,
    setCurrentNodes,
    addNode,
    updateNode,
    removeNode,
    reorderNodes,
    fetchWorkflowInstances,
    fetchInstanceStatus,
    setCurrentInstance,
    fetchWorkflowStats,
    setLoading,
    setExecuting,
    clearWorkflow
  }
})