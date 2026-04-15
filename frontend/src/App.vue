<script setup lang="ts">
import { ref, onMounted } from 'vue'
import Sidebar from '@/components/layout/Sidebar.vue'
import Header from '@/components/layout/Header.vue'
import ChatContainer from '@/components/chat/ChatContainer.vue'
import SettingsPanel from '@/components/settings/SettingsPanel.vue'
import { useChatStore } from '@/stores/chatStore'
import { useDatabaseStore } from '@/stores/databaseStore'

const chatStore = useChatStore()
const databaseStore = useDatabaseStore()

const sidebarCollapsed = ref(false)
const showSettings = ref(false)

onMounted(async () => {
  await databaseStore.init()
  await chatStore.loadConversations()
})

function handleDatabaseChanged() {
  chatStore.clearCurrentConversation()
}
</script>

<template>
  <div class="flex h-screen bg-gray-50">
    <!-- Sidebar -->
    <Sidebar
      :collapsed="sidebarCollapsed"
      @new-chat="chatStore.createConversation"
      @select="chatStore.loadConversation"
      @delete="chatStore.deleteConversation"
    />

    <!-- Main Content -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <Header
        :current-db="databaseStore.currentDatabase"
        :sidebar-collapsed="sidebarCollapsed"
        :databases="databaseStore.databases"
        @open-settings="showSettings = true"
        @toggle-sidebar="sidebarCollapsed = !sidebarCollapsed"
        @set-db="databaseStore.setCurrentDatabase"
      />

      <ChatContainer
        :messages="chatStore.messages"
        :loading="chatStore.loading"
        :error="chatStore.error"
        :databases="databaseStore.databases"
        :current-db="databaseStore.currentDatabase?.name"
        @send="chatStore.sendMessage"
      />
    </div>

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