<template>
  <div class="content-editor">
    <div class="editor-toolbar">
      <div class="toolbar-left">
        <el-button-group>
          <el-tooltip content="撤销" placement="bottom">
            <el-button :disabled="!editor?.can().undo()" @click="editor?.chain().focus().undo().run()">
              <el-icon><RefreshLeft /></el-icon>
            </el-button>
          </el-tooltip>
          <el-tooltip content="重做" placement="bottom">
            <el-button :disabled="!editor?.can().redo()" @click="editor?.chain().focus().redo().run()">
              <el-icon><RefreshRight /></el-icon>
            </el-button>
          </el-tooltip>
        </el-button-group>
        <el-divider direction="vertical" />
        <el-button-group>
          <el-tooltip content="标题1" placement="bottom">
            <el-button @click="editor?.chain().focus().toggleHeading({ level: 1 }).run()" :class="{ 'is-active': editor?.isActive('heading', { level: 1 }) }">H1</el-button>
          </el-tooltip>
          <el-tooltip content="标题2" placement="bottom">
            <el-button @click="editor?.chain().focus().toggleHeading({ level: 2 }).run()" :class="{ 'is-active': editor?.isActive('heading', { level: 2 }) }">H2</el-button>
          </el-tooltip>
          <el-tooltip content="标题3" placement="bottom">
            <el-button @click="editor?.chain().focus().toggleHeading({ level: 3 }).run()" :class="{ 'is-active': editor?.isActive('heading', { level: 3 }) }">H3</el-button>
          </el-tooltip>
        </el-button-group>
        <el-divider direction="vertical" />
        <el-button-group>
          <el-tooltip content="加粗" placement="bottom">
            <el-button @click="editor?.chain().focus().toggleBold().run()" :class="{ 'is-active': editor?.isActive('bold') }">
              <el-icon><DataLine /></el-icon>
            </el-button>
          </el-tooltip>
          <el-tooltip content="斜体" placement="bottom">
            <el-button @click="editor?.chain().focus().toggleItalic().run()" :class="{ 'is-active': editor?.isActive('italic') }">
              <el-icon><EditPen /></el-icon>
            </el-button>
          </el-tooltip>
          <el-tooltip content="下划线" placement="bottom">
            <el-button @click="editor?.chain().focus().toggleUnderline().run()" :class="{ 'is-active': editor?.isActive('underline') }">
              <el-icon><Minus /></el-icon>
            </el-button>
          </el-tooltip>
        </el-button-group>
        <el-divider direction="vertical" />
        <el-button-group>
          <el-tooltip content="无序列表" placement="bottom">
            <el-button @click="editor?.chain().focus().toggleBulletList().run()" :class="{ 'is-active': editor?.isActive('bulletList') }">
              <el-icon><List /></el-icon>
            </el-button>
          </el-tooltip>
          <el-tooltip content="有序列表" placement="bottom">
            <el-button @click="editor?.chain().focus().toggleOrderedList().run()" :class="{ 'is-active': editor?.isActive('orderedList') }">
              <el-icon><List /></el-icon>
            </el-button>
          </el-tooltip>
        </el-button-group>
        <el-divider direction="vertical" />
        <el-button-group>
          <el-tooltip content="插入表格" placement="bottom">
            <el-button @click="insertTable">
              <el-icon><Grid /></el-icon>
              表格
            </el-button>
          </el-tooltip>
          <el-tooltip content="插入图片" placement="bottom">
            <el-button @click="insertImage">
              <el-icon><Picture /></el-icon>
              图片
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
      <editor-content :editor="editor" class="editor-content" />
    </div>

    <div class="editor-footer">
      <span class="word-count">字数：{{ wordCount }}</span>
      <span class="last-save">最后保存：{{ lastSaveTime || '未保存' }}</span>
    </div>

    <!-- 图片URL输入对话框 -->
    <el-dialog v-model="imageDialogVisible" title="插入图片" width="400px">
      <el-form>
        <el-form-item label="图片URL">
          <el-input v-model="imageUrl" placeholder="请输入图片URL" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="imageDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmInsertImage">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import { Table } from '@tiptap/extension-table'
