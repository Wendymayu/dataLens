import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { databaseApi, configApi } from '@/services/api'
import type { DatabaseInfo, DatabaseCreateRequest, ProviderInfo, ConfigResponse } from '@/types/database'

export const useDatabaseStore = defineStore('database', () => {
  const databases = ref<DatabaseInfo[]>([])
  const providers = ref<ProviderInfo[]>([])
  const config = ref<ConfigResponse | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const currentDatabase = computed(() => databases.value.find(db => db.is_current))
  const hasDatabase = computed(() => databases.value.length > 0)

  async function loadDatabases() {
    try {
      databases.value = await databaseApi.list()
    } catch (e: any) {
      console.error('Failed to load databases:', e)
    }
  }

  async function loadConfig() {
    try {
      config.value = await configApi.get()
    } catch (e: any) {
      console.error('Failed to load config:', e)
    }
  }

  async function loadProviders() {
    try {
      providers.value = await configApi.getProviders()
    } catch (e: any) {
      console.error('Failed to load providers:', e)
    }
  }

  async function addDatabase(data: DatabaseCreateRequest) {
    loading.value = true
    error.value = null

    try {
      await databaseApi.add(data)
      await loadDatabases()
      return true
    } catch (e: any) {
      error.value = e.response?.data?.detail || e.message
      return false
    } finally {
      loading.value = false
    }
  }

  async function removeDatabase(name: string) {
    try {
      await databaseApi.remove(name)
      await loadDatabases()
    } catch (e: any) {
      error.value = e.message
    }
  }

  async function setCurrentDatabase(name: string) {
    try {
      await databaseApi.setCurrent(name)
      await loadDatabases()
    } catch (e: any) {
      error.value = e.message
    }
  }

  async function testConnection(name: string) {
    try {
      const result = await databaseApi.test(name)
      return result
    } catch (e: any) {
      return { status: 'error', message: e.message }
    }
  }

  async function updateModelConfig(data: any) {
    loading.value = true
    error.value = null

    try {
      await configApi.updateModel(data)
      await loadConfig()
      return true
    } catch (e: any) {
      error.value = e.response?.data?.detail || e.message
      return false
    } finally {
      loading.value = false
    }
  }

  async function init() {
    await loadDatabases()
    await loadConfig()
    await loadProviders()
  }

  return {
    databases,
    providers,
    config,
    loading,
    error,
    currentDatabase,
    hasDatabase,
    loadDatabases,
    loadConfig,
    loadProviders,
    addDatabase,
    removeDatabase,
    setCurrentDatabase,
    testConnection,
    updateModelConfig,
    init
  }
})