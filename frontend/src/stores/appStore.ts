import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

// 功能菜单类型
export type MenuItem = 'smart-query' | 'adhoc-query' | 'alert' | 'settings'

// 会话菜单类型（不包含 settings）
export type MenuType = 'smart-query' | 'adhoc-query' | 'alert'

// 菜单配置
export const MENU_CONFIG: Record<MenuItem, { label: string; icon: string }> = {
  'smart-query': { label: '智能问数', icon: 'lucide:message-square-text' },
  'adhoc-query': { label: '即席查询', icon: 'lucide:table' },
  'alert': { label: '智能告警', icon: 'lucide:bell' },
  'settings': { label: '设置', icon: 'lucide:settings' },
}

export const useAppStore = defineStore('app', () => {
  // 当前选中的菜单
  const currentMenu = ref<MenuItem>('smart-query')

  // 右侧面板折叠状态（默认展开）
  const rightPanelCollapsed = ref(false)

  // 左侧菜单折叠状态
  const sidebarCollapsed = ref(false)

  // 当前菜单是否有会话功能
  const hasConversations = computed(() => {
    return currentMenu.value !== 'settings'
  })

  // 设置当前菜单
  function setMenu(menu: MenuItem) {
    currentMenu.value = menu
  }

  // 切换右侧面板
  function toggleRightPanel() {
    rightPanelCollapsed.value = !rightPanelCollapsed.value
  }

  // 切换左侧菜单
  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  return {
    currentMenu,
    rightPanelCollapsed,
    sidebarCollapsed,
    hasConversations,
    setMenu,
    toggleRightPanel,
    toggleSidebar,
  }
})
