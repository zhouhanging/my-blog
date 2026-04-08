<template>
  <div style="max-width: 900px; margin: 0 auto">
    <n-page-header title="AI 生成博客" subtitle="输入主题，AI 帮你写" />
    
    <n-card style="margin-top: 24px">
      <n-form :model="form">
        <n-form-item label="博客主题">
          <n-input
            v-model:value="form.topic"
            placeholder="例如：Vue3 组合式 API 最佳实践、Docker 部署 FastAPI 完整指南"
            size="large"
          />
        </n-form-item>
        <n-form-item>
          <n-button
            type="primary"
            size="large"
            @click="handleGenerate"
            :loading="store.loading"
          >
            <template #icon>
              <n-icon><SparklesOutline /></n-icon>
            </template>
            生成博客
          </n-button>
        </n-form-item>
      </n-form>
    </n-card>

    <n-card v-if="store.currentBlog" title="生成结果" style="margin-top: 24px">
      <n-tabs type="line">
        <n-tab-pane name="preview" tab="预览">
          <div class="markdown-preview" v-html="renderedMarkdown"></div>
        </n-tab-pane>
        <n-tab-pane name="raw" tab="原始 Markdown">
          <n-input
            type="textarea"
            :value="store.currentBlog.content"
            readonly
            style="min-height: 400px"
          />
        </n-tab-pane>
      </n-tabs>

      <n-space style="margin-top: 24px; justify-content: flex-end">
        <n-button @click="showFeedbackModal = true">
          <template #icon>
            <n-icon><CreateOutline /></n-icon>
          </template>
          提修改意见
        </n-button>
        <n-button type="success" @click="handleApprove" :loading="store.loading">
          <template #icon>
            <n-icon><CheckmarkOutline /></n-icon>
          </template>
          审核通过
        </n-button>
      </n-space>
    </n-card>

    <n-modal v-model:show="showFeedbackModal" preset="card" title="提修改意见" style="width: 600px">
      <n-form :model="feedbackForm">
        <n-form-item label="修改意见">
          <n-input
            type="textarea"
            v-model:value="feedbackForm.feedback"
            placeholder="例如：这里加个代码示例、语言更口语化一点、增加最新的 2024 年数据"
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
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useBlogStore } from '@/stores/blog'
import { SparklesOutline, CreateOutline, CheckmarkOutline } from '@vicons/ionicons5'
import { marked } from 'marked'
import { useMessage } from 'naive-ui'
import api from '@/api'

const router = useRouter()
const store = useBlogStore()
const message = useMessage()

const form = ref({ topic: '' })
const feedbackForm = ref({ feedback: '' })
const showFeedbackModal = ref(false)

const renderedMarkdown = computed(() => {
  if (!store.currentBlog) return ''
  return marked.parse(store.currentBlog.content)
})

const handleGenerate = async () => {
  if (!form.value.topic.trim()) {
    message.warning('请输入博客主题')
    return
  }
  try {
    await store.generateBlog(form.value.topic)
    message.success('生成成功！')
  } catch (error) {
    message.error('生成失败：' + error.message)
  }
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
