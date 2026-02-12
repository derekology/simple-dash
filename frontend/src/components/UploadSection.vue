<script setup lang="ts">
import { ref, computed } from 'vue'

const emit = defineEmits<{
    filesSelected: [files: File[]]
    upload: []
    validationError: [error: string]
}>()

const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB
const MAX_FILES = 12

const selectedFiles = ref<File[]>([])
const isDragging = ref(false)

const validateFiles = (files: File[]): { valid: File[], errors: string[] } => {
    const errors: string[] = []
    const valid: File[] = []

    if (files.length > MAX_FILES) {
        errors.push(`Too many files selected. Maximum ${MAX_FILES} files allowed.`)
        return { valid: files.slice(0, MAX_FILES), errors }
    }

    for (const file of files) {
        if (file.size > MAX_FILE_SIZE) {
            errors.push(`${file.name} is too large (${(file.size / (1024 * 1024)).toFixed(2)}MB). Maximum size is 10MB.`)
        } else {
            valid.push(file)
        }
    }

    return { valid, errors }
}

const handleFileInput = (event: Event) => {
    const target = event.target as HTMLInputElement
    if (target.files) {
        const csvFiles = Array.from(target.files).filter(file => file.name.toLowerCase().endsWith('.csv'))
        const { valid, errors } = validateFiles(csvFiles)
        selectedFiles.value = valid
        emit('filesSelected', valid)
        if (errors.length > 0) {
            emit('validationError', errors.join(' '))
        }
    }
}

const handleDrop = (event: DragEvent) => {
    isDragging.value = false
    if (event.dataTransfer?.files) {
        const csvFiles = Array.from(event.dataTransfer.files).filter(file => file.name.toLowerCase().endsWith('.csv'))
        const { valid, errors } = validateFiles(csvFiles)
        selectedFiles.value = valid
        emit('filesSelected', valid)
        if (errors.length > 0) {
            emit('validationError', errors.join(' '))
        }
    }
}

const handleDragOver = (event: DragEvent) => {
    event.preventDefault()
    isDragging.value = true
}

const handleDragLeave = () => {
    isDragging.value = false
}

const removeFile = (index: number) => {
    selectedFiles.value.splice(index, 1)
    emit('filesSelected', selectedFiles.value)
}

const clearFiles = () => {
    selectedFiles.value = []
    emit('filesSelected', [])
}

const triggerUpload = () => {
    if (selectedFiles.value.length > 0) {
        emit('upload')
    }
}

const totalSize = computed(() => {
    return selectedFiles.value.reduce((sum, file) => sum + file.size, 0)
})
</script>

<template>
    <div class="upload-section">
        <div v-if="selectedFiles.length === 0" class="drop-zone" :class="{ 'dragging': isDragging }"
            @drop.prevent="handleDrop" @dragover.prevent="handleDragOver" @dragleave="handleDragLeave">
            <div class="drop-zone-content">
                <svg class="upload-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" stroke-width="2">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                    <polyline points="17 8 12 3 7 8" />
                    <line x1="12" y1="3" x2="12" y2="15" />
                </svg>
                <p class="drop-text">Drag and drop CSV files here</p>
                <p class="drop-subtext">or</p>
                <label class="file-input-label">
                    <input type="file" accept=".csv" multiple @change="handleFileInput" class="file-input" />
                    Browse Files
                </label>
                <p class="limits-text">Max {{ MAX_FILES }} files, 10MB per file</p>
                <p class="limits-text">If you upload duplicate campaigns, we’ll try to use the most recent version. For
                    best
                    results, remove duplicates before uploading.</p>
            </div>
        </div>

        <div v-if="selectedFiles.length > 0" class="selected-files">
            <h3>Selected Files ({{ selectedFiles.length }}/{{ MAX_FILES }})</h3>
            <p class="total-size">Total size: {{ (totalSize / (1024 * 1024)).toFixed(2) }} MB</p>
            <ul class="file-list">
                <li v-for="(file, index) in selectedFiles" :key="index" class="file-item">
                    <span class="file-name">{{ file.name }}</span>
                    <span class="file-size">{{ (file.size / 1024).toFixed(2) }} KB</span>
                    <button @click="removeFile(index)" class="remove-btn">×</button>
                </li>
            </ul>
            <button @click="triggerUpload" class="upload-btn">Upload</button>
            <button @click="clearFiles" class="back-link">Clear all files</button>
        </div>
    </div>
</template>

<style scoped>
.upload-section {
    width: 100%;
    max-width: 800px;
    margin: 0 auto;
}

.drop-zone {
    border: 2px dashed var(--color-primary);
    border-radius: 8px;
    padding: 60px 20px;
    text-align: center;
    background-color: var(--color-bg-white);
    transition: all 0.3s ease;
    cursor: pointer;
}

.drop-zone.dragging {
    background-color: #fff5f5;
    border-color: var(--color-primary-dark);
}

.drop-zone-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;
}

.upload-icon {
    width: 64px;
    height: 64px;
    color: var(--color-primary);
}

.drop-text {
    font-size: 18px;
    font-weight: 600;
    color: var(--color-bg-dark);
    margin: 0;
}

.drop-subtext {
    font-size: 14px;
    color: var(--color-text-light);
    margin: 0;
}

.limits-text {
    font-size: 12px;
    color: var(--color-text-lighter);
    margin: 0;
    font-style: italic;
    max-width: 500px;
}

.file-input {
    display: none;
}

.file-input-label {
    display: inline-block;
    padding: 12px 32px;
    background-color: var(--color-primary);
    color: var(--color-bg-white);
    border-radius: 6px;
    font-weight: 600;
    cursor: pointer;
    transition: background-color 0.2s ease;
}

.file-input-label:hover {
    background-color: var(--color-primary-dark);
}

.selected-files {
    margin-top: 32px;
    background-color: var(--color-bg-white);
    padding: 24px;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.selected-files h3 {
    margin: 0 0 8px 0;
    color: var(--color-bg-dark);
    font-size: 18px;
}

.total-size {
    margin: 0 0 16px 0;
    font-size: 14px;
    color: var(--color-text-light);
}

.file-list {
    list-style: none;
    padding: 0;
    margin: 0 0 24px 0;
}

.file-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    background-color: var(--color-bg);
    border: 1px solid var(--color-border-light);
    border-radius: 6px;
    margin-bottom: 8px;
}

.file-name {
    flex: 1;
    color: var(--color-bg-dark);
    font-weight: 500;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.file-size {
    color: var(--color-text-light);
    font-size: 14px;
}

.remove-btn {
    background: none;
    border: none;
    color: var(--color-primary);
    font-size: 28px;
    line-height: 1;
    cursor: pointer;
    padding: 0;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: color 0.2s ease;
}

.remove-btn:hover {
    color: var(--color-primary-dark);
}

.upload-btn {
    width: 100%;
    padding: 14px;
    background-color: var(--color-primary);
    color: var(--color-bg-white);
    border: none;
    border-radius: 6px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: background-color 0.2s ease;
    margin-bottom: 12px;
}

.upload-btn:hover {
    background-color: var(--color-primary-dark);
}

.upload-btn:disabled {
    background-color: var(--color-border-light);
    cursor: not-allowed;
}

.back-link {
    display: block;
    width: 100%;
    background: none;
    border: none;
    color: var(--color-text-light);
    font-size: 14px;
    text-align: center;
    cursor: pointer;
    padding: 8px;
    transition: color 0.2s ease;
}

.back-link:hover {
    color: var(--color-primary);
}
</style>
