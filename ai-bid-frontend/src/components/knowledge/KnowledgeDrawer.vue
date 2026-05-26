<template>
  <el-drawer
    :model-value="modelValue"
    title="知识库检索"
    size="500px"
    direction="rtl"
    @update:model-value="$emit('update:modelValue', $event)"
  >
    <div class="knowledge-drawer">
      <!-- 搜索表单 -->
      <div class="search-form">
        <el-form label-position="top">
          <el-form-item label="检索关键词">
            <el-input
              v-model="form.query"
              type="textarea"
              :rows="3"
              placeholder="输入检索关键词，如：项目名称、技术要求、资质条件等"
              @keyup.enter="handleSearch"
            />
          </el-form-item>
          <el-form-item label="检索模式">
            <el-radio-group v-model="form.mode">
              <el-radio label="hybrid">混合检索</el-radio>
              <el-radio label="vector">向量检索</el-radio>
              <el-radio label="keyword">关键词检索</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="返回数量">
            <el-input-number v-model="form.topK" :min="1" :max="20" />
          </el-form-item>
        </el-form>
        <el-button type="primary" :loading="searching" style="width: 100%" @click="handleSearch">
          <el-icon><Search /></el-icon>
          检索
        </el-button>
      </div>

      <el-divider content-position="left">检索结果</el-divider>

      <!-- 搜索结果 -->
      <div v-if="searching" class="loading-state">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>正在检索...</span>
      </div>

      <div v-else-if="results.length === 0 && searched" class="empty-state">
        <el-empty description="未找到相关知识" :image-size="60" />
      </div>

      <div v-else class="result-list">
        <div
          v-for="(item, index) in results"
          :key="index"
          class="result-item"
          @click="handleSelect(item)"
        >
          <div class="result-header">
            <span class="result-index">{{ index + 1 }}</span>
            <span class="result-title">{{ item.title }}</span>
            <el-tag size="small" type="info">
              {{ (item.score * 100).toFixed(1) }}%
            </el-tag>
          </div>
          <div class="result-content">{{ item.content }}</div>
          <div v-if="item.source" class="result-source">
            来源：{{ item.source }}
          </div>
          <div class="result-actions">
            <el-button type="primary" link size="small" @click.stop="handlePreview(item)">
              预览
            </el-button>
            <el-button type="primary" link size="small" @click.stop="handleSelect(item)">
              插入
            </el-button>
          </div>
        </div>
      </div>

      <!-- 知识分类快捷入口 -->
      <el-divider content-position="left">知识分类</el-divider>
      <div class="category-chips">
        <el-tag
          v-for="category in categories"
          :key="category"
          class="category-chip"
          @click="handleCategoryClick(category)"
        >
          {{ category }}
        </el-tag>
      </div>
    </div>

    <!-- 预览对话框 -->
    <el-dialog v-model="previewVisible" title="知识预览" width="600px">
      <div class="preview-content">
        <h3>{{ previewItem?.title }}</h3>
        <div class="preview-meta">
          <el-tag size="small" type="info">{{ previewItem?.category }}</el-tag>
          <span class="preview-source">{{ previewItem?.source }}</span>
        </div>
        <el-divider />
        <div class="preview-body">
          {{ previewItem?.content }}
        </div>
      </div>
      <template #footer>
        <el-button @click="previewVisible = false">关闭</el-button>
        <el-button type="primary" @click="handleSelect(previewItem); previewVisible = false">
          插入到正文
        </el-button>
      </template>
    </el-dialog>
  </el-drawer>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Loading } from '@element-plus/icons-vue'
import { searchKnowledge, hybridSearch } from '@/api/knowledge'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'select'])

const form = reactive({
  query: '',
  mode: 'hybrid',
  topK: 5
})

const searching = ref(false)
const searched = ref(false)
const results = ref([])
const categories = ref([
  '投标规范',
  '技术方案',
  '资质要求',
  '合同范本',
  '行业标准',
  '案例库'
])
const previewVisible = ref(false)
const previewItem = ref(null)

const handleSearch = async () => {
  if (!form.query.trim()) {
    ElMessage.warning('请输入检索关键词')
    return
  }

  searching.value = true
  searched.value = true
  try {
    const params = {
      query: form.query,
      mode: form.mode,
      topK: form.topK
    }

    let res
    if (form.mode === 'hybrid') {
      res = await hybridSearch(params)
    } else {
      res = await searchKnowledge(params)
    }
    results.value = res.data || []
  } catch (error) {
    results.value = []
    ElMessage.error('检索失败')
  } finally {
    searching.value = false
  }
}

const handleSelect = (item) => {
  emit('select', item)
}

const handlePreview = (item) => {
  previewItem.value = item
  previewVisible.value = true
}

const handleCategoryClick = (category) => {
  form.query = category
  handleSearch()
}
</script>

<style scoped>
.knowledge-drawer {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.search-form {
  margin-bottom: var(--el-spacing-md);
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--el-spacing-sm);
  padding: var(--el-spacing-lg);
  color: var(--el-text-color-secondary);
}

.result-list {
  display: flex;
  flex-direction: column;
  gap: var(--el-spacing-md);
  max-height: 400px;
  overflow-y: auto;
}

.result-item {
  padding: var(--el-spacing-md);
  background: var(--el-fill-color-light);
  border-radius: var(--el-border-radius-base);
  cursor: pointer;
  transition: all var(--el-transition-fast-duration);
}

.result-item:hover {
  background: var(--el-fill-color);
}

.result-header {
  display: flex;
  align-items: center;
  gap: var(--el-spacing-sm);
  margin-bottom: var(--el-spacing-sm);
}

.result-index {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  background: var(--el-color-primary);
  color: #fff;
  border-radius: 50%;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.result-title {
  flex: 1;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.result-content {
  font-size: var(--el-font-size-sm);
  color: var(--el-text-color-secondary);
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: var(--el-spacing-sm);
}

.result-source {
  font-size: var(--el-font-size-xs);
  color: var(--el-text-color-placeholder);
  margin-bottom: var(--el-spacing-sm);
}

.result-actions {
  display: flex;
  gap: var(--el-spacing-sm);
}

.category-chips {
  display: flex;
  flex-wrap: wrap;
  gap: var(--el-spacing-sm);
}

.category-chip {
  cursor: pointer;
}

.preview-content h3 {
  margin: 0 0 var(--el-spacing-md) 0;
}

.preview-meta {
  display: flex;
  align-items: center;
  gap: var(--el-spacing-md);
}

.preview-source {
  font-size: var(--el-font-size-sm);
  color: var(--el-text-color-secondary);
}

.preview-body {
  line-height: 1.8;
  white-space: pre-wrap;
}
</style>