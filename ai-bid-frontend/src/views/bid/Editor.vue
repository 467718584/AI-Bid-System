<template>
  <div class="bid-editor">
    <div class="editor-header">
      <div class="header-left">
        <el-button @click="handleBack">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <el-input
          v-model="bidTitle"
          placeholder="请输入标书标题"
          class="title-input"
        />
      </div>
      <div class="header-right">
        <el-button @click="handlePreview">
          <el-icon><View /></el-icon>
          预览
        </el-button>
        <el-button @click="handleReorder" :disabled="!outline.length">
          <el-icon><Sort /></el-icon>
          重新排序
        </el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">
          <el-icon><DocumentChecked /></el-icon>
          保存
        </el-button>
        <el-button type="success" :loading="submitting" @click="handleSubmit">
          <el-icon><Upload /></el-icon>
          提交
        </el-button>
      </div>
    </div>

    <div class="editor-content">
      <div class="outline-panel">
        <BidOutlineGenerator
          :outline="outline"
          :loading="generating"
          @generate="handleGenerateOutline"
          @update="handleUpdateOutline"
          @generate-content="handleGenerateContent"
        />
      </div>
      <div class="content-panel">
        <BidContentEditor
          :content="content"
          :loading="generating"
          @update="handleUpdateContent"
        />
      </div>
      <div class="upload-panel">
        <DocumentUploader
          @upload="handleUpload"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useBidStore } from '@/stores/bid'
import { ElMessage } from 'element-plus'
import BidOutlineGenerator from '@/components/bid/BidOutlineGenerator.vue'
import BidContentEditor from '@/components/bid/BidContentEditor.vue'
import DocumentUploader from '@/components/bid/DocumentUploader.vue'
import { getBidDetail, updateBid } from '@/api/bid'
import { ArrowLeft, View, DocumentChecked, Upload, Sort } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const bidStore = useBidStore()

const bidTitle = ref('')
const saving = ref(false)
const submitting = ref(false)
const generating = ref(false)

const outline = ref([])
const content = ref('')

const handleBack = () => {
  router.push('/bid')
}

const handlePreview = () => {
  const id = route.params.id
  if (id) {
    router.push(`/bid/${id}/preview`)
  }
}

const handleSave = async () => {
  if (!bidTitle.value) {
    ElMessage.warning('请输入标书标题')
    return
  }
  saving.value = true
  try {
    const id = route.params.id
    if (id) {
      // 更新已有标书
      await updateBid(id, {
        title: bidTitle.value,
        outline: outline.value,
        content: content.value
      })
    }
    ElMessage.success('保存成功')
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const handleSubmit = async () => {
  await handleSave()
  submitting.value = true
  try {
    // TODO: 调用提交API
    ElMessage.success('提交成功')
  } catch (error) {
    ElMessage.error('提交失败')
  } finally {
    submitting.value = false
  }
}

// 重新排序内容，基于目录顺序
const handleReorder = () => {
  if (!content.value || !outline.value.length) {
    ElMessage.warning('没有内容可排序')
    return
  }
  
  // 提取所有章节块并按目录顺序重新排列
  const chapterBlocks = []
  
  // 尝试匹配新版格式：<div class="chapter-block" data-chapter="...">
  let regex = /<div class="chapter-block" data-chapter="([^"]+)">([\s\S]*?)<\/div>/g
  let match
  while ((match = regex.exec(content.value)) !== null) {
    chapterBlocks.push({ chapter: match[1], block: match[0] })
  }
  
  // 如果没有新版格式，尝试匹配旧版格式：<h1>或<h2>或<h3>标题</h...>
  if (chapterBlocks.length === 0) {
    // 匹配所有级别的标题标签 <h1>, <h2>, <h3>
    const hRegex = /<h([1-3])(?:[^>]*)>([\s\S]*?)<\/h\1>/g
    const hPositions = []
    let hMatch
    while ((hMatch = hRegex.exec(content.value)) !== null) {
      hPositions.push({ 
        level: parseInt(hMatch[1]), 
        title: hMatch[2].trim(), 
        pos: hMatch.index, 
        len: hMatch[0].length,
        content: hMatch[2]
      })
    }
    
    if (hPositions.length > 0) {
      // 按位置切分内容块 - 每个标题到下一个同级或更高级标题之前
      for (let i = 0; i < hPositions.length; i++) {
        const startPos = hPositions[i].pos
        const currentLevel = hPositions[i].level
        
        // 找下一个同级或更高级的标题位置
        let endPos = content.value.length
        for (let j = i + 1; j < hPositions.length; j++) {
          if (hPositions[j].level <= currentLevel) {
            endPos = hPositions[j].pos
            break
          }
        }
        
        // 确保每个块都包含完整内容（从标题开始到下一个标题之前）
        const blockContent = content.value.substring(startPos, endPos).trim()
        if (blockContent) {
          chapterBlocks.push({ chapter: hPositions[i].title, block: blockContent })
        }
      }
    }
  }
  
  if (chapterBlocks.length === 0) {
    ElMessage.warning('未找到可识别的章节内容')
    return
  }
  
  // 按目录顺序排序
  const orderedChapters = []
  const flatOutline = []
  
  // 展平目录结构 - 支持嵌套层级
  const flattenOutline = (items) => {
    items.forEach(item => {
      flatOutline.push(item.title)
      if (item.children && item.children.length) {
        flattenOutline(item.children)
      }
    })
  }
  flattenOutline(outline.value)
  
  // 辅助函数：检查标题是否匹配（支持模糊匹配）
  const titleMatches = (blockTitle, outlineTitle) => {
    // 精确匹配
    if (blockTitle === outlineTitle) return true
    // 去掉"第X章"前缀后匹配
    const normalize = (t) => t.replace(/^第[一二三四五六七八九十]+章\s*/, '').replace(/^第\d+章\s*/, '')
    return normalize(blockTitle) === normalize(outlineTitle) || 
           blockTitle.includes(outlineTitle) || 
           outlineTitle.includes(blockTitle)
  }
  
  // 按目录顺序重新排列
  flatOutline.forEach(chapterTitle => {
    // 优先精确匹配
    let block = chapterBlocks.find(b => b.chapter === chapterTitle)
    if (!block) {
      // 然后模糊匹配
      block = chapterBlocks.find(b => titleMatches(b.chapter, chapterTitle))
    }
    if (block) {
      orderedChapters.push(block.block)
    }
  })
  
  // 保留未识别的章节块（按原顺序放在最后）
  const usedChapters = new Set(orderedChapters.map(b => b.chapter))
  chapterBlocks.forEach(b => {
    if (!usedChapters.has(b.chapter)) {
      orderedChapters.push(b.block)
    }
  })
  
  content.value = orderedChapters.join('\n')
  ElMessage.success('内容已按目录顺序重新排序')
}

