import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  const isCollapse = ref(false)
  const activeMenu = ref('')
  const loading = ref(false)

  const setCollapse = (val) => { isCollapse.value = val }
  const setActiveMenu = (val) => { activeMenu.value = val }
  const setLoading = (val) => { loading.value = val }

  return {
    isCollapse,
    activeMenu,
    loading,
    setCollapse,
    setActiveMenu,
    setLoading
  }
})