import { ref } from 'vue'

// Shared state for mobile UI collapse (dock + mini player)
const isPlayerCollapsed = ref(false)
const isDockCollapsed = ref(false)

// Player and dock both open by default (not persisted)

export function useMobileCollapse() {
  // No persistence — player and dock are open by default on every load

  const togglePlayer = () => {
    isPlayerCollapsed.value = !isPlayerCollapsed.value
  }

  const toggleDock = () => {
    isDockCollapsed.value = !isDockCollapsed.value
  }

  const collapseAll = () => {
    isPlayerCollapsed.value = true
    isDockCollapsed.value = true
  }

  const expandAll = () => {
    isPlayerCollapsed.value = false
    isDockCollapsed.value = false
  }

  return {
    isPlayerCollapsed,
    isDockCollapsed,
    togglePlayer,
    toggleDock,
    collapseAll,
    expandAll
  }
}
