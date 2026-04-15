<script setup lang="ts">
import { ref, computed } from 'vue'
import { Icon } from '@iconify/vue'
import type { ProviderInfo, ConfigResponse } from '@/types/database'

const props = defineProps<{
  providers: ProviderInfo[]
  config: ConfigResponse | null
}>()

const emit = defineEmits<{
  update: [data: any]
}>()

const selectedProvider = ref(props.config?.provider || '')
const modelForm = ref({
  provider: props.config?.provider || '',
  model_name: props.config?.model_name || '',
  api_key: '',
  base_url: props.config?.base_url || '',
  temperature: props.config?.temperature || 0.7,
  max_tokens: props.config?.max_tokens || 4096
})

const currentProvider = computed(() => {
  return props.providers.find(p => p.id === selectedProvider.value)
})

function selectProvider(provider: ProviderInfo) {
  selectedProvider.value = provider.id
  modelForm.value.provider = provider.id
  modelForm.value.model_name = provider.default_model
}

function handleSubmit() {
  emit('update', { ...modelForm.value })
}
</script>

<template>
  <div class="space-y-4">
    <!-- Current Config -->
    <div v-if="config" class="bg-gray-50 rounded-lg p-4">
      <h4 class="font-medium text-gray-800 mb-2">当前配置</h4>
      <div class="text-sm text-gray-600 space-y-1">
        <p>提供商: {{ config.provider }}</p>
        <p>模型: {{ config.model_name }}</p>
        <p>API Key: {{ config.api_key_masked }}</p>
        <p v-if="config.base_url">Base URL: {{ config.base_url }}</p>
      </div>
    </div>

    <!-- Provider Selection -->
    <div>
      <h4 class="font-medium text-gray-800 mb-2">选择提供商</h4>
      <div class="grid grid-cols-2 gap-2">
        <button
          v-for="provider in providers"
          :key="provider.id"
          @click="selectProvider(provider)"
          :class="[
            'p-3 rounded-lg border text-left',
            selectedProvider === provider.id
              ? 'bg-blue-50 border-blue-200'
              : 'bg-white border-gray-200 hover:bg-gray-50'
          ]"
        >
          <p class="font-medium text-sm">{{ provider.name }}</p>
          <p class="text-xs text-gray-500 mt-1">{{ provider.default_model }}</p>
        </button>
      </div>
    </div>

    <!-- Model Form -->
    <div v-if="selectedProvider" class="space-y-3">
      <div>
        <label class="text-xs text-gray-500 mb-1 block">模型名称</label>
        <input
          v-model="modelForm.model_name"
          type="text"
          class="w-full text-sm border rounded px-2 py-1"
        />
      </div>

      <div v-if="currentProvider?.supports_base_url">
        <label class="text-xs text-gray-500 mb-1 block">Base URL</label>
        <input
          v-model="modelForm.base_url"
          type="text"
          placeholder="https://api.example.com/v1"
          class="w-full text-sm border rounded px-2 py-1"
        />
      </div>

      <div>
        <label class="text-xs text-gray-500 mb-1 block">API Key *</label>
        <input
          v-model="modelForm.api_key"
          type="password"
          placeholder="sk-xxx"
          class="w-full text-sm border rounded px-2 py-1"
        />
      </div>

      <div class="grid grid-cols-2 gap-2">
        <div>
          <label class="text-xs text-gray-500 mb-1 block">Temperature</label>
          <input
            v-model.number="modelForm.temperature"
            type="number"
            step="0.1"
            min="0"
            max="1"
            class="w-full text-sm border rounded px-2 py-1"
          />
        </div>
        <div>
          <label class="text-xs text-gray-500 mb-1 block">Max Tokens</label>
          <input
            v-model.number="modelForm.max_tokens"
            type="number"
            class="w-full text-sm border rounded px-2 py-1"
          />
        </div>
      </div>

      <button
        @click="handleSubmit"
        class="w-full py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
      >
        更新配置
      </button>
    </div>
  </div>
</template>