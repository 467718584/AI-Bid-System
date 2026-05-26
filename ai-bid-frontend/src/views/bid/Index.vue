<template>
  <div class="bid-index">
    <div class="page-header">
      <h2>标书列表</h2>
      <el-button type="primary" @click="handleCreate">
        <el-icon><Plus /></el-icon>
        创建标书
      </el-button>
    </div>

    <div class="filter-bar">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索标书名称"
        style="width: 240px"
        clearable
        @clear="handleSearch"
        @keyup.enter="handleSearch"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <el-select v-model="statusFilter" placeholder="状态筛选" style="width: 140px" clearable @change="handleSearch">
        <el-option label="草稿" value="draft" />
        <el-option label="编制中" value="in_progress" />
        <el-option label="待审核" value="review" />
        <el-option label="已通过" value="approved" />
      </el-select>
    </div>

    <div class="bid-list">
      <el-row :gutter="16">
        <el-col v-for="item in bidList" :key="item.id" :xs="24" :sm="12" :md="8" :lg="6">
          <div class="bid-card" @click="handleEdit(item.id)">
            <div class="bid-card-header">
              <span :class="['status-tag', `status-${item.status}`]">
                {{ getStatusText(item.status) }}
              </span>
            </div>
            <h3 class="bid-title">{{ item.title }}</h3>
            <p class="bid-desc">{{ item.description || '暂无描述' }}</p>
            <div class="bid-card-footer">
              <span class="bid-date">更新时间：{{ formatDate(item.updatedAt) }}</span>
            </div>
          </div>
        </el-col>
      </el-row>

      <div v-if="!bidList.length" class="empty-state">
        <el-empty description="暂无标书" />
        <el-button type="primary" @click="handleCreate">创建第一个标书</el-button>
      </div>
    </div>

    <div v-if="total > 0" class="pagination-wrapper">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search, Plus } from '@element-plus/icons-vue'
import dayjs from 'dayjs'

const router = useRouter()
const searchKeyword = ref('')
const statusFilter = ref('')
const bidList = ref([])
const page = ref(1)
const pageSize = ref(12)
const total = ref(0)

const getStatusText = (status) => {
  const map = {
    draft: '草稿',
    in_progress: '编制中',
    review: '待审核',
    approved: '已通过',
    submitted: '已提交'
  }
  return map[status] || status
}

const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD')
}

const handleCreate = () => {
  router.push('/bid/create')
}

const handleEdit = (id) => {
  router.push(`/bid/${id}`)
}

const handleSearch = () => {
  page.value = 1
  // TODO: 调用API获取列表
}

const handlePageChange = () => {
  // TODO: 调用API获取列表
}

onMounted(() => {
  // TODO: 初始化加载数据
})
</script>

<style scoped>
.bid-index {
  min-height: 100%;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--el-spacing-lg);
}

.page-header h2 {
  font-size: var(--el-font-size-xxl);
  font-weight: 600;
  margin: 0;
}

.filter-bar {
  display: flex;
  gap: var(--el-spacing-md);
  margin-bottom: var(--el-spacing-lg);
}

.bid-list {
  min-height: 300px;
}

.bid-card {
  background: var(--el-bg-color);
  border-radius: var(--card-radius);
  padding: var(--card-padding);
  margin-bottom: 16px;
  cursor: pointer;
  transition: all var(--el-transition-fast-duration);
  box-shadow: var(--el-box-shadow-light);
}

.bid-card:hover {
  box-shadow: var(--el-box-shadow-base);
  transform: translateY(-2px);
}

.bid-card-header {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 12px;
}

.status-tag {
  padding: 2px 8px;
  border-radius: var(--el-border-radius-sm);
  font-size: var(--el-font-size-xs);
  color: #fff;
}

.status-draft { background: var(--bid-status-draft); }
.status-in_progress { background: var(--bid-status-in-progress); }
.status-review { background: var(--bid-status-review); }
.status-approved { background: var(--bid-status-approved); }
.status-submitted { background: var(--bid-status-submitted); }

.bid-title {
  font-size: var(--el-font-size-lg);
  font-weight: 500;
  margin: 0 0 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.bid-desc {
  font-size: var(--el-font-size-sm);
  color: var(--el-text-color-secondary);
  margin: 0;
  height: 40px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.bid-card-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--el-border-color-lighter);
}

.bid-date {
  font-size: var(--el-font-size-xs);
  color: var(--el-text-color-placeholder);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  gap: 16px;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: var(--el-spacing-lg);
}
</style>