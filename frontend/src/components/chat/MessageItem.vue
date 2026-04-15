<script setup lang="ts">
import { computed, onMounted, nextTick, watch } from 'vue'
import { Icon } from '@iconify/vue'
import { renderMarkdown, initCopyButtons } from '@/utils/markdown'
import type { Message } from '@/types/chat'

const props = defineProps<{
  message: Message
}>()

const renderedContent = computed(() => {
  let content = props.message.content

  // 如果是 AI 消息，将 SQL 代码块移到最后
  if (props.message.role === 'assistant') {
    // 提取所有 SQL 代码块
    const sqlBlocks: string[] = []
    content = content.replace(/```sql\s*([\s\S]*?)```/gi, (match) => {
      sqlBlocks.push(match)
      return '' // 先移除
    })

    // 将 SQL 代码块添加到末尾
    if (sqlBlocks.length > 0) {
      content = content.trim() + '\n\n' + sqlBlocks.join('\n\n')
    }
  }

  return renderMarkdown(content)
})

const isUser = computed(() => props.message.role === 'user')

// 格式化耗时显示
function formatDuration(seconds: number): string {
  if (seconds < 1) {
    return `${(seconds * 1000).toFixed(0)}ms`
  }
  return `${seconds.toFixed(2)}s`
}

// 每次消息更新后初始化复制按钮
watch(() => props.message.content, async () => {
  await nextTick()
  initCopyButtons()
})

onMounted(() => {
  initCopyButtons()
})
</script>

<template>
  <div
    :class="[
      'flex gap-3 items-start',
      isUser ? 'flex-row-reverse ml-auto' : 'mr-auto',
      'max-w-[85%]'
    ]"
  >
    <!-- Avatar -->
    <div
      :class="[
        'w-8 h-8 rounded-full flex items-center justify-center text-white shrink-0 mt-1',
        isUser ? 'bg-blue-500' : 'bg-green-500'
      ]"
    >
      <Icon :icon="isUser ? 'lucide:user' : 'lucide:bot'" class="w-4 h-4" />
    </div>

    <!-- Content -->
    <div
      :class="[
        'flex-1 min-w-0 p-4 rounded-lg',
        isUser ? 'bg-blue-50' : 'bg-gray-50'
      ]"
    >
      <div
        class="prose prose-sm max-w-none"
        v-html="renderedContent"
      />

      <!-- Duration for AI messages -->
      <div v-if="!isUser && message.duration" class="text-xs text-gray-400 mt-2">
        耗时: {{ formatDuration(message.duration) }}
      </div>
    </div>
  </div>
</template>