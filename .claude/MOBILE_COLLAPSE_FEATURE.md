# Mobile Collapse Feature

## Overview
Added collapsible functionality to the mobile bottom navigation dock and now-playing bar for a cleaner, more immersive mobile experience.

## Features

### 1. **Collapsible Now Playing Bar**
   - Swipe down or tap the handle bar at the top to collapse
   - Swipe up or tap again to expand
   - Collapsed state shows only a small handle bar (20px)
   - Smooth animation with cubic-bezier easing

### 2. **Collapsible Mobile Dock**
   - Same swipe/tap interaction as the now playing bar
   - Independent collapse state from the now playing bar
   - Collapses both navigation rows simultaneously
   - Preserves all navigation functionality when expanded

### 3. **Persistent State**
   - Collapse preferences saved to localStorage
   - `ahoy.ui.playerCollapsed` - stores now playing bar state
   - `ahoy.ui.dockCollapsed` - stores mobile dock state
   - State persists across sessions and page reloads

### 4. **Adaptive Body Padding**
   - Body padding automatically adjusts when components are collapsed
   - Prevents content from being hidden under collapsed bars
   - Responsive to both mobile breakpoints (768px and 480px)

## Implementation Details

### Files Created
- `spa/src/composables/useMobileCollapse.js` - Shared collapse state management

### Files Modified
- `spa/src/components/MiniPlayer.vue` - Added collapse handle and state
- `spa/src/components/NavBar.vue` - Added collapse handle and state
- `spa/src/App.vue` - Added body class management for collapsed states
- `spa/src/assets/main.css` - Added collapse animations and padding adjustments
- `static/css/combined.css` - Added legacy support for Flask templates

### How It Works
1. **Composable** (`useMobileCollapse.js`):
   - Manages shared reactive state for both components
   - Provides toggle functions and swipe gesture handlers
   - Syncs with localStorage for persistence

2. **Touch Gestures**:
   - Detects swipe down (>50px in <300ms) to collapse
   - Detects swipe up (>50px in <300ms) to expand
   - Tap on handle bar instantly toggles state

3. **Animations**:
   - Uses `transform: translateY()` for smooth 60fps animations
   - `cubic-bezier(0.4, 0, 0.2, 1)` easing curve (Material Design standard)
   - 300ms duration for natural feel

4. **Desktop**:
   - Collapse handles hidden on screens wider than 768px
   - Feature only active on mobile devices

## Usage

### For Users
- **Collapse**: Swipe down on the handle bar or tap it
- **Expand**: Swipe up on the handle bar or tap it
- **Independent Control**: Now playing bar and dock can be collapsed separately

### For Developers
```javascript
import { useMobileCollapse } from '../composables/useMobileCollapse'

const collapse = useMobileCollapse()

// Access state
collapse.isPlayerCollapsed.value  // true/false
collapse.isDockCollapsed.value    // true/false

// Toggle functions
collapse.togglePlayer()
collapse.toggleDock()
collapse.collapseAll()
collapse.expandAll()
```

## Testing Checklist
- [ ] Swipe gestures work smoothly on mobile
- [ ] Tap on handle bar toggles state
- [ ] Collapsed state persists after page reload
- [ ] Body padding adjusts correctly when collapsed
- [ ] No overlap between content and collapsed bars
- [ ] Feature hidden on desktop (>768px)
- [ ] Animations are smooth without jank
- [ ] Works with both now playing bar and dock independently

## Future Enhancements
- Add haptic feedback on collapse/expand (requires native integration)
- Add animation preference for users who prefer reduced motion
- Consider auto-collapse after inactivity
- Add settings toggle to disable feature entirely
