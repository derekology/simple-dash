<script setup lang="ts">
import { ref, computed, watch } from 'vue'

interface Option {
  value: number
  label: string
  subtitle?: string
}

const props = defineProps<{
  options: Option[]
  modelValue: number[]
  showOutliers?: boolean
  outliersCount?: number
  outliersButtonText?: string
  showLowVolume?: boolean
  lowVolumeCount?: number
  lowVolumeButtonText?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: number[]]
  'toggleOutliers': []
  'toggleLowVolume': []
}>()

const isOpen = ref(false)
const searchQuery = ref('')

const filteredOptions = computed(() => {
  if (!searchQuery.value) return props.options
  const query = searchQuery.value.toLowerCase()
  return props.options.filter(opt =>
    opt.label.toLowerCase().includes(query) ||
    (opt.subtitle && opt.subtitle.toLowerCase().includes(query))
  )
})

const selectedCount = computed(() => props.modelValue.length)

const isSelected = (value: number) => {
  return props.modelValue.includes(value)
}

const toggleOption = (value: number) => {
  if (isSelected(value)) {
    emit('update:modelValue', props.modelValue.filter(v => v !== value))
  } else {
    emit('update:modelValue', [...props.modelValue, value])
  }
}

const selectAll = () => {
  emit('update:modelValue', filteredOptions.value.map(opt => opt.value))
}

const selectNone = () => {
  emit('update:modelValue', [])
}

const toggleDropdown = () => {
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    searchQuery.value = ''
  }
}

const closeDropdown = () => {
  isOpen.value = false
  searchQuery.value = ''
}

// Close dropdown when clicking outside
const dropdownRef = ref<HTMLElement | null>(null)
const handleClickOutside = (event: MouseEvent) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target as Node)) {
    closeDropdown()
  }
}

watch(isOpen, (open) => {
  if (open) {
    document.addEventListener('click', handleClickOutside)
  } else {
    document.removeEventListener('click', handleClickOutside)
  }
})
</script>

<template>
  <div class="multi-search-dropdown" ref="dropdownRef">
    <button class="dropdown-trigger" @click.stop="toggleDropdown" type="button">
      <div class="trigger-content">
        <span class="trigger-label">
          {{ selectedCount === 0 ? 'Select campaigns...' : `${selectedCount} campaign${selectedCount === 1 ? '' : 's'}
          selected` }}
        </span>
      </div>
      <svg class="dropdown-icon" :class="{ open: isOpen }" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
        fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="6 9 12 15 18 9" />
      </svg>
    </button>

    <div v-if="isOpen" class="dropdown-menu">
      <input v-model="searchQuery" type="text" class="dropdown-search" placeholder="Search..." @click.stop />
      <div class="dropdown-actions">
        <button @click.stop="selectAll" class="action-button" type="button">Select All</button>
        <button @click.stop="selectNone" class="action-button" type="button">Select None</button>
        <button v-if="showOutliers && outliersCount && outliersCount > 0" @click.stop="emit('toggleOutliers')"
          class="action-button outliers-button" type="button"
          :title="`${outliersCount} outlier${outliersCount === 1 ? '' : 's'} detected based on deliveries (IQR method)`">
          {{ outliersButtonText }} ({{ outliersCount }})
        </button>
        <button v-if="showLowVolume && lowVolumeCount && lowVolumeCount > 0" @click.stop="emit('toggleLowVolume')"
          class="action-button low-volume-button" type="button"
          :title="`${lowVolumeCount} campaign${lowVolumeCount === 1 ? '' : 's'} with deliveries < 50% of median`">
          {{ lowVolumeButtonText }} ({{ lowVolumeCount }})
        </button>
      </div>
      <div class="dropdown-options">
        <label v-for="option in filteredOptions" :key="option.value" class="dropdown-option" @click.stop>
          <input type="checkbox" :checked="isSelected(option.value)" @change="toggleOption(option.value)"
            class="option-checkbox" />
          <div class="option-content">
            <span class="option-label">{{ option.label }}</span>
            <span v-if="option.subtitle" class="option-subtitle">{{ option.subtitle }}</span>
          </div>
        </label>
        <div v-if="filteredOptions.length === 0" class="no-results">
          No results found
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.multi-search-dropdown {
  position: relative;
  width: 100%;
}

.dropdown-trigger {
  width: 100%;
  padding: 12px 16px;
  background-color: var(--color-bg-white);
  border: 2px solid var(--color-border-light);
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  transition: border-color 0.2s ease;
}

.dropdown-trigger:hover {
  border-color: var(--color-primary);
}

.trigger-content {
  flex: 1;
  text-align: left;
}

.trigger-label {
  font-weight: 600;
  color: var(--color-bg-dark);
}

.dropdown-icon {
  width: 20px;
  height: 20px;
  color: var(--color-text-light);
  transition: transform 0.2s ease;
  flex-shrink: 0;
}

.dropdown-icon.open {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  right: 0;
  background-color: var(--color-bg-white);
  border: 2px solid var(--color-border-light);
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  max-height: 450px;
  display: flex;
  flex-direction: column;
}

.dropdown-search {
  padding: 12px 16px;
  border: none;
  border-bottom: 2px solid var(--color-border-light);
  font-size: 14px;
  outline: none;
}

.dropdown-search:focus {
  border-bottom-color: var(--color-primary);
}

.dropdown-actions {
  display: flex;
  gap: 8px;
  padding: 8px 12px;
  border-bottom: 2px solid var(--color-border-light);
  flex-wrap: wrap;
}

.action-button {
  flex: 1;
  min-width: 100px;
  padding: 6px 12px;
  background-color: var(--color-bg);
  border: 1px solid var(--color-border-light);
  border-radius: 4px;
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-light);
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-button:hover {
  background-color: var(--color-primary);
  color: var(--color-bg-white);
  border-color: var(--color-primary);
}

.outliers-button {
  background-color: #fff9e6;
  border-color: var(--color-warning);
  color: var(--color-warning);
}

.outliers-button:hover {
  background-color: var(--color-warning);
  color: var(--color-bg-white);
  border-color: var(--color-warning);
}

.dropdown-options {
  overflow-y: auto;
  max-height: 350px;
}

.dropdown-option {
  width: 100%;
  padding: 12px 16px;
  cursor: pointer;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  transition: background-color 0.2s ease;
}

.dropdown-option:hover {
  background-color: var(--color-bg);
}

.option-checkbox {
  margin-top: 2px;
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: var(--color-primary);
}

.option-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.option-label {
  font-weight: 600;
  color: var(--color-bg-dark);
}

.option-subtitle {
  font-size: 14px;
  color: var(--color-text-light);
}

.no-results {
  padding: 24px;
  text-align: center;
  color: var(--color-text-lighter);
  font-style: italic;
}
</style>
