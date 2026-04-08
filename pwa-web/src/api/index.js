import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 60000
})

export const blogApi = {
  generate: (topic) => api.post('/blogs/generate', { topic }),
  
  get: (id) => api.get(`/blogs/${id}`),
  
  list: (params) => api.get('/blogs', { params }),
  
  optimize: (id, feedback) => api.post(`/blogs/${id}/optimize`, { blog_id: id, feedback }),
  
  approve: (id) => api.post(`/blogs/${id}/approve`)
}

export default api
