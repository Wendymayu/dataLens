import axios from 'axios'
import type { ChatRequest, ChatResponse } from '@/types/chat'

const api = axios.create({
  baseURL: '/api',
  timeout: 60000,
})

export default api

// Chat API
export const chatApi = {
  async sendQuery(request: ChatRequest): Promise<ChatResponse> {
    const response = await api.post('/chat', request)
    return response.data
  }
}

// Database API
export const databaseApi = {
  async list(): Promise<any[]> {
    const response = await api.get('/databases')
    return response.data
  },

  async add(data: any): Promise<any> {
    const response = await api.post('/databases', data)
    return response.data
  },

  async remove(name: string): Promise<void> {
    await api.delete(`/databases/${name}`)
  },

  async setCurrent(name: string): Promise<void> {
    await api.put(`/databases/${name}/current`)
  },

  async test(name: string): Promise<any> {
    const response = await api.post(`/databases/${name}/test`)
    return response.data
  },

  async getSchema(name: string): Promise<any> {
    const response = await api.get(`/databases/${name}/schema`)
    return response.data
  }
}

// Config API
export const configApi = {
  async get(): Promise<any> {
    const response = await api.get('/config')
    return response.data
  },

  async updateModel(data: any): Promise<void> {
    await api.put('/config/model', data)
  },

  async getProviders(): Promise<any[]> {
    const response = await api.get('/config/providers')
    return response.data
  }
}

// Conversation API
export const conversationApi = {
  async list(): Promise<any[]> {
    const response = await api.get('/conversations')
    return response.data
  },

  async create(menuType?: string, title?: string): Promise<any> {
    const response = await api.post('/conversations', {
      title,
      menu_type: menuType || 'smart-query'
    })
    return response.data
  },

  async get(id: string): Promise<any> {
    const response = await api.get(`/conversations/${id}`)
    return response.data
  },

  async delete(id: string): Promise<void> {
    await api.delete(`/conversations/${id}`)
  },

  async updateTitle(id: string, title: string): Promise<void> {
    await api.patch(`/conversations/${id}/title`, { title })
  }
}