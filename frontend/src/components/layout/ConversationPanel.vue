<script setup lang="ts">
import { computed } from 'vue'
import { Icon } from '@iconify/vue'
import { useAppStore } from '@/stores/appStore'
import { useChatStore } from '@/stores/chatStore'

const appStore = useAppStore()
const chatStore = useChatStore()

const conversations = computed(() => chatStore.filteredConversations)
const currentId = computed(() => chatStore.currentConversation?.id)
const collapsed = computed(() => appStore.rightPanelCollapsed)
const hasConversations = computed(() => appStore.hasConversations)

const emit = defineEmits<{
  newChat: []
  select: [id: string]
  delete: [id: string]
}>()

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

function togglePanel() {
  appStore.toggleRightPanel()
}
</script>

<template>
  <aside
    v-if="hasConversations"
    :class="[
      'bg-white border-l border-gray-200 flex flex-col transition-all duration-300',
      collapsed ? 'w-12' : 'w-64'
    ]"
  >
    <!-- Header -->
    <div class="h-14 px-3 flex items-center justify-between border-b border-gray-200">
      <span v-if="!collapsed" class="font-semibold text-gray-700 text-sm">会话记录</span>
      <button
        @click="togglePanel"
        class="p-1.5 hover:bg-gray-100 rounded-lg"
        :title="collapsed ? '展开' : '折叠'"
      >
        <Icon
          :icon="collapsed ? 'lucide:chevron-left' : 'lucide:chevron-right'"
          class="w-4 h-4 text-gray-500"
        />
      </button>
    </div>

    <!-- New Chat Button -->
    <div v-if="!collapsed" class="p-3">
      <button
        @click="emit('newChat')"
        class="w-full py-2 px-4 bg-blue-500 text-white rounded-lg hover:bg-blue-600 flex items-center justify-center gap-2 transition-colors text-sm"
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
          'px-3 py-3 cursor-pointer border-l-2 transition-colors group',
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
        <Icon icon="lucide:message-square-off" class="w-8 h-8 mx-auto mb-2 text-gray-300" />
        <p>暂无对话</p>
        <p class="text-xs mt-1">点击上方按钮开始新对话</p>
      </div>
    </div>

    <!-- Collapsed state - show icon only -->
    <div v-if="collapsed" class="flex-1 flex flex-col items-center py-4">
      <button
        @click="emit('newChat')"
        class="p-2 hover:bg-gray-100 rounded-lg mb-2"
        title="新对话"
      >
        <Icon icon="lucide:plus" class="w-5 h-5 text-gray-500" />
      </button>
      <div class="text-xs text-gray-400 writing-vertical">
        {{ conversations.length }} 条会话
      </div>
    </div>
  </aside>
</template>

<style scoped>
.writing-vertical {
  writing-mode: vertical-rl;
  text-orientation: mixed;
}
</style>
