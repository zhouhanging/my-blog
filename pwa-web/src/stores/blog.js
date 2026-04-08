import { defineStore } from 'pinia'
import { ref } from 'vue'
import { blogApi } from '@/api'

export const useBlogStore = defineStore('blog', () => {
  const currentBlog = ref(null)
  const blogList = ref([])
  const loading = ref(false)

  const generateBlog = async (topic) => {
    loading.value = true
    try {
      const res = await blogApi.generate(topic)
      currentBlog.value = res.data
      return res.data
    } finally {
      loading.value = false
    }
  }

  const fetchBlogList = async () => {
    loading.value = true
    try {
      const res = await blogApi.list()
      blogList.value = res.data
    } finally {
      loading.value = false
    }
  }

  const optimizeBlog = async (id, feedback) => {
    loading.value = true
    try {
      const res = await blogApi.optimize(id, feedback)
      currentBlog.value = res.data
      return res.data
    } finally {
      loading.value = false
    }
  }

  const approveBlog = async (id) => {
    loading.value = true
    try {
      const res = await blogApi.approve(id)
      currentBlog.value = res.data
      return res.data
    } finally {
      loading.value = false
    }
  }

  return {
    currentBlog,
    blogList,
    loading,
    generateBlog,
    fetchBlogList,
    optimizeBlog,
    approveBlog
  }
})
