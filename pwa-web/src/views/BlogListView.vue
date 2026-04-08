<template>
  <div style="max-width: 1000px; margin: 0 auto">
    <n-page-header title="博客列表">
      <template #extra>
        <n-button type="primary" @click="$router.push('/')">
          <template #icon>
            <n-icon><AddOutline /></n-icon>
          </template>
          生成新博客
        </n-button>
      </template>
    </n-page-header>

    <n-card style="margin-top: 24px">
      <n-spin :show="store.loading">
        <n-list>
          <n-list-item v-for="blog in store.blogList" :key="blog.id" clickable @click="$router.push(`/blogs/${blog.id}`)">
            <n-thing>
              <template #header>
                <n-text depth="3" style="margin-right: 12px">{{ formatDate(blog.created_at) }}</n-text>
                <n-tag :type="getStatusType(blog.status)">{{ getStatusText(blog.status) }}</n-tag>
              </template>
              <template #header-extra>
                <n-icon><ChevronForwardOutline /></n-icon>
              </template>
              <template #title>{{ blog.topic }}</template>
              <template #description>{{ truncateContent(blog.content) }}</template>
            </n-thing>
          </n-list-item>
        </n-list>
        <n-empty v-if="store.blogList.length === 0 && !store.loading" description="暂无博客，去生成一篇吧！" />
      </n-spin>
    </n-card>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useBlogStore } from '@/stores/blog'
import { AddOutline, ChevronForwardOutline } from '@vicons/ionicons5'

const store = useBlogStore()

onMounted(() => {
  store.fetchBlogList()
})

const formatDate = (dateStr) => {
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

const truncateContent = (content) => {
  return content.replace(/[#*`]/g, '').substring(0, 100) + '...'
}
</script>
