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
              <span :class="['status-tag', 'status-' + item.status]">
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

      <div v-if="!bidList.length && !loading" class="empty-state">
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
import { getBidList, createBid } from '@/api/bid'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

const router = useRouter()
const searchKeyword = ref('')
const statusFilter = ref('')
const bidList = ref([])
const page = ref(1)
const pageSize = ref(12)
const total = ref(0)
const loading = ref(false)

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

const loadBidList = async () => {
  loading.value = true
  try {
    const res = await getBidList({ page: page.value, pageSize: pageSize.value })
    bidList.value = res.data?.list || []
    total.value = res.data?.total || 0
  } catch (error) {
    console.error('加载标书列表失败:', error)
    ElMessage.error('加载标书列表失败')
  } finally {
    loading.value = false
  }
}

const handleCreate = async () => {
  try {
    const res = await createBid({
      title: '未命名标书',
      description: '',
      status: 'draft'
    })
    if (res.code === 200 && res.data) {
      // 优先使用直接返回的ID，否则从列表中获取最新创建的
      const newBid = res.data.id ? res.data : (res.data.list ? res.data.list[res.data.list.length - 1] : null)
      if (newBid && newBid.id) {
        router.push(`/bid/${newBid.id}`)
      } else {
        loadBidList()
      }
    }
  } catch (error) {
    console.error('创建标书失败:', error)
    ElMessage.error('创建标书失败')
  }
}

const handleEdit = (id) => {
  router.push(`/bid/${id}`)
}

const handleSearch = () => {
  page.value = 1
  loadBidList()
}

const handlePageChange = () => {
  loadBidList()
}

onMounted(() => {
  loadBidList()
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
  min-height: 200px;
}

.bid-card {
  background: var(--el-bg-color);
  border-radius: var(--el-border-radius-md);
  padding: var(--el-spacing-lg);
  margin-bottom: var(--el-spacing-md);
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid var(--el-border-color-light);
}

.bid-card:hover {
  box-shadow: var(--el-box-shadow);
  transform: translateY(-2px);
}

.bid-card-header {
  margin-bottom: var(--el-spacing-md);
}

.status-tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.status-draft { background: var(--el-fill-color); color: var(--el-text-color-secondary); }
.status-in_progress { background: var(--el-color-primary-light-9); color: var(--el-color-primary); }
.status-review { background: var(--el-color-warning-light-9); color: var(--el-color-warning); }
.status-approved { background: var(--el-color-success-light-9); color: var(--el-color-success); }
.status-submitted { background: var(--el-color-info-light-9); color: var(--el-color-info); }

.bid-title {
  margin: 0 0 var(--el-spacing-sm);
  font-size: var(--el-font-size-md);
  font-weight: 600;
}

.bid-desc {
  margin: 0 0 var(--el-spacing-md);
  font-size: var(--el-font-size-sm);
  color: var(--el-text-color-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.bid-card-footer {
  font-size: var(--el-font-size-xs);
  color: var(--el-text-color-secondary);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--el-spacing-xxl);
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: var(--el-spacing-lg);
}
</style>
