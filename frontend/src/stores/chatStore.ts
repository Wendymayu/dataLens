import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { chatApi, conversationApi } from '@/services/api'
import type { Message, Conversation, ConversationListItem, ChatResponse } from '@/types/chat'

export const useChatStore = defineStore('chat', () => {
  const conversations = ref<ConversationListItem[]>([])
  const currentConversation = ref<Conversation | null>(null)
  const messages = ref<Message[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const currentTitle = computed(() => currentConversation.value?.title || 'New Chat')

  async function loadConversations() {
    try {
      conversations.value = await conversationApi.list()
    } catch (e: any) {
      console.error('Failed to load conversations:', e)
    }
  }

  async function loadConversation(id: string) {
    try {
      currentConversation.value = await conversationApi.get(id)
      messages.value = currentConversation.value.messages
    } catch (e: any) {
      error.value = e.message
    }
  }

  async function createConversation() {
    try {
      const conv = await conversationApi.create()
      currentConversation.value = conv
      messages.value = []
      await loadConversations()
      return conv.id
    } catch (e: any) {
      error.value = e.message
      return null
    }
  }

  async function sendMessage(content: string, database?: string) {
    if (!content.trim() || loading.value) return

    loading.value = true
    error.value = null

    // Add user message to UI immediately
    const userMessage: Message = {
      id: 'temp-' + Date.now(),
      role: 'user',
      content,
      created_at: new Date().toISOString()
    }
    messages.value.push(userMessage)

    try {
      const response: ChatResponse = await chatApi.sendQuery({
        query: content,
        conversation_id: currentConversation.value?.id,
        database
      })

      // Replace temp message with real one and add assistant message
      messages.value = messages.value.filter(m => !m.id.startsWith('temp-'))
      messages.value.push({
        id: response.message_id,
        role: 'assistant',
        content: response.response,
        sql: response.sql,
        created_at: response.created_at,
        duration: response.duration
      })

      // Update conversation if new
      if (!currentConversation.value) {
        await loadConversation(response.conversation_id)
      } else if (currentConversation.value.id === response.conversation_id) {
        // Refresh to get updated title
        await loadConversation(response.conversation_id)
      }

      await loadConversations()
    } catch (e: any) {
      // Remove temp message on error
      messages.value = messages.value.filter(m => !m.id.startsWith('temp-'))
      error.value = e.response?.data?.detail || e.message
    } finally {
      loading.value = false
    }
  }

  async function deleteConversation(id: string) {
    try {
      await conversationApi.delete(id)
      if (currentConversation.value?.id === id) {
        currentConversation.value = null
        messages.value = []
      }
      await loadConversations()
    } catch (e: any) {
      error.value = e.message
    }
  }

  function clearCurrentConversation() {
    currentConversation.value = null
    messages.value = []
  }

  return {
    conversations,
    currentConversation,
    messages,
    loading,
    error,
    currentTitle,
    loadConversations,
    loadConversation,
    createConversation,
    sendMessage,
    deleteConversation,
    clearCurrentConversation
  }
})