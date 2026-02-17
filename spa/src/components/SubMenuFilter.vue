<template>
  <div class="sub-menu-filter" :class="{ 'has-toolbar': hasToolbar }">
    <div class="sub-menu-filter-glass">
      <!-- Single row: filter strip (scroll) + toolbar -->
      <div class="sub-menu-filter-strip">
        <button
          type="button"
          class="sub-menu-filter-chip"
          :class="{ active: selectedValue === allValue }"
          :aria-pressed="selectedValue === allValue"
          @click="select(allValue)"
        >
          <span v-if="filterAllLabel" class="sub-menu-filter-chip-label">{{ filterAllLabel }}</span>
          <slot v-else name="all-label">All</slot>
        </button>
        <button
          v-for="item in filters"
          :key="String(item.value)"
          type="button"
          class="sub-menu-filter-chip"
          :class="{ active: selectedValue === item.value }"
          :aria-pressed="selectedValue === item.value"
          :aria-label="item.label"
          @click="select(item.value)"
        >
          <img
            v-if="item.image"
            :src="item.image"
            :alt="item.label"
            class="sub-menu-filter-chip-avatar"
            loading="lazy"
            @error="($event.target).style.display = 'none'"
          />
          <span v-else class="sub-menu-filter-chip-avatar sub-menu-filter-chip-avatar-placeholder">
            {{ (item.label || '').charAt(0).toUpperCase() }}
          </span>
          <span class="sub-menu-filter-chip-label">{{ item.label }}</span>
        </button>
      </div>
      <template v-if="hasToolbar">
        <div v-if="showSearch" class="sub-menu-filter-search">
          <i class="fas fa-search" aria-hidden="true"></i>
          <input
            :value="searchQuery"
            type="text"
            class="sub-menu-filter-search-input"
            :placeholder="searchPlaceholder"
            :aria-label="searchPlaceholder"
            @input="$emit('update:searchQuery', ($event.target).value)"
          />
          <button
            v-if="searchQuery"
            type="button"
            class="sub-menu-filter-search-clear"
            aria-label="Clear search"
            @click="$emit('update:searchQuery', '')"
          >
            <i class="fas fa-times" aria-hidden="true"></i>
          </button>
        </div>
        <select
          v-if="sortOptions && sortOptions.length"
          :value="sortBy"
          class="sub-menu-filter-sort"
          :aria-label="sortLabel"
          @change="$emit('update:sortBy', ($event.target).value)"
        >
          <option v-for="opt in sortOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
        </select>
        <div v-if="showViewToggle" class="sub-menu-filter-view">
          <button
            type="button"
            class="sub-menu-filter-view-btn"
            :class="{ active: viewMode === 'grid' }"
            aria-label="Grid view"
            @click="$emit('update:viewMode', 'grid')"
          >
            <i class="fas fa-th" aria-hidden="true"></i>
          </button>
          <button
            type="button"
            class="sub-menu-filter-view-btn"
            :class="{ active: viewMode === 'list' }"
            aria-label="List view"
            @click="$emit('update:viewMode', 'list')"
          >
            <i class="fas fa-list" aria-hidden="true"></i>
          </button>
        </div>
        <slot name="toolbar-right"></slot>
        <button
          v-if="actionLabel || $slots.action"
          type="button"
          class="sub-menu-filter-action"
          @click="$emit('action')"
        >
          <slot name="action">
            <i v-if="actionIcon" :class="actionIcon" aria-hidden="true"></i>
            <span>{{ actionLabel }}</span>
          </slot>
        </button>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  /** Currently selected filter value (e.g. '' for All or artist name) */
  modelValue: { type: [String, Number], default: '' },
  /** List of { value, label, image? } for filter chips */
  filters: { type: Array, default: () => [] },
  /** Value that means "all" (e.g. '') */
  allValue: { type: [String, Number], default: '' },
  /** Label for the "All" chip */
  filterAllLabel: { type: String, default: 'All' },
  /** Show search input */
  showSearch: { type: Boolean, default: false },
  searchPlaceholder: { type: String, default: 'Search…' },
  searchQuery: { type: String, default: '' },
  /** Sort dropdown: [{ value, label }] */
  sortOptions: { type: Array, default: () => [] },
  sortLabel: { type: String, default: 'Sort' },
  sortBy: { type: String, default: '' },
  /** Show grid/list toggle */
  showViewToggle: { type: Boolean, default: false },
  viewMode: { type: String, default: 'list' },
  /** Primary action button */
  actionLabel: { type: String, default: '' },
  actionIcon: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue', 'update:searchQuery', 'update:sortBy', 'update:viewMode', 'action'])

