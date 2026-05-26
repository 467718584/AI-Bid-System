<template>
  <div class="content-editor">
    <div class="editor-toolbar">
      <div class="toolbar-left">
        <el-button-group>
          <el-tooltip content="撤销" placement="bottom">
            <el-button :disabled="!canUndo" @click="handleUndo">
              <el-icon><RefreshLeft /></el-icon>
            </el-button>
          </el-tooltip>
          <el-tooltip content="重做" placement="bottom">
            <el-button :disabled="!canRedo" @click="handleRedo">
              <el-icon><RefreshRight /></el-icon>
            </el-button>
          </el-tooltip>
        </el-button-group>
        <el-divider direction="vertical" />
        <el-button-group>
          <el-tooltip content="标题1" placement="bottom">
            <el-button @click="handleFormat('h1')">H1</el-button>
          </el-tooltip>
          <el-tooltip content="标题2" placement="bottom">
            <el-button @click="handleFormat('h2')">H2</el-button>
          </el-tooltip>
          <el-tooltip content="标题3" placement="bottom">
            <el-button @click="handleFormat('h3')">H3</el-button>
          </el-tooltip>
        </el-button-group>
        <el-divider direction="vertical" />
        <el-button-group>
          <el-tooltip content="加粗" placement="bottom">
            <el-button @click="handleFormat('bold')">
              <el-icon><Bolder /></el-icon>
            </el-button>
          </el-tooltip>
          <el-tooltip content="斜体" placement="bottom">
            <el-button @click="handleFormat('italic')">
              <el-icon><Italic /></el-icon>
            </el-button>
          </el-tooltip>
          <el-tooltip content="下划线" placement="bottom">
            <el-button @click="handleFormat('underline')">
              <el-icon><Minus /></el-icon>
            </el-button>
          </el-tooltip>
        </el-button-group>
      </div>
      <div class="toolbar-right">
        <el-button type="primary" :loading="loading" @click="handlePolish">
          <el-icon><MagicStick /></el-icon>
          AI润色
        </el-button>
        <el-button @click="handleGrammarCheck">
          <el-icon><DocumentChecked /></el-icon>
          语法检查
        </el-button>
      </div>
    </div>

    <div class="editor-body">
      <div class="editor-content" ref="editorRef">
        <textarea
          v-model="localContent"
          class="content-textarea"
          placeholder="请输入标书内容..."
          @input="handleInput"
        />
      </div>
    </div>

    <div class="editor-footer">
      <span class="word-count">字数：{{ wordCount }}</span>
      <span class="last-save">最后保存：{{ lastSaveTime || '未保存' }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import {
  RefreshLeft,
  RefreshRight,
  Bolder,
  Italic,
  Minus,
  MagicStick,
  DocumentChecked
} from '@element-plus/icons-vue'

const props = defineProps({
  content: {
    type: String,
    default: ''
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update'])

const editorRef = ref(null)
const localContent = ref(props.content)
const lastSaveTime = ref('')
const undoStack = ref([])
const redoStack = ref([])

const wordCount = computed(() => {
  const text = localContent.value.replace(/\s/g, '')
  return text.length
})

const canUndo = computed(() => undoStack.value.length > 0)
const canRedo = computed(() => redoStack.value.length > 0)

watch(
  () => props.content,
  (newVal) => {
    if (newVal !== localContent.value) {
      localContent.value = newVal
    }
  }
)

const handleInput = () => {
  emit('update', localContent.value)
}

const handleUndo = () => {
  if (undoStack.value.length > 0) {
    const prev = undoStack.value.pop()
    redoStack.value.push(localContent.value)
    localContent.value = prev
    emit('update', localContent.value)
  }
}

const handleRedo = () => {
  if (redoStack.value.length > 0) {
    const next = redoStack.value.pop()
    undoStack.value.push(localContent.value)
    localContent.value = next
    emit('update', localContent.value)
  }
}

const handleFormat = (type) => {
  // TODO: 实现文本格式化
  ElMessage.info(`应用格式: ${type}`)
}

const handlePolish = async () => {
  if (!localContent.value) {
    ElMessage.warning('请先输入内容')
    return
  }
  try {
    // TODO: 调用AI润色API
    ElMessage.success('润色完成')
  } catch (error) {
    ElMessage.error('润色失败')
  }
}

const handleGrammarCheck = async () => {
  if (!localContent.value) {
    ElMessage.warning('请先输入内容')
    return
  }
  try {
    // TODO: 调用语法检查API
    ElMessage.info('语法检查完成')
  } catch (error) {
    ElMessage.error('语法检查失败')
  }
}
</script>

<style scoped>
.content-editor {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.editor-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--el-spacing-sm) var(--el-spacing-md);
  border-bottom: 1px solid var(--el-border-color-lighter);
  background: var(--el-fill-color-light);
  flex-wrap: wrap;
  gap: 8px;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.editor-body {
  flex: 1;
  overflow: hidden;
}

.editor-content {
  height: 100%;
  padding: var(--el-spacing-lg);
}

.content-textarea {
  width: 100%;
  height: 100%;
  border: none;
  resize: none;
  font-family: var(--el-font-family);
  font-size: var(--el-font-size-base);
  line-height: 1.8;
  color: var(--el-text-color-primary);
  background: var(--el-bg-color);
}

.content-textarea:focus {
  outline: none;
}

.content-textarea::placeholder {
  color: var(--el-text-color-placeholder);
}

.editor-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--el-spacing-sm) var(--el-spacing-md);
  border-top: 1px solid var(--el-border-color-lighter);
  font-size: var(--el-font-size-sm);
  color: var(--el-text-color-secondary);
  background: var(--el-fill-color-light);
}
</style>