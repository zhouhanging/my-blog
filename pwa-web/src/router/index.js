import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Generate',
    component: () => import('@/views/GenerateView.vue')
  },
  {
    path: '/blogs',
    name: 'BlogList',
    component: () => import('@/views/BlogListView.vue')
  },
  {
    path: '/blogs/:id',
    name: 'BlogDetail',
    component: () => import('@/views/BlogDetailView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
