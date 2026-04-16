<script setup lang="ts">
import { computed } from 'vue'
import { Icon } from '@iconify/vue'
import { useAppStore, MENU_CONFIG, type MenuItem } from '@/stores/appStore'

const appStore = useAppStore()

const menuItems: MenuItem[] = ['smart-query', 'adhoc-query', 'alert', 'settings']

function handleMenuClick(item: MenuItem) {
  appStore.setMenu(item)
}

function isActive(item: MenuItem): boolean {
  return appStore.currentMenu === item
}
</script>

<template>
  <aside
    class="bg-white border-r border-gray-200 flex flex-col transition-all duration-300 w-16"
  >
    <!-- Logo -->
    <div class="h-14 flex items-center justify-center border-b border-gray-200">
      <div class="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center">
        <Icon icon="lucide:database" class="w-5 h-5 text-white" />
      </div>
    </div>

    <!-- Menu Items -->
    <nav class="flex-1 py-4 px-2">
      <div
        v-for="item in menuItems"
        :key="item"
        @click="handleMenuClick(item)"
        :class="[
          'flex flex-col items-center justify-center py-3 px-1 rounded-lg cursor-pointer transition-all mb-1 group',
          isActive(item)
            ? 'bg-blue-50 text-blue-600'
            : 'text-gray-500 hover:bg-gray-50 hover:text-gray-700'
        ]"
        :title="MENU_CONFIG[item].label"
      >
        <Icon
          :icon="MENU_CONFIG[item].icon"
          :class="[
            'w-5 h-5 transition-transform',
            isActive(item) ? 'scale-110' : 'group-hover:scale-105'
          ]"
        />
        <span class="text-xs mt-1.5 font-medium">{{ MENU_CONFIG[item].label }}</span>
      </div>
    </nav>
  </aside>
</template>
