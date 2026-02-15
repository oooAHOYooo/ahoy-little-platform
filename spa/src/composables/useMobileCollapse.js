import { ref, watch } from 'vue'

// Shared state for mobile UI collapse (dock + mini player)
const isPlayerCollapsed = ref(false)
const isDockCollapsed = ref(false)

// Load from localStorage on init
if (typeof window !== 'undefined') {
  const savedPlayerState = localStorage.getItem('ahoy.ui.playerCollapsed')
  const savedDockState = localStorage.getItem('ahoy.ui.dockCollapsed')
  if (savedPlayerState !== null) isPlayerCollapsed.value = savedPlayerState === 'true'
  if (savedDockState !== null) isDockCollapsed.value = savedDockState === 'true'
}

export function useMobileCollapse() {
  // Persist to localStorage
  watch(isPlayerCollapsed, (val) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('ahoy.ui.playerCollapsed', String(val))
    }
  })

  watch(isDockCollapsed, (val) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('ahoy.ui.dockCollapsed', String(val))
    }
  })

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

  // Swipe detection helper
  let touchStartY = 0
  let touchStartTime = 0

  const handleTouchStart = (e, onCollapse, onExpand) => {
    touchStartY = e.touches[0].clientY
    touchStartTime = Date.now()
  }

  const handleTouchMove = (e, isCollapsed, onCollapse, onExpand) => {
    const touchY = e.touches[0].clientY
    const deltaY = touchY - touchStartY
    const deltaTime = Date.now() - touchStartTime

    // Swipe down to collapse (at least 50px, within 300ms)
    if (!isCollapsed && deltaY > 50 && deltaTime < 300) {
      onCollapse()
    }
    // Swipe up to expand (at least 50px, within 300ms)
    else if (isCollapsed && deltaY < -50 && deltaTime < 300) {
      onExpand()
    }
  }

  return {
    isPlayerCollapsed,
    isDockCollapsed,
    togglePlayer,
    toggleDock,
    collapseAll,
    expandAll,
    handleTouchStart,
    handleTouchMove
  }
}
