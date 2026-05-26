/**
 * 分页组合式函数
 */
import { ref, computed } from 'vue'

export function usePagination(options = {}) {
  const {
    immediate = true,
    onLoad = null
  } = options

  const page = ref(1)
  const pageSize = ref(options.pageSize || 10)
  const total = ref(0)
  const loading = ref(false)

  const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

  const handlePageChange = async (newPage) => {
    page.value = newPage
    if (onLoad) {
      await loadData()
    }
  }

  const handleSizeChange = async (newSize) => {
    pageSize.value = newSize
    page.value = 1
    if (onLoad) {
      await loadData()
    }
  }

  const loadData = async () => {
    if (!onLoad) return
    loading.value = true
    try {
      const result = await onLoad({
        page: page.value,
        pageSize: pageSize.value
      })
      if (result) {
        total.value = result.total || 0
      }
    } finally {
      loading.value = false
    }
  }

  const resetPagination = () => {
    page.value = 1
    total.value = 0
  }

  if (immediate) {
    loadData()
  }

  return {
    page,
    pageSize,
    total,
    totalPages,
    loading,
    handlePageChange,
    handleSizeChange,
    loadData,
    resetPagination
  }
}