const selectedValue = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v),
})

const hasToolbar = computed(
  () =>
    props.showSearch ||
    (props.sortOptions && props.sortOptions.length) ||
    props.showViewToggle ||
    props.actionLabel ||
    (props.actionIcon && !props.actionLabel)
)

function select(value) {
  emit('update:modelValue', value)
}
</script>

<style scoped>
.sub-menu-filter {
  width: 100%;
  margin-bottom: 12px;
}

.sub-menu-filter-glass {
  background: rgba(0, 0, 0, 0.14);
  backdrop-filter: blur(28px);
  -webkit-backdrop-filter: blur(28px);
  border-radius: 12px 12px 0 0;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  padding: 8px 12px 10px;
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 10px;
  flex-wrap: nowrap;
}

.sub-menu-filter-strip {
  display: flex;
  align-items: center;
  gap: 8px;
  overflow-x: auto;
  scrollbar-width: none;
  -webkit-overflow-scrolling: touch;
  flex: 1;
  min-width: 0;
}

.sub-menu-filter-strip::-webkit-scrollbar {
  display: none;
}

.sub-menu-filter-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
  padding: 6px 12px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.04);
  color: rgba(255, 255, 255, 0.82);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s ease, border-color 0.2s ease, color 0.2s ease;
  -webkit-tap-highlight-color: transparent;
}

.sub-menu-filter-chip:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.15);
  color: rgba(255, 255, 255, 0.95);
}

.sub-menu-filter-chip.active {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(255, 255, 255, 0.2);
  color: #fff;
}

.sub-menu-filter-chip-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  object-fit: cover;
  flex-shrink: 0;
}

.sub-menu-filter-chip-avatar-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.12);
  color: rgba(255, 255, 255, 0.9);
  font-size: 11px;
  font-weight: 600;
}

.sub-menu-filter-chip-label {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 120px;
}

/* Toolbar items (same row, right side) */
.sub-menu-filter-search {
  flex-shrink: 0;
  width: 160px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}

.sub-menu-filter-search i {
  color: rgba(255, 255, 255, 0.5);
  font-size: 13px;
}

.sub-menu-filter-search-input {
  flex: 1;
  min-width: 0;
  background: none;
  border: none;
  outline: none;
  color: #f8fafc;
  font-size: 14px;
}

.sub-menu-filter-search-input::placeholder {
  color: rgba(255, 255, 255, 0.45);
}

.sub-menu-filter-search-clear {
  padding: 0 4px;
  border: none;
  background: none;
  color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  font-size: 13px;
}

.sub-menu-filter-search-clear:hover {
  color: rgba(255, 255, 255, 0.9);
}

.sub-menu-filter-sort {
  padding: 6px 10px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  cursor: pointer;
  min-width: 0;
  flex-shrink: 0;
}

.sub-menu-filter-view {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}

.sub-menu-filter-view-btn {
  width: 34px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.04);
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s, color 0.2s;
}

.sub-menu-filter-view-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.95);
}

.sub-menu-filter-view-btn.active {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(255, 255, 255, 0.2);
  color: #fff;
}

.sub-menu-filter-action {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.06);
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  flex-shrink: 0;
  transition: background 0.2s, border-color 0.2s;
}

.sub-menu-filter-action:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

@media (max-width: 768px) {
  .sub-menu-filter-glass {
    padding: 8px 12px 10px;
  }
  .sub-menu-filter-chip {
    padding: 5px 10px;
    font-size: 14px;
  }
  .sub-menu-filter-chip-avatar,
  .sub-menu-filter-chip-avatar-placeholder {
    width: 20px;
    height: 20px;
    font-size: 10px;
  }
  .sub-menu-filter-chip-label {
    max-width: 90px;
  }
  .sub-menu-filter-search {
    width: 100px;
  }
  .sub-menu-filter-search-input,
  .sub-menu-filter-sort {
    font-size: 14px;
  }
}
</style>
