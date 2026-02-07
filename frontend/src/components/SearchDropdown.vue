<script setup lang="ts">
import { ref, computed, watch } from 'vue'

interface Option {
  value: number
  label: string
  subtitle?: string
}

const props = defineProps<{
  options: Option[]
  modelValue: number
  placeholder?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: number]
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

const selectedOption = computed(() => {
  return props.options.find(opt => opt.value === props.modelValue)
})

const selectOption = (value: number) => {
  emit('update:modelValue', value)
  isOpen.value = false
  searchQuery.value = ''
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
  <div class="search-dropdown" ref="dropdownRef">
    <button class="dropdown-trigger" @click.stop="toggleDropdown" type="button">
      <div class="trigger-content">
        <span class="trigger-label">{{ selectedOption?.label || placeholder || 'Select...' }}</span>
        <span v-if="selectedOption?.subtitle" class="trigger-subtitle">{{ selectedOption.subtitle }}</span>
      </div>
      <svg class="dropdown-icon" :class="{ open: isOpen }" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polyline points="6 9 12 15 18 9" />
      </svg>
    </button>
    
    <div v-if="isOpen" class="dropdown-menu">
      <input 
        v-model="searchQuery" 
        type="text" 
        class="dropdown-search" 
        placeholder="Search..."
        @click.stop
      />
      <div class="dropdown-options">
        <button 
          v-for="option in filteredOptions" 
          :key="option.value"
          class="dropdown-option"
          :class="{ selected: option.value === modelValue }"
          @click.stop="selectOption(option.value)"
          type="button"
        >
          <span class="option-label">{{ option.label }}</span>
          <span v-if="option.subtitle" class="option-subtitle">{{ option.subtitle }}</span>
        </button>
        <div v-if="filteredOptions.length === 0" class="no-results">
          No results found
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.search-dropdown {
  position: relative;
  width: 100%;
}

.dropdown-trigger {
  width: 100%;
  padding: 12px 16px;
  background-color: #ffffff;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  transition: border-color 0.2s ease;
}

.dropdown-trigger:hover {
  border-color: #dd3333;
}

.trigger-content {
  flex: 1;
  text-align: left;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.trigger-label {
  font-weight: 600;
  color: #222222;
}

.trigger-subtitle {
  font-size: 14px;
  color: #666666;
}

.dropdown-icon {
  width: 20px;
  height: 20px;
  color: #666666;
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
  background-color: #ffffff;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  max-height: 400px;
  display: flex;
  flex-direction: column;
}

.dropdown-search {
  padding: 12px 16px;
  border: none;
  border-bottom: 2px solid #e0e0e0;
  font-size: 14px;
  outline: none;
}

.dropdown-search:focus {
  border-bottom-color: #dd3333;
}

.dropdown-options {
  overflow-y: auto;
  max-height: 350px;
}

.dropdown-option {
  width: 100%;
  padding: 12px 16px;
  background: none;
  border: none;
  cursor: pointer;
  text-align: left;
  transition: background-color 0.2s ease;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.dropdown-option:hover {
  background-color: #fafafa;
}

.dropdown-option.selected {
  background-color: #fff5f5;
  border-left: 4px solid #dd3333;
}

.option-label {
  font-weight: 600;
  color: #222222;
}

.option-subtitle {
  font-size: 14px;
  color: #666666;
}

.no-results {
  padding: 24px;
  text-align: center;
  color: #999999;
  font-style: italic;
}
</style>
