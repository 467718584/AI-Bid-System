<template>
  <div class="bid-preview" :class="templateClass">
    <div class="preview-toolbar">
      <el-radio-group v-model="viewMode" size="small">
        <el-radio-button label="outline">目录视图</el-radio-button>
        <el-radio-button label="document">文档视图</el-radio-button>
      </el-radio-group>
      <el-select v-model="zoom" size="small" style="width: 120px">
        <el-option label="50%" :value="50" />
        <el-option label="75%" :value="75" />
        <el-option label="100%" :value="100" />
        <el-option label="125%" :value="125" />
        <el-option label="150%" :value="150" />
      </el-select>
    </div>

    <div class="preview-body" :style="{ transform: `scale(${zoom / 100})` }">
      <!-- 封面 -->
      <div class="preview-cover">
        <h1 class="cover-title">{{ title || '技术投标文件' }}</h1>
        <div class="cover-info">
          <p>项目名称：{{ projectName }}</p>
          <p>编制单位：{{ companyName }}</p>
          <p>编制日期：{{ currentDate }}</p>
        </div>
      </div>

      <!-- 目录视图 -->
      <div v-if="viewMode === 'outline'" class="outline-view">
        <h2 class="section-title">目 录</h2>
        <div class="outline-list">
          <template v-for="item in outline" :key="item.id">
            <div class="outline-item">
              <span class="outline-title">{{ item.title }}</span>
              <span class="outline-dots"></span>
              <span class="outline-page">{{ item.page || '-' }}</span>
            </div>
            <div v-if="item.children?.length" class="outline-children">
              <div
                v-for="child in item.children"
                :key="child.id"
                class="outline-item outline-child"
              >
                <span class="outline-title">{{ child.title }}</span>
                <span class="outline-dots"></span>
                <span class="outline-page">{{ child.page || '-' }}</span>
              </div>
            </div>
          </template>
        </div>
      </div>

      <!-- 文档视图 -->
      <div v-else class="document-view">
        <div v-if="!content" class="empty-content">
          <el-empty description="暂无内容" />
        </div>
        <div v-else class="content-body" v-html="formattedContent"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import dayjs from 'dayjs'

const props = defineProps({
  content: {
    type: String,
    default: ''
  },
  outline: {
    type: Array,
    default: () => []
  },
  title: {
    type: String,
    default: '技术投标文件'
  },
  template: {
    type: String,
    default: 'standard'
  },
  projectName: {
    type: String,
    default: ''
  },
  companyName: {
    type: String,
    default: 'XXXXXX有限公司'
  }
})

const viewMode = ref('document')
const zoom = ref(100)

const currentDate = computed(() => {
  return dayjs().format('YYYY年MM月DD日')
})

const templateClass = computed(() => {
  return `template-${props.template || 'standard'}`
})

const formattedContent = computed(() => {
  if (!props.content) return ''
  // Content is already HTML from Tiptap, return as-is
  return props.content
})
</script>

<style scoped>
.bid-preview {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--el-fill-color);
}

.preview-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--el-spacing-sm) var(--el-spacing-md);
  background: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.preview-body {
  flex: 1;
  overflow: auto;
  padding: var(--el-spacing-lg);
  transform-origin: top center;
}

.preview-cover {
  background: var(--el-bg-color);
  padding: 120px 80px;
  text-align: center;
  box-shadow: var(--el-box-shadow-base);
  margin-bottom: var(--el-spacing-xl);
}

.cover-title {
  font-size: 36px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin-bottom: 60px;
}

.cover-info {
  text-align: right;
  font-size: 16px;
  color: var(--el-text-color-regular);
  line-height: 2;
}

.outline-view {
  background: var(--el-bg-color);
  padding: 60px;
  box-shadow: var(--el-box-shadow-base);
}

.section-title {
  text-align: center;
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 40px;
}

.outline-list {
  max-width: 600px;
  margin: 0 auto;
}

.outline-item {
  display: flex;
  align-items: baseline;
  padding: 8px 0;
  font-size: 16px;
  line-height: 1.6;
}

.outline-title {
  flex-shrink: 0;
}

.outline-dots {
  flex: 1;
  border-bottom: 1px dotted var(--el-border-color-base);
  margin: 0 8px;
  min-width: 40px;
}

.outline-page {
  flex-shrink: 0;
  width: 30px;
  text-align: right;
}

.outline-children {
  padding-left: 40px;
}

.outline-child {
  font-size: 14px;
  color: var(--el-text-color-regular);
}

.document-view {
  background: var(--el-bg-color);
  padding: 80px 100px;
  box-shadow: var(--el-box-shadow-base);
  min-height: 1000px;
}

.content-body {
  font-size: 16px;
  line-height: 2;
  color: var(--el-text-color-regular);
}

.content-body :deep(p) {
  margin-bottom: 16px;
  text-indent: 2em;
  text-align: justify;
}

.content-body :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 16px 0;
}

.content-body :deep(th),
.content-body :deep(td) {
  border: 1px solid var(--el-border-color);
  padding: 8px 12px;
  text-align: left;
}

.content-body :deep(th) {
  background: var(--el-fill-color-light);
  font-weight: 600;
}

.content-body :deep(img) {
  max-width: 100%;
  height: auto;
  margin: 16px 0;
}

.content-body :deep(h1) {
  font-size: 24px;
  font-weight: 600;
  text-align: center;
  margin-bottom: 32px;
}

.content-body :deep(h2) {
  font-size: 20px;
  font-weight: 600;
  margin-top: 32px;
  margin-bottom: 16px;
}

.content-body :deep(h3) {
  font-size: 18px;
  font-weight: 500;
  margin-top: 24px;
  margin-bottom: 12px;
}

.empty-content {
  padding: 60px 0;
}

/* 模板主题样式 */
.template-standard .cover-title,
.template-standard :deep(h1) {
  color: #003366;
}

.template-technical .cover-title,
.template-technical :deep(h1) {
  color: #006400;
}

.template-commercial .cover-title,
.template-commercial :deep(h1) {
  color: #8B4513;
}

.template-professional .cover-title,
.template-professional :deep(h1) {
  color: #191970;
}

.template-simple .cover-title,
.template-simple :deep(h1) {
  color: #333333;
}

/* 模板头部样式 */
.template-standard .preview-header,
.template-standard .preview-cover {
  border-top: 4px solid #003366;
}

.template-technical .preview-header,
.template-technical .preview-cover {
  border-top: 4px solid #006400;
}

.template-commercial .preview-header,
.template-commercial .preview-cover {
  border-top: 4px solid #B8860B;
}

.template-professional .preview-header,
.template-professional .preview-cover {
  border-top: 4px solid #191970;
}

.template-simple .preview-header,
.template-simple .preview-cover {
  border-top: 4px solid #cccccc;
}

/* 模板目录样式 */
.template-standard .outline-view .section-title,
.template-standard .outline-item {
  color: #003366;
}

.template-technical .outline-view .section-title,
.template-technical .outline-item {
  color: #006400;
}

.template-commercial .outline-view .section-title,
.template-commercial .outline-item {
  color: #8B4513;
}

.template-professional .outline-view .section-title,
.template-professional .outline-item {
  color: #191970;
}
</style>