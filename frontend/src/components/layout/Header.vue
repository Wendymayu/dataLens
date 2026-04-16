<script setup lang="ts">
import { Icon } from '@iconify/vue'
import type { DatabaseInfo } from '@/types/database'

defineProps<{
  currentDb?: DatabaseInfo
  databases?: DatabaseInfo[]
}>()

const emit = defineEmits<{
  openSettings: []
  setDb: [name: string]
}>()
</script>

<template>
  <header class="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
    <div class="flex items-center gap-3">
      <!-- Database Selector -->
      <select
        :value="currentDb?.name || ''"
        @change="emit('setDb', $event.target.value)"
        class="text-sm border border-gray-200 rounded-lg px-3 py-1.5 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        :disabled="!databases || databases.length === 0"
      >
        <option value="" disabled>选择数据库</option>
        <option
          v-for="db in databases"
          :key="db.name"
          :value="db.name"
        >
          {{ db.name }} ({{ db.database }})
        </option>
      </select>

      <!-- Connection Status -->
      <div v-if="currentDb" class="flex items-center gap-1.5 text-xs text-gray-500">
        <span class="w-2 h-2 bg-green-500 rounded-full"></span>
        已连接
      </div>
    </div>

    <button
      @click="emit('openSettings')"
      class="p-2 hover:bg-gray-100 rounded-lg transition-colors"
      title="设置"
    >
      <Icon icon="lucide:settings" class="w-5 h-5 text-gray-600" />
    </button>
  </header>
</template>