const handleGenerateOutline = async (params) => {
  generating.value = true
  try {
    await bidStore.generateOutlineAsync(params)
    outline.value = bidStore.outline
    ElMessage.success('目录生成成功')
  } catch (error) {
    ElMessage.error('目录生成失败')
  } finally {
    generating.value = false
  }
}

const handleUpdateOutline = (newOutline) => {
  outline.value = newOutline
}

const handleUpdateContent = (newContent) => {
  content.value = newContent
}

// Markdown转HTML函数
const markdownToHtml = (md) => {
  if (!md) return ''
  let html = md
  // 处理加粗 **text** -> <strong>text</strong>
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  // 处理标题
  html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>')
  html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>')
  html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>')
  // 处理表格标记 -> 转换为HTML表格
  html = html.replace(/!\[([^)]*)\]\(table:(\[[\s\S]*?\])\)/g, (match, title, tableJson) => {
    try {
      const tableData = JSON.parse(tableJson)
      if (tableData && tableData[0]) {
        const t = tableData[0]
        const headers = t.headers || []
        const rows = t.rows || []
        let tableHtml = '<table style="border-collapse:collapse;width:100%;margin:16px 0;">'
        if (headers.length) {
          tableHtml += '<thead><tr>'
          headers.forEach(h => { tableHtml += `<th style="border:1px solid #ddd;padding:8px 12px;background:#f5f5f5;font-weight:600;">${h}</th>` })
          tableHtml += '</tr></thead>'
        }
        tableHtml += '<tbody>'
        rows.forEach(row => {
          tableHtml += '<tr>'
          row.forEach(cell => { tableHtml += `<td style="border:1px solid #ddd;padding:8px 12px;">${cell}</td>` })
          tableHtml += '</tr>'
        })
        tableHtml += '</tbody></table>'
        return tableHtml
      }
    } catch (e) { console.error('Table parse error:', e) }
    return `<p><em>[${title}表格]</em></p>`
  })
  // 处理图表标记 -> chart:前缀 或 包含"图表"文字的URL -> 转为占位符显示
  html = html.replace(/!\[([^]]*)\]\((chart:[^)]+)\)/g, '<div class="chart-placeholder" data-title="$1"><span class="chart-icon">📊</span><span class="chart-title">[$1图表]</span></div>')
  html = html.replace(/!\[([^]]*)\]\(([^)]*图表[^)]*)\)/g, '<div class="chart-placeholder" data-title="$1"><span class="chart-icon">📊</span><span class="chart-title">[$1图表]</span></div>')
  // 处理普通图片 -> 如果URL不是有效网络地址，转换为占位符
  html = html.replace(/!\[([^]]*)\]\((?!http|data:)([^)]+)\)/g, '<div class="image-placeholder" data-title="$1"><span class="image-icon">🖼️</span><span class="image-title">[$1图片]</span></div>')
  // 处理MD表格语法: | col1 | col2 | -> HTML表格
  html = html.replace(/<p>\|(.+)\|<\/p>\n<p>\|[-\s|]+\|<\/p>([\s\S]*?)(?=<p>\|\S|\n<p>```|\n<h[123]>|\n<p>\*\*|$)/g, (match, headerRow, bodyRows) => {
    try {
      // 解析表头
      const headers = headerRow.split('|').filter(c => c.trim()).map(c => c.trim())
      // 解析表体
      const rows = []
      const rowMatches = bodyRows.matchAll(/<p>\|(.+)\|<\/p>/g)
      for (const rowMatch of rowMatches) {
        const cells = rowMatch[1].split('|').filter(c => c.trim()).map(c => c.trim())
        if (cells.length > 0) rows.push(cells)
      }
      if (headers.length === 0) return match
      let tableHtml = '<table style="border-collapse:collapse;width:100%;margin:16px 0;">')
      tableHtml += '<thead><tr>'
      headers.forEach(h => { tableHtml += `<th style="border:1px solid #ddd;padding:8px 12px;background:#f5f5f5;font-weight:600;">${h}</th>` })
      tableHtml += '</tr></thead>'
      tableHtml += '<tbody>'
      rows.forEach(row => {
        tableHtml += '<tr>'
        row.forEach(cell => { tableHtml += `<td style="border:1px solid #ddd;padding:8px 12px;">${cell}</td>` })
        tableHtml += '</tr>'
      })
      tableHtml += '</tbody></table>'
      return tableHtml
    } catch (e) { console.error('MD Table parse error:', e) }
    return match
  })
  const lines = html.split('\n')
  html = lines.map(line => {
    line = line.trim()
    if (!line) return ''
    if (line.match(/^<\/?(h[1-6]|table|thead|tbody|tr|th|td|p|ul|ol|li|hr)/)) return line
    if (line === '<p></p>') return ''
    return '<p>' + line + '</p>'
  }).join('')
  html = html.replace(/<p><\/p>\s*/g, '')
  return html
}

// 生成章节内容
const handleGenerateContent = async ({ chapter, pageCount }) => {
  generating.value = true
  try {
    const res = await bidStore.generateContentAsync({
      projectName: bidTitle.value,
      projectType: '智慧城市',
      chapterTitle: chapter,
      chapterPath: chapter,
      pageCount: pageCount || 3,
      bidRequirements: '',
      scoringCriteria: ''
    })
    if (res.data?.content) {
      let html = markdownToHtml(res.data.content)
      const newBlock = '<div class="chapter-block" data-chapter="' + chapter + '">' +
        '<h2>' + chapter + '</h2>' + html + '</div>'
      
      // 检查是否已存在该章节的内容块
      const existingRegex = new RegExp('<div class="chapter-block" data-chapter="' + chapter.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '">[\\s\\S]*?<\\/div>')
      
      if (existingRegex.test(content.value)) {
        // 替换现有内容块
        content.value = content.value.replace(existingRegex, newBlock)
      } else {
        // 插入到正确位置 - 基于目录顺序
        const flatOutline = []
        const flattenOutline = (items) => {
          items.forEach(item => {
            flatOutline.push(item.title)
            if (item.children && item.children.length) {
              flattenOutline(item.children)
            }
          })
        }
        flattenOutline(outline.value)
        
        // 找到新章节在目录中的位置
        const chapterIndex = flatOutline.indexOf(chapter)
        
        // 找到该位置之前的最后一个章节块
        let insertPosition = content.value.length
        for (let i = chapterIndex - 1; i >= 0; i--) {
          const prevChapter = flatOutline[i]
          const prevRegex = new RegExp('<div class="chapter-block" data-chapter="' + prevChapter.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '">[\\s\\S]*?<\\/div>')
          const match = content.value.match(prevRegex)
          if (match && match.index !== undefined) {
            insertPosition = match.index + match[0].length
            break
          }
        }
        
        content.value = content.value.slice(0, insertPosition) + newBlock + content.value.slice(insertPosition)
      }
      ElMessage.success(`"${chapter}" 内容生成成功`)
    }
  } catch (error) {
    ElMessage.error('内容生成失败')
  } finally {
    generating.value = false
  }
}

const handleUpload = (file) => {
  // TODO: 处理文件上传
  console.log('上传文件:', file)
}

onMounted(async () => {
  const id = route.params.id
  if (id) {
    try {
      const res = await getBidDetail(String(id))
      if (res.data) {
        bidTitle.value = res.data.title || ''
        outline.value = res.data.outline || []
        content.value = res.data.content || ''
      }
    } catch (error) {
      console.error('加载标书失败:', error)
      console.error('Error response:', error.response)
      console.error('Error message:', error.message)
      ElMessage.error('加载标书失败: ' + (error.message || '未知错误'))
    }
  }
})
</script>

<style scoped>
.bid-editor {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 60px - 48px);
  background: var(--el-bg-color);
  border-radius: var(--card-radius);
  overflow: hidden;
}

.editor-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--el-spacing-md) var(--el-spacing-lg);
  border-bottom: 1px solid var(--el-border-color-lighter);
  background: var(--el-bg-color);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--el-spacing-md);
}

.header-left .title-input {
  width: 300px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--el-spacing-sm);
}

.editor-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.outline-panel {
  width: 280px;
  border-right: 1px solid var(--el-border-color-lighter);
  overflow-y: auto;
}

.content-panel {
  flex: 1;
  overflow-y: auto;
}

.upload-panel {
  width: 300px;
  border-left: 1px solid var(--el-border-color-lighter);
  overflow-y: auto;
}
</style>