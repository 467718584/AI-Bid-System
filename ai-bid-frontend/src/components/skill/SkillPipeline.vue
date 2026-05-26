<template>
  <div class="skill-pipeline">
    <div class="pipeline-header">
      <div class="header-left">
        <span class="pipeline-title">技能流水线</span>
        <el-tag v-if="pipelineName" size="small">{{ pipelineName }}</el-tag>
      </div>
      <div class="header-right">
        <el-button @click="handleSave" :loading="saving">
          <el-icon><DocumentChecked /></el-icon>
          保存
        </el-button>
        <el-button type="primary" @click="handleRun">
          <el-icon><VideoPlay /></el-icon>
          执行流水线
        </el-button>
      </div>
    </div>

    <div class="pipeline-body">
      <!-- 左侧技能列表 -->
      <div class="skill-list">
        <div class="section-header">
          <span>可用技能</span>
          <el-button type="text" size="small" @click="handleRefreshSkills">
            <el-icon><Refresh /></el-icon>
          </el-button>
        </div>
        <div class="skill-search">
          <el-input
            v-model="skillKeyword"
            placeholder="搜索技能"
            clearable
            size="small"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>
        <div class="skill-items">
          <div
            v-for="skill in filteredSkills"
            :key="skill.id"
            class="skill-item"
            draggable
            @dragstart="handleSkillDragStart($event, skill)"
          >
            <div class="skill-info">
              <el-icon class="skill-icon" :style="{ color: skill.color }">
                <component :is="skill.icon" />
              </el-icon>
              <div class="skill-detail">
                <span class="skill-name">{{ skill.name }}</span>
                <span class="skill-category">{{ skill.category }}</span>
              </div>
            </div>
            <el-tooltip :content="skill.description" placement="right" :show-after="500">
              <el-icon class="skill-help"><QuestionFilled /></el-icon>
            </el-tooltip>
          </div>
        </div>
      </div>

      <!-- 中间流水线设计区 -->
      <div class="pipeline-canvas">
        <div
          ref="pipelineRef"
          class="canvas-dropzone"
          @dragover.prevent="handleDragOver"
          @drop="handleDrop"
        >
          <div v-if="pipelineSteps.length === 0" class="empty-pipeline">
            <el-empty description="拖拽技能到此处构建流水线" :image-size="80" />
          </div>

          <div v-else class="pipeline-steps">
            <div
              v-for="(step, index) in pipelineSteps"
              :key="step.id"
              class="pipeline-step"
              :class="{ 'step-selected': selectedStepId === step.id }"
              @click="handleStepClick(step)"
            >
              <div class="step-number">{{ index + 1 }}</div>
              <div class="step-content">
                <div class="step-header">
                  <el-icon class="step-icon" :style="{ color: step.color }">
                    <component :is="step.icon" />
                  </el-icon>
                  <span class="step-name">{{ step.name }}</span>
                </div>
                <div class="step-description">{{ step.description }}</div>
                <div v-if="step.config" class="step-config">
                  <el-tag size="small" type="info">{{ getConfigSummary(step) }}</el-tag>
                </div>
              </div>
              <div class="step-actions">
                <el-button type="primary" link size="small" @click.stop="handleEditStep(step)">
                  配置
                </el-button>
                <el-button type="danger" link size="small" @click.stop="handleRemoveStep(step)">
                  移除
                </el-button>
              </div>
              <div v-if="index < pipelineSteps.length - 1" class="step-connector">
                <el-icon><DArrowRight /></el-icon>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧配置面板 -->
      <div class="config-panel">
        <div v-if="selectedStep" class="step-config-panel">
          <div class="section-header">
            <span>技能配置</span>
          </div>
          <el-form label-position="top" size="small">
            <el-form-item label="技能名称">
              <el-input v-model="selectedStep.name" disabled />
            </el-form-item>
            <el-form-item label="输入参数">
              <el-input
                v-model="selectedStep.inputTemplate"
                type="textarea"
                :rows="3"
                placeholder="定义输入参数模板"
              />
            </el-form-item>
            <el-form-item label="提示词">
              <el-input
                v-model="selectedStep.prompt"
                type="textarea"
                :rows="4"
                placeholder="输入提示词模板"
              />
            </el-form-item>
            <el-form-item label="输出格式">
              <el-select v-model="selectedStep.outputFormat" style="width: 100%">
                <el-option label="纯文本" value="text" />
                <el-option label="JSON" value="json" />
                <el-option label="Markdown" value="markdown" />
              </el-select>
            </el-form-item>
            <el-form-item label="高级配置">
              <el-collapse>
                <el-collapse-item title="模型参数" name="model">
                  <el-form-item label="模型">
                    <el-select v-model="selectedStep.config.model" style="width: 100%">
                      <el-option label="默认模型" value="default" />
                      <el-option label="GPT-4" value="gpt-4" />
                      <el-option label="Claude" value="claude" />
                    </el-select>
                  </el-form-item>
                  <el-form-item label="温度">
                    <el-slider v-model="selectedStep.config.temperature" :min="0" :max="1" :step="0.1" show-input />
                  </el-form-item>
                  <el-form-item label="最大Token">
                    <el-input-number v-model="selectedStep.config.maxTokens" :min="100" :max="4000" style="width: 100%" />
                  </el-form-item>
                </el-collapse-item>
              </el-collapse>
            </el-form-item>
          </el-form>
          <el-button type="primary" style="width: 100%; margin-top: 16px" @click="handleUpdateStep">
            应用配置
          </el-button>
        </div>
        <div v-else class="empty-config">
          <el-empty description="点击技能查看配置" :image-size="60" />
        </div>
      </div>
    </div>

    <!-- 执行结果对话框 -->
    <el-dialog v-model="resultDialogVisible" title="执行结果" width="700px">
      <div class="result-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="执行状态">
            <el-tag :type="executeResult.success ? 'success' : 'danger'">
              {{ executeResult.success ? '成功' : '失败' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="执行耗时">
            {{ executeResult.duration }}ms
          </el-descriptions-item>
        </el-descriptions>
        <el-divider content-position="left">执行详情</el-divider>
        <div class="result-detail">
          <pre>{{ executeResult.output }}</pre>
        </div>
      </div>
      <template #footer>
        <el-button @click="resultDialogVisible = false">关闭</el-button>
        <el-button v-if="executeResult.success" type="primary" @click="handleUseResult">
          使用结果
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import {
  DocumentChecked,
  VideoPlay,
  Refresh,
  Search,
  QuestionFilled,
  DArrowRight,
  Operation,
  Document,
  Edit,
  Search as SearchIcon,
  FolderOpened
} from '@element-plus/icons-vue'

const emit = defineEmits(['save', 'run'])

const pipelineRef = ref(null)

// 状态
const pipelineName = ref('')
const skillKeyword = ref('')
const skills = ref([])
const pipelineSteps = ref([])
const selectedStepId = ref(null)
const selectedStep = ref(null)
const saving = ref(false)
const resultDialogVisible = ref(false)
const executeResult = reactive({
  success: false,
  duration: 0,
  output: ''
})

// 可用技能
const allSkills = [
  {
    id: 'outline-generator',
    name: '目录生成',
    icon: 'Operation',
    color: '#409eff',
    category: '标书生成',
    description: '使用AI生成投标书目录结构',
    inputTemplate: '{projectName, requirements}',
    prompt: '请根据以下信息生成投标书目录：\n项目名称：{{projectName}}\n要求：{{requirements}}',
    outputFormat: 'json',
    config: { model: 'default', temperature: 0.7, maxTokens: 2000 }
  },
  {
    id: 'content-generator',
    name: '内容生成',
    icon: 'Document',
    color: '#67c23a',
    category: '标书生成',
    description: '使用AI生成标书正文内容',
    inputTemplate: '{chapterTitle, outline}',
    prompt: '请生成以下章节的内容：\n章节标题：{{chapterTitle}}\n目录结构：{{outline}}',
    outputFormat: 'markdown',
    config: { model: 'default', temperature: 0.7, maxTokens: 4000 }
  },
  {
    id: 'polish',
    name: '智能润色',
    icon: 'Edit',
    color: '#e6a23c',
    category: '文本处理',
    description: '对标书内容进行智能润色和优化',
    inputTemplate: '{content}',
    prompt: '请润色以下内容，使其更加专业规范：\n{{content}}',
    outputFormat: 'text',
    config: { model: 'default', temperature: 0.5, maxTokens: 2000 }
  },
  {
    id: 'knowledge-retrieval',
    name: '知识检索',
    icon: 'SearchIcon',
    color: '#9c27b0',
    category: '知识库',
    description: '从知识库检索相关内容',
    inputTemplate: '{query}',
    prompt: '',
    outputFormat: 'json',
    config: { topK: 5, threshold: 0.7 }
  },
  {
    id: 'document-parser',
    name: '文档解析',
    icon: 'FolderOpened',
    color: '#607d8b',
    category: '文档处理',
    description: '解析招标文件，提取关键信息',
    inputTemplate: '{filePath}',
    prompt: '请解析以下招标文件，提取关键信息：',
    outputFormat: 'json',
    config: { extractTables: true, extractImages: false }
  }
]

const filteredSkills = computed(() => {
  if (!skillKeyword.value) return allSkills
  return allSkills.filter(skill =>
    skill.name.includes(skillKeyword.value) ||
    skill.category.includes(skillKeyword.value)
  )
})

const getConfigSummary = (step) => {
  if (!step.config) return ''
  const keys = Object.keys(step.config)
  if (keys.length === 0) return ''
  return `${keys.length}项配置`
}

const handleRefreshSkills = () => {
  ElMessage.success('技能列表已刷新')
}

const handleSkillDragStart = (event, skill) => {
  event.dataTransfer.setData('skill', JSON.stringify(skill))
}

const handleDragOver = (event) => {
  event.dataTransfer.dropEffect = 'copy'
}

const handleDrop = (event) => {
  event.preventDefault()
  const skillData = event.dataTransfer.getData('skill')
  if (!skillData) return

  const skill = JSON.parse(skillData)
  const newStep = {
    id: `step-${Date.now()}`,
    ...skill,
    inputTemplate: skill.inputTemplate,
    prompt: skill.prompt,
    outputFormat: skill.outputFormat,
    config: { ...skill.config }
  }

  pipelineSteps.value.push(newStep)
  ElMessage.success(`已添加技能: ${skill.name}`)
}

const handleStepClick = (step) => {
  selectedStepId.value = step.id
  selectedStep.value = { ...step }
}

const handleEditStep = (step) => {
  handleStepClick(step)
}

const handleRemoveStep = (step) => {
  pipelineSteps.value = pipelineSteps.value.filter(s => s.id !== step.id)
  if (selectedStepId.value === step.id) {
    selectedStepId.value = null
    selectedStep.value = null
  }
}

const handleUpdateStep = () => {
  const index = pipelineSteps.value.findIndex(s => s.id === selectedStepId.value)
  if (index !== -1) {
    pipelineSteps.value[index] = { ...selectedStep.value }
    ElMessage.success('配置已更新')
  }
}

const handleSave = async () => {
  saving.value = true
  try {
    emit('save', {
      name: pipelineName.value,
      steps: pipelineSteps.value
    })
    ElMessage.success('保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const handleRun = async () => {
  if (pipelineSteps.value.length === 0) {
    ElMessage.warning('请先添加技能到流水线')
    return
  }
  try {
    emit('run', {
      steps: pipelineSteps.value
    })
    // 模拟执行结果
    executeResult.success = true
    executeResult.duration = 3500
    executeResult.output = JSON.stringify({
      steps: pipelineSteps.value.map(s => ({ id: s.id, name: s.name, status: 'completed' })),
      finalOutput: '流水线执行成功'
    }, null, 2)
    resultDialogVisible.value = true
  } catch (error) {
    executeResult.success = false
    executeResult.output = error.message
    resultDialogVisible.value = true
  }
}

const handleUseResult = () => {
  ElMessage.success('结果已应用')
  resultDialogVisible.value = false
}
</script>

<style scoped>
.skill-pipeline {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.pipeline-header {
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

.pipeline-title {
  font-weight: 600;
}

.header-right {
  display: flex;
  gap: var(--el-spacing-md);
}

.pipeline-body {
  display: flex;
  flex: 1;
  min-height: 0;
}

.skill-list {
  width: 240px;
  background: var(--el-bg-color);
  border-right: 1px solid var(--el-border-color-lighter);
  display: flex;
  flex-direction: column;
  padding: var(--el-spacing-md);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--el-spacing-md);
  font-weight: 500;
}

.skill-search {
  margin-bottom: var(--el-spacing-md);
}

.skill-items {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: var(--el-spacing-sm);
}

.skill-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--el-spacing-sm) var(--el-spacing-md);
  background: var(--el-fill-color-light);
  border-radius: var(--el-border-radius-base);
  cursor: move;
  transition: all var(--el-transition-fast-duration);
}

.skill-item:hover {
  background: var(--el-fill-color);
}

.skill-info {
  display: flex;
  align-items: center;
  gap: var(--el-spacing-sm);
}

.skill-icon {
  font-size: 18px;
}

.skill-detail {
  display: flex;
  flex-direction: column;
}

.skill-name {
  font-size: var(--el-font-size-sm);
  font-weight: 500;
}

.skill-category {
  font-size: var(--el-font-size-xs);
  color: var(--el-text-color-secondary);
}

.skill-help {
  font-size: 14px;
  color: var(--el-text-color-placeholder);
  cursor: help;
}

.pipeline-canvas {
  flex: 1;
  min-width: 0;
  background: var(--el-fill-color-light);
  overflow: auto;
  padding: var(--el-spacing-lg);
}

.canvas-dropzone {
  min-height: 100%;
  min-width: 600px;
  border: 2px dashed var(--el-border-color);
  border-radius: var(--el-border-radius-base);
  padding: var(--el-spacing-lg);
}

.empty-pipeline {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

.pipeline-steps {
  display: flex;
  flex-wrap: wrap;
  gap: var(--el-spacing-md);
  align-items: flex-start;
}

.pipeline-step {
  display: flex;
  align-items: flex-start;
  gap: var(--el-spacing-md);
  padding: var(--el-spacing-md);
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color);
  border-radius: var(--el-border-radius-base);
  cursor: pointer;
  transition: all var(--el-transition-fast-duration);
  min-width: 280px;
  position: relative;
}

.pipeline-step:hover {
  box-shadow: var(--el-box-shadow-light);
}

.pipeline-step.step-selected {
  border-color: var(--el-color-primary);
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.step-number {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--el-color-primary);
  color: #fff;
  border-radius: 50%;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.step-content {
  flex: 1;
}

.step-header {
  display: flex;
  align-items: center;
  gap: var(--el-spacing-sm);
  margin-bottom: 4px;
}

.step-icon {
  font-size: 18px;
}

.step-name {
  font-weight: 500;
}

.step-description {
  font-size: var(--el-font-size-sm);
  color: var(--el-text-color-secondary);
  margin-bottom: var(--el-spacing-sm);
}

.step-config {
  margin-top: var(--el-spacing-sm);
}

.step-actions {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.step-connector {
  position: absolute;
  right: -24px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--el-text-color-placeholder);
  z-index: 1;
}

.config-panel {
  width: 320px;
  background: var(--el-bg-color);
  border-left: 1px solid var(--el-border-color-lighter);
  display: flex;
  flex-direction: column;
  padding: var(--el-spacing-md);
}

.step-config-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.empty-config {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.result-content {
  max-height: 500px;
  overflow-y: auto;
}

.result-detail {
  background: var(--el-fill-color-light);
  padding: var(--el-spacing-md);
  border-radius: var(--el-border-radius-base);
  max-height: 300px;
  overflow: auto;
}

.result-detail pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-all;
  font-size: var(--el-font-size-sm);
}
</style>