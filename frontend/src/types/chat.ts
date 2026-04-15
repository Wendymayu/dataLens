// Chat related types
export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  sql?: string
  created_at: string
  duration?: number  // 耗时（秒）
}

export interface Conversation {
  id: string
  title: string
  database?: string
  created_at: string
  updated_at: string
  messages: Message[]
}

export interface ConversationListItem {
  id: string
  title: string
  created_at: string
  updated_at: string
  message_count: number
}

export interface ChatRequest {
  query: string
  conversation_id?: string
  database?: string
}

export interface ChatResponse {
  response: string
  sql?: string
  conversation_id: string
  message_id: string
  created_at: string
  duration?: number  // 耗时（秒）
}