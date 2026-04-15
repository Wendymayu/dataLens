<script setup lang="ts">
import { Icon } from '@iconify/vue'
import type { DatabaseInfo } from '@/types/database'

defineProps<{
  currentDb?: DatabaseInfo
  sidebarCollapsed?: boolean
  databases?: DatabaseInfo[]
}>()

const emit = defineEmits<{
  openSettings: []
  toggleSidebar: []
  setDb: [name: string]
}>()
</script>

<template>
  <header class="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
    <div class="flex items-center gap-3">
      <button
        @click="emit('toggleSidebar')"
        class="p-2 hover:bg-gray-100 rounded-lg"
        :title="sidebarCollapsed ? '展开侧边栏' : '折叠侧边栏'"
      >
        <Icon :icon="sidebarCollapsed ? 'lucide:panel-right' : 'lucide:panel-left'" class="w-5 h-5 text-gray-600" />
      </button>

      <!-- Database Selector -->
      <select
        :value="currentDb?.name || ''"
        @change="emit('setDb', $event.target.value)"
        class="text-sm border border-gray-200 rounded px-2 py-1 bg-white"
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
    </div>

    <button
      @click="emit('openSettings')"
      class="p-2 hover:bg-gray-100 rounded-lg"
    >
      <Icon icon="lucide:settings" class="w-5 h-5 text-gray-600" />
    </button>
  </header>
</template>