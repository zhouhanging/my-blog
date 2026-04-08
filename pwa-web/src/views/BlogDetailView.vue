<template>
  <div style="max-width: 900px; margin: 0 auto">
    <n-page-header @back-click="$router.back()">
      <template #header>
        <n-breadcrumb>
          <n-breadcrumb-item @click="$router.push('/blogs')">博客列表</n-breadcrumb-item>
          <n-breadcrumb-item>详情</n-breadcrumb-item>
        </n-breadcrumb>
      </template>
      <template #avatar>
        <n-avatar round>
          <template #icon>
            <n-icon><DocumentTextOutline /></n-icon>
          </template>
        </n-avatar>
      </template>
      <template #title>{{ blog?.topic }}</template>
      <template #subtitle>
        <n-text depth="3">{{ formatDate(blog?.created_at) }}</n-text>
        <n-tag :type="getStatusType(blog?.status)" style="margin-left: 12px">{{ getStatusText(blog?.status) }}</n-tag>
      </template>
      <template #extra>
        <n-space>
          <n-button v-if="blog?.status === 'pending'" @click="showFeedbackModal = true">
            提修改意见
          </n-button>
          <n-button v-if="blog?.status === 'pending'" type="success" @click="handleApprove" :loading="store.loading">
            审核通过
          </n-button>
        </n-space>
      </template>
    </n-page-header>

    <n-card style="margin-top: 24px">
      <div class="markdown-preview" v-html="renderedMarkdown"></div>
    </n-card>

    <n-modal v-model:show="showFeedbackModal" preset="card" title="提修改意见" style="width: 600px">
      <n-form :model="feedbackForm">
        <n-form-item label="修改意见">
          <n-input
            type="textarea"
            v-model:value="feedbackForm.feedback"
            placeholder="例如：这里加个代码示例、语言更口语化一点"
            style="min-height: 150px"
          />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showFeedbackModal = false">取消</n-button>
          <n-button type="primary" @click="handleOptimize" :loading="store.loading">
            提交优化
          </n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useBlogStore } from '@/stores/blog'
import { DocumentTextOutline } from '@vicons/ionicons5'
import { marked } from 'marked'
import { useMessage } from 'naive-ui'
import api from '@/api'

const route = useRoute()
const router = useRouter()
const store = useBlogStore()
const message = useMessage()

const blog = computed(() => store.currentBlog)
const showFeedbackModal = ref(false)
const feedbackForm = ref({ feedback: '' })

const renderedMarkdown = computed(() => {
  if (!blog.value) return ''
  return marked.parse(blog.value.content)
})

onMounted(async () => {
  const id = parseInt(route.params.id)
  const existing = store.blogList.find(b => b.id === id)
  if (existing) {
    store.currentBlog = existing
  } else {
    try {
      const res = await api.blogApi.get(id)
      store.currentBlog = res.data
    } catch (error) {
      message.error('获取博客失败')
      router.push('/blogs')
    }
  }
})

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString('zh-CN')
}

const getStatusType = (status) => {
  const map = {
    draft: 'default',
    pending: 'warning',
    approved: 'info',
    published: 'success'
  }
  return map[status] || 'default'
}

const getStatusText = (status) => {
  const map = {
    draft: '草稿',
    pending: '待审核',
    approved: '已审核',
    published: '已发布'
  }
  return map[status] || status
}

const handleOptimize = async () => {
  if (!feedbackForm.value.feedback.trim()) {
    message.warning('请输入修改意见')
    return
  }
  try {
    await store.optimizeBlog(store.currentBlog.id, feedbackForm.value.feedback)
    showFeedbackModal.value = false
    feedbackForm.value.feedback = ''
    message.success('优化成功！')
  } catch (error) {
    message.error('优化失败：' + error.message)
  }
}

const handleApprove = async () => {
  try {
    await store.approveBlog(store.currentBlog.id)
    message.success('审核通过！已推送到博客和公众号')
    router.push('/blogs')
  } catch (error) {
    message.error('审核失败：' + error.message)
  }
}
</script>

<style scoped>
.markdown-preview {
  line-height: 1.8;
}
.markdown-preview h1 { font-size: 2em; margin: 0.67em 0; }
.markdown-preview h2 { font-size: 1.5em; margin: 0.83em 0; }
.markdown-preview h3 { font-size: 1.17em; margin: 1em 0; }
.markdown-preview p { margin: 1em 0; }
.markdown-preview code { background: #f5f5f5; padding: 2px 6px; border-radius: 4px; }
.markdown-preview pre { background: #2d2d2d; color: #f8f8f2; padding: 16px; border-radius: 8px; overflow-x: auto; }
.markdown-preview pre code { background: none; padding: 0; }
</style>
