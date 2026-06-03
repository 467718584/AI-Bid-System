<template>
  <div class="home-view">
    <!-- 欢迎区域 -->
    <div class="welcome-section">
      <h2 class="welcome-title">欢迎使用AI智能投标系统</h2>
      <p class="welcome-desc">智能、高效、专业的投标文件编制平台</p>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-section">
      <el-row :gutter="16">
        <el-col :xs="24" :sm="12" :md="6">
          <div class="stat-card stat-primary">
            <div class="stat-icon">
              <el-icon><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.bidCount }}</div>
              <div class="stat-label">标书总数</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <div class="stat-card stat-success">
            <div class="stat-icon">
              <el-icon><CircleCheck /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.approvedCount }}</div>
              <div class="stat-label">已完成</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <div class="stat-card stat-warning">
            <div class="stat-icon">
              <el-icon><Edit /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.inProgressCount }}</div>
              <div class="stat-label">编制中</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <div class="stat-card stat-danger">
            <div class="stat-icon">
              <el-icon><Folder /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.materialCount }}</div>
              <div class="stat-label">素材数量</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 快捷入口 -->
    <div class="quick-actions">
      <h3 class="section-title">快捷操作</h3>
      <el-row :gutter="16">
        <el-col :xs="12" :sm="8" :md="6">
          <div class="quick-card" @click="router.push('/bid/create')">
            <el-icon class="quick-icon"><Plus /></el-icon>
            <span>创建标书</span>
          </div>
        </el-col>
        <el-col :xs="12" :sm="8" :md="6">
          <div class="quick-card" @click="router.push('/material')">
            <el-icon class="quick-icon"><Upload /></el-icon>
            <span>上传素材</span>
          </div>
        </el-col>
        <el-col :xs="12" :sm="8" :md="6">
          <div class="quick-card" @click="router.push('/workflow')">
            <el-icon class="quick-icon"><Operation /></el-icon>
            <span>工作流管理</span>
          </div>
        </el-col>
        <el-col :xs="12" :sm="8" :md="6">
          <div class="quick-card" @click="router.push('/enterprise')">
            <el-icon class="quick-icon"><OfficeBuilding /></el-icon>
            <span>企业资料</span>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 最近标书 -->
    <div class="recent-section">
      <h3 class="section-title">最近标书</h3>
      <el-table :data="recentBids" style="width: 100%">
        <el-table-column prop="title" label="标书名称" min-width="200" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="updatedAt" label="更新时间" width="160" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleEditBid(row)">
              编辑
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <div v-if="!recentBids.length" class="empty-state">
        <el-empty description="暂无标书" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import {
  Document,
  Folder,
  CircleCheck,
  Edit,
  Plus,
  Upload,
  Operation,
  OfficeBuilding
} from '@element-plus/icons-vue'
import { getBidList } from '@/api/bid'
import { getMaterialStats } from '@/api/material'

const router = useRouter()

// 统计数据
const stats = ref({
  bidCount: 0,
  approvedCount: 0,
  inProgressCount: 0,
  materialCount: 0
})

// 最近标书
const recentBids = ref([])

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

const getStatusType = (status) => {
  const map = {
    draft: 'info',
    in_progress: 'primary',
    review: 'warning',
    approved: 'success',
    submitted: 'success'
  }
  return map[status] || 'info'
}

const handleEditBid = (row) => {
  router.push(`/bid/${row.id}`)
}

// 加载统计数据
const loadStats = async () => {
  try {
    const [bidRes, materialRes] = await Promise.all([
      getBidList({ page: 1, pageSize: 100 }),
      getMaterialStats()
    ])
    const bids = bidRes.data?.list || []
    stats.value = {
      bidCount: bidRes.data?.total || 0,
      approvedCount: bids.filter(b => b.status === 'approved' || b.status === 'submitted').length,
      inProgressCount: bids.filter(b => b.status === 'in_progress' || b.status === 'review').length,
      materialCount: materialRes.data?.total || 0
    }
  } catch (error) {
    // 使用默认值
  }
}

// 加载最近标书
const loadRecentBids = async () => {
  try {
    const res = await getBidList({ page: 1, pageSize: 5 })
    recentBids.value = res.data?.list || []
  } catch (error) {
    // 使用空列表
  }
}

// 初始化
loadStats()
loadRecentBids()
</script>

<style scoped>
.home-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.welcome-section {
  background: linear-gradient(135deg, #409EFF 0%, #337ecc 100%);
  padding: 32px;
  border-radius: 8px;
  text-align: center;
  color: #fff;
}

.welcome-title {
  font-size: 28px;
  font-weight: 600;
  margin: 0 0 8px;
}

.welcome-desc {
  font-size: 14px;
  margin: 0;
  opacity: 0.9;
}

.stats-section {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.stat-card {
  flex: 1;
  min-width: 200px;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
}

.stat-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  border-radius: 12px;
  font-size: 28px;
  color: #fff;
}

.stat-primary .stat-icon { background: #409EFF; }
.stat-success .stat-icon { background: #67C23A; }
.stat-warning .stat-icon { background: #E6A23C; }
.stat-danger .stat-icon { background: #F56C6C; }

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.quick-actions,
.recent-section {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 16px;
}

.quick-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 24px 16px;
  background: #f5f7fa;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.quick-card:hover {
  background: #eef1f5;
  transform: translateY(-2px);
}

.quick-icon {
  font-size: 32px;
  color: #409EFF;
}

.quick-card span {
  font-size: 14px;
  color: #606266;
}

.empty-state {
  display: flex;
  justify-content: center;
  padding: 40px 0;
}
</style>
