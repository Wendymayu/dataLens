// Menu type for conversation categorization
export type MenuType = 'smart-query' | 'adhoc-query' | 'alert'

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
  menu_type?: MenuType  // 所属菜单类型
}

export interface ConversationListItem {
  id: string
  title: string
  created_at: string
  updated_at: string
  message_count: number
  menu_type?: MenuType  // 所属菜单类型
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