<script setup lang="ts">
import { computed, onMounted } from 'vue'
import Sidebar from '@/components/layout/Sidebar.vue'
import Header from '@/components/layout/Header.vue'
import ConversationPanel from '@/components/layout/ConversationPanel.vue'
import ChatContainer from '@/components/chat/ChatContainer.vue'
import SettingsPanel from '@/components/settings/SettingsPanel.vue'
import AdhocContainer from '@/components/adhoc/AdhocContainer.vue'
import AlertContainer from '@/components/alert/AlertContainer.vue'
import { useAppStore } from '@/stores/appStore'
import { useChatStore } from '@/stores/chatStore'
import { useDatabaseStore } from '@/stores/databaseStore'

const appStore = useAppStore()
const chatStore = useChatStore()
const databaseStore = useDatabaseStore()

const showSettings = ref(false)

// 根据当前菜单显示不同内容
const currentComponent = computed(() => {
  switch (appStore.currentMenu) {
    case 'smart-query':
      return 'chat'
    case 'adhoc-query':
      return 'adhoc'
    case 'alert':
      return 'alert'
    case 'settings':
      return 'settings'
    default:
      return 'chat'
  }
})

onMounted(async () => {
  await databaseStore.init()
  await chatStore.loadConversations()
})

function handleDatabaseChanged() {
  chatStore.clearCurrentConversation()
}

// Watch for settings menu
import { ref, watch } from 'vue'
watch(() => appStore.currentMenu, (newMenu) => {
  if (newMenu === 'settings') {
    showSettings.value = true
  }
})
</script>

<template>
  <div class="flex h-screen bg-gray-50">
    <!-- Left Sidebar - Menu -->
    <Sidebar />

    <!-- Main Content Area -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <Header
        v-if="currentComponent !== 'settings'"
        :current-db="databaseStore.currentDatabase"
        :databases="databaseStore.databases"
        @open-settings="showSettings = true"
        @set-db="databaseStore.setCurrentDatabase"
      />

      <!-- Chat Container (智能问数) -->
      <ChatContainer
        v-if="currentComponent === 'chat'"
        :messages="chatStore.messages"
        :loading="chatStore.loading"
        :error="chatStore.error"
        :databases="databaseStore.databases"
        :current-db="databaseStore.currentDatabase?.name"
        @send="chatStore.sendMessage"
      />

      <!-- Adhoc Query (即席查询) -->
      <AdhocContainer v-else-if="currentComponent === 'adhoc'" />

      <!-- Alert (智能告警) -->
      <AlertContainer v-else-if="currentComponent === 'alert'" />

      <!-- Settings -->
      <div v-else-if="currentComponent === 'settings'" class="flex-1 flex items-center justify-center">
        <div class="text-center">
          <p class="text-gray-500 mb-4">点击右下角按钮打开设置面板</p>
          <button
            @click="showSettings = true"
            class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
          >
            打开设置
          </button>
        </div>
      </div>
    </div>

    <!-- Right Sidebar - Conversation Panel -->
    <ConversationPanel
      @new-chat="chatStore.createConversation"
      @select="chatStore.loadConversation"
      @delete="chatStore.deleteConversation"
    />

    <!-- Settings Panel -->
    <SettingsPanel
      v-model:show="showSettings"
      :databases="databaseStore.databases"
      :providers="databaseStore.providers"
      :config="databaseStore.config"
      @add-db="databaseStore.addDatabase"
      @remove-db="databaseStore.removeDatabase"
      @test-db="databaseStore.testConnection"
      @set-db="databaseStore.setCurrentDatabase"
      @update-model="databaseStore.updateModelConfig"
      @database-changed="handleDatabaseChanged"
    />
  </div>
</template>
