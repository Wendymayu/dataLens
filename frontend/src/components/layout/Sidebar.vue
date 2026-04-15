<script setup lang="ts">
import { computed } from 'vue'
import { Icon } from '@iconify/vue'

const props = defineProps<{
  collapsed: boolean
}>()

const emit = defineEmits<{
  newChat: []
  select: [id: string]
  delete: [id: string]
}>()

import { useChatStore } from '@/stores/chatStore'
const chatStore = useChatStore()

const conversations = computed(() => chatStore.conversations)
const currentId = computed(() => chatStore.currentConversation?.id)

function formatDate(dateStr: string) {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (days === 0) {
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  } else if (days === 1) {
    return '昨天'
  } else if (days < 7) {
    return `${days}天前`
  } else {
    return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
  }
}
</script>

<template>
  <aside
    :class="[
      'bg-white border-r border-gray-200 flex flex-col transition-all duration-300',
      collapsed ? 'w-0 overflow-hidden border-0' : 'w-64'
    ]"
  >
    <!-- Header -->
    <div v-if="!collapsed" class="p-3 flex items-center justify-between border-b border-gray-200">
      <span class="font-semibold text-gray-700">DataLens</span>
    </div>

    <!-- New Chat Button -->
    <div v-if="!collapsed" class="p-3">
      <button
        @click="emit('newChat')"
        class="w-full py-2 px-4 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 flex items-center justify-center gap-2 transition-colors"
      >
        <Icon icon="lucide:plus" class="w-4 h-4" />
        新对话
      </button>
    </div>

    <!-- Conversation List -->
    <div v-if="!collapsed" class="flex-1 overflow-y-auto">
      <div
        v-for="conv in conversations"
        :key="conv.id"
        @click="emit('select', conv.id)"
        :class="[
          'px-4 py-3 cursor-pointer border-l-2 transition-colors group',
          conv.id === currentId
            ? 'bg-blue-50 border-blue-500'
            : 'hover:bg-gray-50 border-transparent'
        ]"
      >
        <div class="flex items-start justify-between">
          <p class="text-sm font-medium text-gray-700 truncate flex-1">
            {{ conv.title }}
          </p>
          <button
            @click.stop="emit('delete', conv.id)"
            class="opacity-0 group-hover:opacity-100 p-1 hover:bg-gray-200 rounded"
          >
            <Icon icon="lucide:trash-2" class="w-3 h-3 text-gray-400" />
          </button>
        </div>
        <p class="text-xs text-gray-500 mt-1">
          {{ formatDate(conv.updated_at) }} · {{ conv.message_count }}条消息
        </p>
      </div>

      <!-- Empty state -->
      <div v-if="conversations.length === 0" class="p-4 text-center text-gray-500 text-sm">
        暂无对话历史
      </div>
    </div>
  </aside>
</template>