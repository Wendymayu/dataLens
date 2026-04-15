<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { Icon } from '@iconify/vue'
import MessageItem from './MessageItem.vue'
import type { Message } from '@/types/chat'
import type { DatabaseInfo } from '@/types/database'

const props = defineProps<{
  messages: Message[]
  loading: boolean
  error?: string | null
  databases: DatabaseInfo[]
  currentDb?: string
}>()

const emit = defineEmits<{
  send: [content: string, db?: string]
}>()

const inputText = ref('')
const messagesContainer = ref<HTMLElement | null>(null)

// Scroll to bottom when messages change
watch(() => props.messages.length, async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
})

function sendMessage() {
  if (!inputText.value.trim() || props.loading) return

  emit('send', inputText.value.trim(), props.currentDb)
  inputText.value = ''
}
</script>

<template>
  <div class="flex-1 flex flex-col overflow-hidden">
    <!-- Empty State - Input in center -->
    <div
      v-if="messages.length === 0"
      class="flex-1 flex flex-col items-center justify-center p-4"
    >
      <div class="w-full max-w-4xl">
        <!-- Input with button inside -->
        <div class="relative">
          <textarea
            v-model="inputText"
            @keydown.enter.exact.prevent="sendMessage"
            placeholder="输入您的问题，例如：有多少用户？"
            rows="1"
            class="w-full resize-none border border-gray-200 rounded-lg px-4 py-3 pr-12 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            :disabled="loading || databases.length === 0"
          />
          <button
            @click="sendMessage"
            :disabled="!inputText.trim() || loading || databases.length === 0"
            class="absolute right-2 bottom-2 p-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Icon v-if="!loading" icon="lucide:send" class="w-5 h-5" />
            <Icon v-else icon="lucide:loader-2" class="w-5 h-5 animate-spin" />
          </button>
        </div>
      </div>
    </div>

    <!-- Messages Area - When has messages -->
    <template v-else>
      <div
        ref="messagesContainer"
        class="flex-1 overflow-y-auto p-4"
      >
        <!-- Messages -->
        <div class="max-w-4xl mx-auto space-y-4">
          <MessageItem
            v-for="msg in messages"
            :key="msg.id"
            :message="msg"
          />

          <!-- Loading Indicator -->
          <div v-if="loading" class="flex items-center gap-2 p-4">
            <div class="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
              <Icon icon="lucide:bot" class="w-4 h-4 text-white" />
            </div>
            <div class="flex gap-1">
              <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0ms"></span>
              <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 150ms"></span>
              <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 300ms"></span>
            </div>
          </div>

          <!-- Error Message -->
          <div v-if="error" class="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            <Icon icon="lucide:alert-circle" class="w-4 h-4 inline mr-2" />
            {{ error }}
          </div>
        </div>
      </div>

      <!-- Input Area -->
      <div class="border-t bg-white p-4">
        <div class="max-w-4xl mx-auto">
          <!-- Input with button inside -->
          <div class="relative">
            <textarea
              v-model="inputText"
              @keydown.enter.exact.prevent="sendMessage"
              placeholder="输入您的问题，例如：有多少用户？"
              rows="1"
              class="w-full resize-none border border-gray-200 rounded-lg px-4 py-3 pr-12 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              :disabled="loading || databases.length === 0"
            />
            <button
              @click="sendMessage"
              :disabled="!inputText.trim() || loading || databases.length === 0"
              class="absolute right-2 bottom-2 p-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Icon v-if="!loading" icon="lucide:send" class="w-5 h-5" />
              <Icon v-else icon="lucide:loader-2" class="w-5 h-5 animate-spin" />
            </button>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>