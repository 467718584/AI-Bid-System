<template>
  <div class="skill-catalog">
    <!-- 分类导航 -->
    <div class="category-nav">
      <el-radio-group v-model="activeCategory" @change="handleCategoryChange">
        <el-radio-button label="">全部</el-radio-button>
        <el-radio-button
          v-for="category in categories"
          :key="category"
          :label="category"
        >
          {{ category }}
        </el-radio-button>
      </el-radio-group>
    </div>

    <!-- 搜索和操作 -->
    <div class="toolbar">
      <el-input
        v-model="keyword"
        placeholder="搜索技能名称或描述"
        style="width: 300px"
        clearable
        @clear="handleSearch"
        @keyup.enter="handleSearch"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <div class="toolbar-right">
        <el-button @click="handleInstall">
          <el-icon><Download /></el-icon>
          安装技能
        </el-button>
        <el-button @click="handleRefresh">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <!-- 技能网格 -->
    <div class="skill-grid">
      <el-row :gutter="16">
        <el-col
          v-for="skill in filteredSkills"
          :key="skill.id"
          :xs="24"
          :sm="12"
          :md="8"
          :lg="6"
        >
          <div class="skill-card" @click="handlePreview(skill)">
            <div class="card-header">
              <el-icon class="skill-icon" :style="{ color: skill.color }">
                <component :is="skill.icon" />
              </el-icon>
              <div class="skill-badges">
                <el-tag v-if="skill.isBuiltin" size="small" type="success">内置</el-tag>
                <el-tag v-if="skill.isInstalled" size="small" type="primary">已安装</el-tag>
              </div>
            </div>
            <div class="card-body">
              <h3 class="skill-name">{{ skill.name }}</h3>
              <p class="skill-description">{{ skill.description }}</p>
              <div class="skill-tags">
                <el-tag
                  v-for="tag in skill.tags"
                  :key="tag"
                  size="small"
                  type="info"
                >
                  {{ tag }}
                </el-tag>
              </div>
            </div>
            <div class="card-footer">
              <div class="skill-meta">
                <span class="skill-version">v{{ skill.version }}</span>
                <span class="skill-author">{{ skill.author }}</span>
              </div>
              <div class="skill-actions">
                <el-button
                  v-if="!skill.isInstalled && !skill.isBuiltin"
                  type="primary"
                  size="small"
                  @click.stop="handleInstallSkill(skill)"
                >
                  安装
                </el-button>
                <el-button
                  v-else-if="skill.isInstalled"
                  type="success"
                  size="small"
                  @click.stop="handleUseSkill(skill)"
                >
                  使用
                </el-button>
                <el-button
                  type="info"
                  size="small"
                  @click.stop="handleViewDetail(skill)"
                >
                  详情
                </el-button>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>

      <el-empty v-if="filteredSkills.length === 0" description="未找到匹配的技能">
        <el-button type="primary" @click="handleClearFilter">清除筛选</el-button>
      </el-empty>
    </div>

    <!-- 技能详情对话框 -->
    <el-dialog v-model="detailDialogVisible" :title="previewSkill?.name" width="700px">
      <div v-if="previewSkill" class="skill-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="技能ID">{{ previewSkill.id }}</el-descriptions-item>
          <el-descriptions-item label="版本">v{{ previewSkill.version }}</el-descriptions-item>
          <el-descriptions-item label="作者">{{ previewSkill.author }}</el-descriptions-item>
          <el-descriptions-item label="分类">{{ previewSkill.category }}</el-descriptions-item>
          <el-descriptions-item label="标签" :span="2">
            <el-tag
              v-for="tag in previewSkill.tags"
              :key="tag"
              size="small"
              style="margin-right: 4px"
            >
              {{ tag }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="left">技能描述</el-divider>
        <div class="detail-description">{{ previewSkill.description }}</div>

        <el-divider content-position="left">输入参数</el-divider>
        <div class="detail-code">
          <pre>{{ previewSkill.inputTemplate }}</pre>
        </div>

        <el-divider content-position="left">输出格式</el-divider>
        <div class="detail-output">
          <el-tag>{{ previewSkill.outputFormat }}</el-tag>
        </div>

        <template v-if="previewSkill.configSchema">
          <el-divider content-position="left">配置参数</el-divider>
          <div class="detail-code">
            <pre>{{ JSON.stringify(previewSkill.configSchema, null, 2) }}</pre>
          </div>
        </template>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
        <el-button
          v-if="!previewSkill?.isInstalled"
          type="primary"
          @click="handleInstallSkill(previewSkill); detailDialogVisible = false"
        >
          安装
        </el-button>
        <el-button
          v-else
          type="success"
          @click="handleUseSkill(previewSkill); detailDialogVisible = false"
        >
          使用
        </el-button>
      </template>
    </el-dialog>

    <!-- 安装对话框 -->
    <el-dialog v-model="installDialogVisible" title="安装技能" width="500px">
      <el-form :model="installForm" label-width="100px">
        <el-form-item label="技能包URL">
          <el-input
            v-model="installForm.url"
            placeholder="请输入技能包URL或选择本地文件"
          />
        </el-form-item>
        <el-form-item label="本地文件">
          <el-upload :auto-upload="false" accept=".zip,.tar.gz">
            <el-button type="default">选择文件</el-button>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="installDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="installing" @click="confirmInstall">确认安装</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Download, Refresh } from '@element-plus/icons-vue'

const emit = defineEmits(['install', 'use', 'refresh'])

// 状态
const keyword = ref('')
const activeCategory = ref('')
const categories = ref(['标书生成', '文本处理', '知识库', '文档处理', '数据分析'])
const skills = ref([])
const detailDialogVisible = ref(false)
const installDialogVisible = ref(false)
const previewSkill = ref(null)
const installing = ref(false)

const installForm = ref({
  url: ''
})

// 所有可用技能
const allSkills = [
  {
    id: 'outline-generator',
    name: '目录生成器',
    icon: 'Operation',
    color: '#409eff',
    category: '标书生成',
    description: '使用AI智能生成投标书目录结构，支持自定义章节和模板。',
    tags: ['AI', '目录', '自动生成'],
    version: '1.0.0',
    author: '系统内置',
    isBuiltin: true,
    isInstalled: true,
    inputTemplate: '{\n  projectName: string,\n  bidType: "technical" | "commercial" | "comprehensive",\n  requirements: string[]\n}',
    outputFormat: 'JSON',
    configSchema: { temperature: 0.7, maxTokens: 2000 }
  },
  {
    id: 'content-generator',
    name: '内容生成器',
    icon: 'Document',
    color: '#67c23a',
    category: '标书生成',
    description: '基于目录结构智能生成标书正文内容，支持图文并茂。',
    tags: ['AI', '内容', '自动生成'],
    version: '1.0.0',
    author: '系统内置',
    isBuiltin: true,
    isInstalled: true,
    inputTemplate: '{\n  chapterTitle: string,\n  outline: OutlineNode[],\n  context: string\n}',
    outputFormat: 'Markdown',
    configSchema: { temperature: 0.7, maxTokens: 4000 }
  },
  {
    id: 'polish',
    name: '智能润色',
    icon: 'Edit',
    color: '#e6a23c',
    category: '文本处理',
    description: '对标书内容进行专业润色，提升文字质量和规范性。',
    tags: ['AI', '润色', '优化'],
    version: '1.0.0',
    author: '系统内置',
    isBuiltin: true,
    isInstalled: true,
    inputTemplate: '{\n  content: string,\n  style: "formal" | "concise" | "detailed"\n}',
    outputFormat: 'Text',
    configSchema: { temperature: 0.5, maxTokens: 2000 }
  },
  {
    id: 'grammar-check',
    name: '语法检查',
    icon: 'CircleCheck',
    color: '#f56c6c',
    category: '文本处理',
    description: '自动检查标书语法错误和表达问题，确保文字准确。',
    tags: ['AI', '检查', '语法'],
    version: '1.0.0',
    author: '系统内置',
    isBuiltin: true,
    isInstalled: true,
    inputTemplate: '{\n  content: string,\n  language: "zh" | "en"\n}',
    outputFormat: 'JSON',
    configSchema: { strictMode: true }
  },
  {
    id: 'knowledge-retrieval',
    name: '知识检索',
    icon: 'Search',
    color: '#9c27b0',
    category: '知识库',
    description: '从企业知识库检索相关信息，支持向量检索和混合检索。',
    tags: ['知识库', '检索', 'RAG'],
    version: '1.0.0',
    author: '系统内置',
    isBuiltin: true,
    isInstalled: true,
    inputTemplate: '{\n  query: string,\n  topK: number,\n  threshold: number\n}',
    outputFormat: 'JSON',
    configSchema: { searchType: 'hybrid', topK: 5 }
  },
  {
    id: 'document-parser',
    name: '文档解析',
    icon: 'FolderOpened',
    color: '#607d8b',
    category: '文档处理',
    description: '解析招标文件（PDF/Word），提取关键信息和结构化数据。',
    tags: ['文档', '解析', 'PDF'],
    version: '1.0.0',
    author: '系统内置',
    isBuiltin: true,
    isInstalled: true,
    inputTemplate: '{\n  filePath: string,\n  fileType: "pdf" | "docx"\n}',
    outputFormat: 'JSON',
    configSchema: { extractTables: true, extractImages: false }
  },
  {
    id: 'image-generator',
    name: '图片生成',
    icon: 'Picture',
    color: '#2196f3',
    category: '标书生成',
    description: '根据标书内容自动生成配套图表和插图，提升视觉效果。',
    tags: ['AI', '图片', '图表'],
    version: '1.1.0',
    author: '系统内置',
    isBuiltin: false,
    isInstalled: false,
    inputTemplate: '{\n  description: string,\n  style: string\n}',
    outputFormat: 'Image URL',
    configSchema: null
  },
  {
    id: 'translation',
    name: '智能翻译',
    icon: 'Reading',
    color: '#ff5722',
    category: '文本处理',
    description: '支持中英文互译，保持专业术语一致性。',
    tags: ['翻译', '双语'],
    version: '2.0.0',
    author: '社区贡献',
    isBuiltin: false,
    isInstalled: false,
    inputTemplate: '{\n  content: string,\n  targetLang: "zh" | "en"\n}',
    outputFormat: 'Text',
    configSchema: null
  }
]

const filteredSkills = computed(() => {
  let result = allSkills

  if (activeCategory.value) {
    result = result.filter(s => s.category === activeCategory.value)
  }

  if (keyword.value) {
    const kw = keyword.value.toLowerCase()
    result = result.filter(s =>
      s.name.toLowerCase().includes(kw) ||
      s.description.toLowerCase().includes(kw)
    )
  }

  return result
})

const handleCategoryChange = () => {
  // 分类切换
}

const handleSearch = () => {
  // 搜索
}

const handleClearFilter = () => {
  keyword.value = ''
  activeCategory.value = ''
}

const handleRefresh = () => {
  emit('refresh')
  ElMessage.success('技能列表已刷新')
}

const handleInstall = () => {
  installForm.value.url = ''
  installDialogVisible.value = true
}

const confirmInstall = async () => {
  if (!installForm.value.url) {
    ElMessage.warning('请输入技能包URL')
    return
  }
  installing.value = true
  try {
    emit('install', { url: installForm.value.url })
    ElMessage.success('安装成功')
    installDialogVisible.value = false
  } catch (error) {
    ElMessage.error('安装失败')
  } finally {
    installing.value = false
  }
}

const handleInstallSkill = async (skill) => {
  try {
    emit('install', { skillId: skill.id })
    ElMessage.success(`技能 "${skill.name}" 安装成功`)
  } catch (error) {
    ElMessage.error('安装失败')
  }
}

const handleUseSkill = (skill) => {
  emit('use', { skill })
}

const handleViewDetail = (skill) => {
  previewSkill.value = skill
  detailDialogVisible.value = true
}

const handlePreview = (skill) => {
  handleViewDetail(skill)
}
</script>

<style scoped>
.skill-catalog {
  display: flex;
  flex-direction: column;
  gap: var(--el-spacing-md);
}

.category-nav {
  padding: var(--el-spacing-md);
  background: var(--el-bg-color);
  border-radius: var(--card-radius);
  overflow-x: auto;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--el-spacing-md);
  background: var(--el-bg-color);
  border-radius: var(--card-radius);
}

