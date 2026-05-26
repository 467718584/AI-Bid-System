import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getProjectList, getProjectDetail, createProject, updateProject, deleteProject } from '@/api/project'

export const useProjectStore = defineStore('project', () => {
  const projectList = ref([])
  const currentProject = ref(null)
  const total = ref(0)

  const fetchProjectList = async (params) => {
    const res = await getProjectList(params)
    projectList.value = res.data.list
    total.value = res.data.total
    return res
  }

  const fetchProjectDetail = async (id) => {
    const res = await getProjectDetail(id)
    currentProject.value = res.data
    return res
  }

  const create = async (data) => {
    const res = await createProject(data)
    projectList.value.unshift(res.data)
    total.value++
    return res
  }

  const update = async (id, data) => {
    const res = await updateProject(id, data)
    const index = projectList.value.findIndex(item => item.id === id)
    if (index !== -1) {
      projectList.value[index] = res.data
    }
    return res
  }

  const remove = async (id) => {
    await deleteProject(id)
    projectList.value = projectList.value.filter(item => item.id !== id)
    total.value--
  }

  return {
    projectList,
    currentProject,
    total,
    fetchProjectList,
    fetchProjectDetail,
    create,
    update,
    remove
  }
})