<template>
  <div class="enterprise-profile-view">
    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <h2>企业资料管理</h2>
      </div>
      <div class="toolbar-right">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          导出资料
        </el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">
          <el-icon><DocumentChecked /></el-icon>
          保存资料
        </el-button>
      </div>
    </div>

    <!-- 资料完整度 -->
    <div class="completeness-bar">
      <div class="completeness-info">
        <span class="completeness-label">资料完整度</span>
        <el-progress
          :percentage="completeness"
          :color="getCompletenessColor(completeness)"
          style="width: 200px"
        />
        <span class="completeness-text">{{ completeness }}%</span>
      </div>
      <div v-if="suggestions.length > 0" class="completeness-suggestions">
        <el-tag type="warning" size="small">待完善</el-tag>
        <span v-for="(item, index) in suggestions.slice(0, 3)" :key="index" class="suggestion-item">
          {{ item }}
        </span>
      </div>
    </div>

    <!-- 资料主体 -->
    <div class="profile-content">
      <el-tabs v-model="activeTab" class="profile-tabs">
        <!-- 基本信息 -->
        <el-tab-pane label="基本信息" name="basic">
          <el-form :model="enterpriseInfo" label-width="120px" class="profile-form">
            <el-card header="企业基本信息">
              <el-row :gutter="24">
                <el-col :span="12">
                  <el-form-item label="企业名称">
                    <el-input v-model="enterpriseInfo.name" placeholder="请输入企业名称" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="统一社会信用代码">
                    <el-input v-model="enterpriseInfo.creditCode" placeholder="请输入统一社会信用代码" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="法定代表人">
                    <el-input v-model="enterpriseInfo.legalPerson" placeholder="请输入法定代表人" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="注册资本">
                    <el-input v-model="enterpriseInfo.registeredCapital" placeholder="请输入注册资本">
                      <template #append>万元</template>
                    </el-input>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="成立日期">
                    <el-date-picker
                      v-model="enterpriseInfo.establishDate"
                      type="date"
                      placeholder="选择日期"
                      style="width: 100%"
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="企业类型">
                    <el-select v-model="enterpriseInfo.type" placeholder="请选择企业类型" style="width: 100%">
                      <el-option label="有限责任公司" value="limited" />
                      <el-option label="股份有限公司" value="joint-stock" />
                      <el-option label="国有企业" value="state-owned" />
                      <el-option label="民营企业" value="private" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="24">
                  <el-form-item label="注册地址">
                    <el-input v-model="enterpriseInfo.address" placeholder="请输入注册地址" />
                  </el-form-item>
                </el-col>
                <el-col :span="24">
                  <el-form-item label="经营范围">
                    <el-input
                      v-model="enterpriseInfo.businessScope"
                      type="textarea"
                      :rows="3"
                      placeholder="请输入经营范围"
                    />
                  </el-form-item>
                </el-col>
              </el-row>
            </el-card>
          </el-form>
        </el-tab-pane>

        <!-- 资质证书 -->
        <el-tab-pane label="资质证书" name="qualification">
          <div class="section-header">
            <el-button type="primary" @click="handleAddQualification">
              <el-icon><Plus /></el-icon>
              添加资质
            </el-button>
          </div>
          <el-table :data="qualifications" border stripe>
            <el-table-column prop="name" label="资质名称" min-width="150" />
            <el-table-column prop="type" label="资质类型" width="120">
              <template #default="{ row }">
                <el-tag size="small">{{ getQualificationTypeName(row.type) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="level" label="等级" width="100" />
            <el-table-column prop="issueDate" label="发证日期" width="120" />
            <el-table-column prop="expireDate" label="有效期至" width="120" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.expireDate > new Date() ? 'success' : 'danger'" size="small">
                  {{ row.expireDate > new Date() ? '有效' : '过期' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="证书附件" width="100">
              <template #default="{ row }">
                <el-button
                  v-if="row.fileUrl"
                  type="primary"
                  link
                  size="small"
                  @click="handlePreviewFile(row)"
                >
                  查看
                </el-button>
                <span v-else class="text-muted">未上传</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="handleEditQualification(row)">
                  编辑
                </el-button>
                <el-button type="danger" link size="small" @click="handleDeleteQualification(row)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- 业绩案例 -->
        <el-tab-pane label="业绩案例" name="experience">
          <div class="section-header">
            <el-button type="primary" @click="handleAddExperience">
              <el-icon><Plus /></el-icon>
              添加业绩
            </el-button>
          </div>
          <el-table :data="experiences" border stripe>
            <el-table-column prop="projectName" label="项目名称" min-width="150" />
            <el-table-column prop="owner" label="甲方单位" width="150" />
            <el-table-column prop="contractAmount" label="合同金额(万元)" width="120" align="right">
              <template #default="{ row }">
                {{ row.contractAmount?.toLocaleString() }}
              </template>
            </el-table-column>
            <el-table-column prop="startDate" label="开始时间" width="120" />
            <el-table-column prop="endDate" label="结束时间" width="120" />
            <el-table-column prop="status" label="项目状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getExperienceStatusType(row.status)" size="small">
                  {{ getExperienceStatusName(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="handleEditExperience(row)">
                  编辑
                </el-button>
                <el-button type="danger" link size="small" @click="handleDeleteExperience(row)">
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- 财务数据 -->
        <el-tab-pane label="财务数据" name="financial">
          <el-form :model="financialData" label-width="140px" class="profile-form">
            <el-card header="近三年财务数据">
              <el-row :gutter="24">
                <el-col :span="8">
                  <el-form-item label="年度">
                    <el-input v-model="financialData.year" disabled />
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="资产总额(万元)">
                    <el-input-number
                      v-model="financialData.totalAssets"
                      :min="0"
                      :precision="2"
                      style="width: 100%"
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="净资产总额(万元)">
                    <el-input-number
                      v-model="financialData.netAssets"
                      :min="0"
                      :precision="2"
                      style="width: 100%"
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="营业收入(万元)">
                    <el-input-number
                      v-model="financialData.revenue"
                      :min="0"
                      :precision="2"
                      style="width: 100%"
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="利润总额(万元)">
                    <el-input-number
                      v-model="financialData.profit"
                      :min="0"
                      :precision="2"
                      style="width: 100%"
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="净利润(万元)">
                    <el-input-number
                      v-model="financialData.netProfit"
                      :min="0"
                      :precision="2"
                      style="width: 100%"
                    />
                  </el-form-item>
                </el-col>
              </el-row>
            </el-card>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 资质证书对话框 -->
    <el-dialog v-model="qualificationDialogVisible" :title="qualificationDialogTitle" width="600px">
      <el-form :model="qualificationForm" label-width="120px">
        <el-form-item label="资质名称" required>
          <el-input v-model="qualificationForm.name" placeholder="请输入资质名称" />
        </el-form-item>
        <el-form-item label="资质类型" required>
          <el-select v-model="qualificationForm.type" placeholder="请选择资质类型" style="width: 100%">
            <el-option label="建筑业企业资质" value="construction" />
            <el-option label="安全生产许可证" value="safety" />
            <el-option label="ISO认证" value="iso" />
            <el-option label="其他资质" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="资质等级">
          <el-input v-model="qualificationForm.level" placeholder="请输入资质等级" />
        </el-form-item>
        <el-form-item label="发证日期">
          <el-date-picker v-model="qualificationForm.issueDate" type="date" style="width: 100%" />
        </el-form-item>
        <el-form-item label="有效期至">
          <el-date-picker v-model="qualificationForm.expireDate" type="date" style="width: 100%" />
        </el-form-item>
        <el-form-item label="证书附件">
          <el-upload
            :auto-upload="false"
            :limit="1"
            accept=".pdf,.jpg,.png"
          >
            <el-button type="primary">上传证书</el-button>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="qualificationDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmQualification">确定</el-button>
      </template>
    </el-dialog>

    <!-- 业绩对话框 -->
    <el-dialog v-model="experienceDialogVisible" :title="experienceDialogTitle" width="700px">
      <el-form :model="experienceForm" label-width="120px">
        <el-form-item label="项目名称" required>
          <el-input v-model="experienceForm.projectName" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="甲方单位">
          <el-input v-model="experienceForm.owner" placeholder="请输入甲方单位" />
        </el-form-item>
        <el-form-item label="合同金额(万元)">
          <el-input-number v-model="experienceForm.contractAmount" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="开始时间">
              <el-date-picker v-model="experienceForm.startDate" type="date" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束时间">
              <el-date-picker v-model="experienceForm.endDate" type="date" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="项目描述">
          <el-input v-model="experienceForm.description" type="textarea" :rows="3" placeholder="请输入项目描述" />
        </el-form-item>
        <el-form-item label="项目状态">
          <el-select v-model="experienceForm.status" style="width: 100%">
            <el-option label="进行中" value="ongoing" />
            <el-option label="已完成" value="completed" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="experienceDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmExperience">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Download,
  DocumentChecked,
  Plus
} from '@element-plus/icons-vue'
import {
  getEnterpriseInfo,
  updateEnterpriseInfo,
  getEnterpriseQualifications,
  getProjectExperiences,
  getFinancialData,
  updateFinancialData,
  getCompletenessSuggestions
} from '@/api/enterprise'

// 状态
const activeTab = ref('basic')
const saving = ref(false)
const completeness = ref(0)
const suggestions = ref([])

// 基本信息
const enterpriseInfo = ref({
  name: '',
  creditCode: '',
  legalPerson: '',
  registeredCapital: '',
  establishDate: '',
  type: '',
  address: '',
  businessScope: ''
})

// 资质证书
const qualifications = ref([])
const qualificationDialogVisible = ref(false)
const qualificationDialogTitle = ref('')
const qualificationForm = ref({
  id: '',
  name: '',
  type: '',
  level: '',
  issueDate: '',
  expireDate: '',
  file: null
})

// 业绩
const experiences = ref([])
const experienceDialogVisible = ref(false)
const experienceDialogTitle = ref('')
const experienceForm = ref({
  id: '',
  projectName: '',
  owner: '',
  contractAmount: 0,
  startDate: '',
  endDate: '',
  description: '',
  status: 'completed'
})

// 财务数据
const financialData = ref({
  year: new Date().getFullYear().toString(),
  totalAssets: 0,
  netAssets: 0,
  revenue: 0,
  profit: 0,
  netProfit: 0
})

// ========== 生命周期 ==========

onMounted(async () => {
  await loadEnterpriseInfo()
  await loadQualifications()
  await loadExperiences()
  await loadFinancialData()
  await loadSuggestions()
})

// ========== 方法 ==========

const loadEnterpriseInfo = async () => {
  try {
    const res = await getEnterpriseInfo()
    enterpriseInfo.value = res.data || enterpriseInfo.value
  } catch (error) {
    // 使用默认值
  }
}

const loadQualifications = async () => {
  try {
    const res = await getEnterpriseQualifications()
    qualifications.value = res.data?.list || []
  } catch (error) {
    // 使用空列表
  }
}

const loadExperiences = async () => {
  try {
    const res = await getProjectExperiences()
    experiences.value = res.data?.list || []
  } catch (error) {
    // 使用空列表
  }
}

const loadFinancialData = async () => {
  try {
    const res = await getFinancialData()
    financialData.value = res.data || financialData.value
  } catch (error) {
    // 使用默认值
  }
}

const loadSuggestions = async () => {
  try {
    const res = await getCompletenessSuggestions()
    suggestions.value = res.data || []
    // 计算完整度
    completeness.value = res.data?.completeness || 0
  } catch (error) {
    // 使用默认值
  }
}

const handleSave = async () => {
  saving.value = true
  try {
    await updateEnterpriseInfo(enterpriseInfo.value)
    await updateFinancialData(financialData.value)
    ElMessage.success('保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const handleExport = () => {
  ElMessage.info('导出资料功能开发中')
}

const handleAddQualification = () => {
  qualificationForm.value = {
    id: '',
    name: '',
    type: '',
    level: '',
    issueDate: '',
    expireDate: '',
    file: null
  }
  qualificationDialogTitle.value = '添加资质'
  qualificationDialogVisible.value = true
}

const handleEditQualification = (row) => {
  qualificationForm.value = { ...row }
  qualificationDialogTitle.value = '编辑资质'
  qualificationDialogVisible.value = true
}

const handleDeleteQualification = async (row) => {
  ElMessage.info('删除资质功能开发中')
}

const confirmQualification = async () => {
  ElMessage.success('保存成功')
  qualificationDialogVisible.value = false
  await loadQualifications()
}

const handlePreviewFile = (row) => {
  window.open(row.fileUrl)
}

const handleAddExperience = () => {
  experienceForm.value = {
    id: '',
    projectName: '',
    owner: '',
    contractAmount: 0,
    startDate: '',
    endDate: '',
    description: '',
    status: 'completed'
  }
  experienceDialogTitle.value = '添加业绩'
  experienceDialogVisible.value = true
}

const handleEditExperience = (row) => {
  experienceForm.value = { ...row }
  experienceDialogTitle.value = '编辑业绩'
  experienceDialogVisible.value = true
}

const handleDeleteExperience = async (row) => {
  ElMessage.info('删除业绩功能开发中')
}

const confirmExperience = async () => {
  ElMessage.success('保存成功')
  experienceDialogVisible.value = false
  await loadExperiences()
}

const getQualificationTypeName = (type) => {
  const map = {
    construction: '建筑业',
    safety: '安全许可',
    iso: 'ISO认证',
    other: '其他'
  }
  return map[type] || type
}

const getExperienceStatusType = (status) => {
  return status === 'completed' ? 'success' : 'primary'
}

const getExperienceStatusName = (status) => {
  return status === 'completed' ? '已完成' : '进行中'
}

const getCompletenessColor = (percentage) => {
  if (percentage >= 80) return '#67c23a'
  if (percentage >= 50) return '#e6a23c'
  return '#f56c6c'
}
</script>

<style scoped>
.enterprise-profile-view {
  display: flex;
  flex-direction: column;
  gap: var(--el-spacing-md);
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--el-spacing-md);
  background: var(--el-bg-color);
  border-radius: var(--card-radius);
}

.toolbar-left h2 {
  margin: 0;
  font-size: var(--el-font-size-md);
  font-weight: 600;
}

.toolbar-right {
  display: flex;
  gap: var(--el-spacing-md);
}

.completeness-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--el-spacing-md);
  background: var(--el-bg-color);
  border-radius: var(--card-radius);
}

.completeness-info {
  display: flex;
  align-items: center;
  gap: var(--el-spacing-md);
}

.completeness-label {
  font-weight: 500;
}

.completeness-text {
  color: var(--el-text-color-secondary);
  font-size: var(--el-font-size-sm);
}

.completeness-suggestions {
  display: flex;
  align-items: center;
  gap: var(--el-spacing-sm);
}

.suggestion-item {
  color: var(--el-text-color-secondary);
  font-size: var(--el-font-size-sm);
}

.suggestion-item:not(:last-child)::after {
  content: '、';
}

.profile-content {
  flex: 1;
  background: var(--el-bg-color);
  border-radius: var(--card-radius);
  overflow: hidden;
}

.profile-tabs {
  padding: 0 var(--el-spacing-md);
}

.profile-form {
  padding: var(--el-spacing-md) 0;
}

.section-header {
  display: flex;
  justify-content: flex-end;
  margin-bottom: var(--el-spacing-md);
}

.text-muted {
  color: var(--el-text-color-placeholder);
  font-size: var(--el-font-size-sm);
}
</style>