.toolbar-right {
  display: flex;
  gap: var(--el-spacing-md);
}

.skill-grid {
  background: var(--el-bg-color);
  border-radius: var(--card-radius);
  padding: var(--el-spacing-md);
  min-height: 400px;
}

.skill-card {
  background: var(--el-bg-color-page);
  border: 1px solid var(--el-border-color-lighter);
  border-radius: var(--card-radius);
  padding: var(--el-spacing-md);
  cursor: pointer;
  transition: all var(--el-transition-fast-duration);
  margin-bottom: var(--el-spacing-md);
  height: 100%;
  display: flex;
  flex-direction: column;
}

.skill-card:hover {
  border-color: var(--el-border-color);
  box-shadow: var(--el-box-shadow-light);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--el-spacing-md);
}

.skill-icon {
  font-size: 28px;
}

.skill-badges {
  display: flex;
  gap: 4px;
}

.card-body {
  flex: 1;
}

.skill-name {
  margin: 0 0 var(--el-spacing-sm) 0;
  font-size: var(--el-font-size-base);
  font-weight: 600;
}

.skill-description {
  margin: 0 0 var(--el-spacing-md) 0;
  font-size: var(--el-font-size-sm);
  color: var(--el-text-color-secondary);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.skill-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: var(--el-spacing-md);
  padding-top: var(--el-spacing-md);
  border-top: 1px solid var(--el-border-color-lighter);
}

.skill-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.skill-version {
  font-size: var(--el-font-size-xs);
  color: var(--el-text-color-secondary);
}

.skill-author {
  font-size: var(--el-font-size-xs);
  color: var(--el-text-color-placeholder);
}

.skill-actions {
  display: flex;
  gap: 4px;
}

.skill-detail {
  max-height: 60vh;
  overflow-y: auto;
}

.detail-description {
  line-height: 1.8;
  color: var(--el-text-color-regular);
}

.detail-code {
  background: var(--el-fill-color-light);
  padding: var(--el-spacing-md);
  border-radius: var(--el-border-radius-base);
  overflow-x: auto;
}

.detail-code pre {
  margin: 0;
  font-size: var(--el-font-size-sm);
  white-space: pre-wrap;
}

.detail-output {
  display: flex;
  gap: var(--el-spacing-sm);
}
</style>