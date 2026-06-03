<template>
  <div class="project-index">
    <div class="page-header">
      <h2>项目管理</h2>
      <el-button type="primary" @click="handleCreate">
        <el-icon><Plus /></el-icon>
        新建项目
      </el-button>
    </div>

    <div class="filter-bar">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索项目名称"
        style="width: 240px"
        clearable
        @clear="loadProjects"
        @keyup.enter="loadProjects"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <el-select v-model="typeFilter" placeholder="项目类型" clearable style="width: 140px" @change="loadProjects">
        <el-option label="智慧城市" value="智慧城市" />
        <el-option label="水利" value="水利" />
        <el-option label="交通" value="交通" />
        <el-option label="政务" value="政务" />
      </el-select>
    </div>

    <div class="project-list">
      <el-table :data="projectList" v-loading="loading" stripe>
        <el-table-column prop="id" label="项目ID" width="120" />
        <el-table-column prop="name" label="项目名称" min-width="180" />
        <el-table-column prop="type" label="类型" width="100" />
        <el-table-column prop="amount" label="金额(万元)" width="120">
          <template #default="{ row }">
            {{ row.amount ? (row.amount / 10000).toFixed(2) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="创建时间" width="160" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="success" link size="small" @click="handleCreateBid(row)">生成标书</el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="total > 0" class="pagination-wrapper">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="loadProjects"
        />
      </div>
    </div>

    <!-- 创建/编辑项目对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="项目名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="项目类型" prop="type">
          <el-select v-model="form.type" placeholder="请选择项目类型" style="width: 100%">
            <el-option label="智慧城市" value="智慧城市" />
            <el-option label="水利" value="水利" />
            <el-option label="交通" value="交通" />
            <el-option label="政务" value="政务" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="金额(万元)" prop="amount">
          <el-input-number v-model="form.amount" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="招标人" prop="tenderer">
          <el-input v-model="form.tenderer" placeholder="请输入招标人" />
        </el-form-item>
        <el-form-item label="截止时间" prop="deadline">
          <el-date-picker v-model="form.deadline" type="datetime" placeholder="选择截止时间" style="width: 100%" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入项目描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmSave">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useProjectStore } from '@/stores/project'
import { ElMessage } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'

const router = useRouter()
const projectStore = useProjectStore()

const searchKeyword = ref('')
const typeFilter = ref('')
const projectList = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(12)
const total = ref(0)

const dialogVisible = ref(false)
const dialogTitle = ref('创建项目')
const formRef = ref(null)
const form = ref({
  name: '',
  type: '',
  amount: 0,
  tenderer: '',
  deadline: '',
  description: ''
})
const rules = {
  name: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择项目类型', trigger: 'change' }]
}

onMounted(() => {
  loadProjects()
})

const loadProjects = async () => {
  loading.value = true
  try {
    const res = await projectStore.fetchProjectList({
      page: page.value,
      pageSize: pageSize.value,
      keyword: searchKeyword.value,
      type: typeFilter.value
    })
    projectList.value = res.data?.list || []
    total.value = res.data?.total || 0
  } finally {
    loading.value = false
  }
}

const handleCreate = () => {
  dialogTitle.value = '创建项目'
  form.value = { name: '', type: '', amount: 0, tenderer: '', deadline: '', description: '' }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogTitle.value = '编辑项目'
  form.value = { ...row }
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await projectStore.remove(row.id)
    ElMessage.success('删除成功')
    await loadProjects()
  } catch {
    ElMessage.error('删除失败')
  }
}

const handleCreateBid = (row) => {
  router.push({ path: '/bid/create', query: { projectId: row.id } })
}

const confirmSave = async () => {
  try {
    await formRef.value.validate()
    if (form.value.id) {
      await projectStore.update(form.value.id, form.value)
      ElMessage.success('更新成功')
    } else {
      await projectStore.create(form.value)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    await loadProjects()
  } catch {
    // 表单验证失败
  }
}

const getStatusType = (status) => {
  const map = { DRAFT: 'info', IN_PROGRESS: 'primary', COMPLETED: 'success', CANCELLED: 'danger' }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = { DRAFT: '草稿', IN_PROGRESS: '进行中', COMPLETED: '已完成', CANCELLED: '已取消' }
  return map[status] || status
}
</script>

<style scoped>
.project-index {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.project-list {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