import { TableRow } from '@tiptap/extension-table-row'
import { TableCell } from '@tiptap/extension-table-cell'
import { TableHeader } from '@tiptap/extension-table-header'
import { Image } from '@tiptap/extension-image'
import Underline from '@tiptap/extension-underline'
import { ElMessage } from 'element-plus'
import { polishContent, checkGrammar } from '@/api/ai'
import {
  RefreshLeft,
  RefreshRight,
  DataLine,
  EditPen,
  Minus,
  List,
  Grid,
  Picture,
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

// Image dialog
const imageDialogVisible = ref(false)
const imageUrl = ref('')

// Editor
const editor = useEditor({
  content: props.content || '',
  extensions: [
    StarterKit,
    Underline,
    Table.configure({
      resizable: true,
    }),
    TableRow,
    TableHeader,
    TableCell,
    Image.configure({
      inline: true,
      allowBase64: true,
    }),
  ],
  onUpdate: ({ editor }) => {
    emit('update', editor.getHTML())
  },
})

// Word count
const wordCount = ref(0)
const lastSaveTime = ref('')

const updateWordCount = () => {
  if (editor.value) {
    const text = editor.value.getText()
    wordCount.value = text.replace(/\s/g, '').length
  }
}

// Watch for content changes from parent
watch(
  () => props.content,
  (newVal) => {
    if (editor.value && newVal !== editor.value.getHTML()) {
      editor.value.commands.setContent(newVal || '')
    }
  }
)

onMounted(() => {
  updateWordCount()
})

onBeforeUnmount(() => {
  editor.value?.destroy()
})

// Insert table
const insertTable = () => {
  editor.value
    ?.chain()
    .focus()
    .insertTable({ rows: 3, cols: 3, withHeaderRow: true })
    .run()
  ElMessage.success('表格已插入')
}

// Insert image
const insertImage = () => {
  imageDialogVisible.value = true
  imageUrl.value = ''
}

const confirmInsertImage = () => {
  if (imageUrl.value) {
    editor.value
      ?.chain()
      .focus()
      .setImage({ src: imageUrl.value })
      .run()
    ElMessage.success('图片已插入')
  }
  imageDialogVisible.value = false
}

// AI Polish
const handlePolish = async () => {
  if (!editor.value?.getText()) {
    ElMessage.warning('请先输入内容')
    return
  }
  loading.value = true
  try {
    const res = await polishContent({ content: editor.value.getHTML() })
    if (res.data?.content) {
      editor.value.commands.setContent(res.data.content)
      emit('update', res.data.content)
      ElMessage.success('润色完成')
    }
  } catch (error) {
    ElMessage.error('润色失败')
  } finally {
    loading.value = false
  }
}

// Grammar check
const handleGrammarCheck = async () => {
  if (!editor.value?.getText()) {
    ElMessage.warning('请先输入内容')
    return
  }
  loading.value = true
  try {
    const res = await checkGrammar({
      content: editor.value.getHTML(),
      requirements: '技术标投标文件，语法规范、专业术语准确'
    })
    const data = res.data || {}
    if (data.corrections && data.corrections.length > 0) {
      ElMessage.info(`发现 ${data.corrections.length} 处问题，已修复`)
      if (data.correctedContent) {
        editor.value.commands.setContent(data.correctedContent)
        emit('update', data.correctedContent)
      }
    } else if (data.pass === false) {
      ElMessage.warning('语法检查发现问题，请检查内容')
    } else {
      ElMessage.success('语法检查完成，未发现问题')
    }
  } catch (error) {
    ElMessage.error('语法检查失败')
  } finally {
    loading.value = false
  }
}

// Expose loading ref
const loading = ref(false)
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
  overflow-y: auto;
}

.editor-content :deep(.tiptap) {
  height: 100%;
  outline: none;
  font-family: var(--el-font-family);
  font-size: var(--el-font-size-base);
  line-height: 1.8;
}

.editor-content :deep(.tiptap p) {
  margin-bottom: 16px;
  text-indent: 2em;
}

.editor-content :deep(.tiptap h1) {
  font-size: 24px;
  font-weight: 600;
  text-align: center;
  margin-bottom: 24px;
}

.editor-content :deep(.tiptap h2) {
  font-size: 20px;
  font-weight: 600;
  margin-top: 24px;
  margin-bottom: 16px;
}

.editor-content :deep(.tiptap h3) {
  font-size: 18px;
  font-weight: 500;
  margin-top: 16px;
  margin-bottom: 12px;
}

.editor-content :deep(.tiptap table) {
  border-collapse: collapse;
  width: 100%;
  margin: 16px 0;
}

.editor-content :deep(.tiptap th),
.editor-content :deep(.tiptap td) {
  border: 1px solid var(--el-border-color);
  padding: 8px 12px;
  text-align: left;
}

.editor-content :deep(.tiptap th) {
  background: var(--el-fill-color-light);
  font-weight: 600;
}

.editor-content :deep(.tiptap img) {
  max-width: 100%;
  height: auto;
  margin: 16px 0;
}

.editor-content :deep(.tiptap ul),
.editor-content :deep(.tiptap ol) {
  padding-left: 24px;
  margin-bottom: 16px;
}

.editor-content :deep(.tiptap li) {
  margin-bottom: 8px;
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

.word-count {
  font-weight: 500;
}

.is-active {
  background: var(--el-color-primary-light-8);
  color: var(--el-color-primary);
}
</style>
