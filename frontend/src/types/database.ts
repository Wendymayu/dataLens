// Database related types
export interface DatabaseInfo {
  name: string
  host: string
  port: number
  user: string
  database: string
  is_current: boolean
  connection_status?: string
}

export interface DatabaseCreateRequest {
  name: string
  host: string
  port: number
  user: string
  password: string
  database: string
}

export interface ProviderInfo {
  id: string
  name: string
  description: string
  default_model: string
  supports_base_url: boolean
}

export interface ModelConfig {
  provider: string
  model_name: string
  api_key: string
  base_url?: string
  temperature: number
  max_tokens: number
}

export interface ConfigResponse {
  provider: string
  model_name: string
  api_key_masked: string
  base_url?: string
  temperature: number
  max_tokens: number
  current_database?: string
}