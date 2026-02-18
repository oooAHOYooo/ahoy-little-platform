<template>
  <div class="sub-menu-filter" :class="{ 'has-toolbar': hasToolbar }">
    <div class="sub-menu-filter-glass">
      <!-- Single row: filter strip (scroll) + toolbar -->
      <!-- Compact Filter Bar -->
      <div class="sub-menu-filter-row">
        <!-- Artist Filter (Compact Dropdown) -->
        <select
          :value="modelValue"
          class="sub-menu-filter-sort main-filter"
          aria-label="Filter by Artist"
          @change="$emit('update:modelValue', ($event.target).value)"
        >
          <option :value="allValue">{{ filterAllLabel || 'All Artists' }}</option>
          <option v-for="item in filters" :key="String(item.value)" :value="item.value">
            {{ item.label }}
          </option>
        </select>
      </div>
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
        <select
          v-if="albums && albums.length"
          :value="selectedAlbum"
          class="sub-menu-filter-sort"
          aria-label="Filter by Album"
          @change="$emit('update:selectedAlbum', ($event.target).value)"
        >
          <option value="">All Albums</option>
          <option v-for="alb in albums" :key="alb.value" :value="alb.value">{{ alb.label }}</option>
        </select>

        <button
          v-if="showFavoritesToggle"
          type="button"
          class="sub-menu-filter-view-btn"
          :class="{ active: favoritesOnly }"
          title="Show Favorites Only"
          aria-label="Top Favorites Only"
          @click="$emit('update:favoritesOnly', !favoritesOnly)"
        >
          <i :class="favoritesOnly ? 'fas fa-heart' : 'far fa-heart'" aria-hidden="true"></i>
        </button>

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
  /** Favorites Toggle */
  showFavoritesToggle: { type: Boolean, default: false },
  favoritesOnly: { type: Boolean, default: false },
  /** Album Filter */
  albums: { type: Array, default: () => [] },
  selectedAlbum: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue', 'update:searchQuery', 'update:sortBy', 'update:viewMode', 'update:favoritesOnly', 'update:selectedAlbum', 'action'])

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
  padding: 8px 12px;
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap; /* Allow wrapping on very small screens */
}

.sub-menu-filter-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1; /* Take up available space */
  min-width: 0;
}

/* Make the main artist filter prominent */
.sub-menu-filter-sort.main-filter {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
  color: #fff;
  font-weight: 600;
  flex: 1; /* Expand to fill space on mobile */
  min-width: 120px;
}

/* Toolbar items */
.sub-menu-filter-search {
  flex-shrink: 1;
  width: auto;
  min-width: 100px;
  max-width: 160px;
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
  appearance: none; /* Let's normalize it slightly, or use custom arrow if desired */
  /* Add custom chevron if needed, for now standard select is native and accessible */
}

/* On mobile, ensure things fit */
@media (max-width: 768px) {
  .sub-menu-filter-glass {
    gap: 6px;
    padding: 8px 10px;
  }
  .sub-menu-filter-sort {
    font-size: 13px;
    padding: 6px 8px;
    max-width: 140px; /* Constrain width */
  }
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
  .sub-menu-filter-search {
    width: 100px;
  }
  .sub-menu-filter-search-input,
  .sub-menu-filter-sort {
    font-size: 14px;
  }
}
</style>
