<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import UploadSection from '@/components/UploadSection.vue'

interface CampaignData {
    platform: string
    subject: string
    sent_at: string
    delivered: number
    opens: number
    open_rate: number
    clicks: number
    click_rate: number
    ctor: number
    unsubscribes: number
    unsubscribe_rate: number
    spam_complaints: number
    hard_bounces: number
    hard_bounce_rate: number
    soft_bounces: number
    soft_bounce_rate: number
}

interface UploadResult {
    filename: string
    data?: { campaign?: CampaignData }
}

interface UploadResponse {
    results?: UploadResult[]
    errors?: Array<{ filename: string; error: string }>
}

const router = useRouter()
const selectedFiles = ref<File[]>([])
const isUploading = ref(false)
const uploadResults = ref<UploadResponse | null>(null)
const uploadError = ref<string | null>(null)
const validationError = ref<string | null>(null)

const handleFilesSelected = (files: File[]) => {
    selectedFiles.value = files
    uploadResults.value = null
    uploadError.value = null
    validationError.value = null
}

const handleValidationError = (error: string) => {
    validationError.value = error
    uploadResults.value = null
    uploadError.value = null
}

const handleUpload = async () => {
    if (selectedFiles.value.length === 0) return

    isUploading.value = true
    uploadError.value = null
    uploadResults.value = null
    validationError.value = null

    try {
        sessionStorage.removeItem('campaigns')

        const formData = new FormData()
        selectedFiles.value.forEach(file => {
            formData.append('files', file)
        })

        const response = await fetch('http://localhost:8000/parse', {
            method: 'POST',
            body: formData,
        })

        if (!response.ok) {
            const errorData = await response.json().catch(() => null)
            throw new Error(errorData?.detail || `Upload failed: ${response.statusText}`)
        }

        const data = await response.json()
        uploadResults.value = data

        if (data.results && data.results.length > 0) {
            const campaigns = data.results
                .filter((r: UploadResult) => r.data?.campaign)
                .map((r: UploadResult) => r.data!.campaign!)

            if (campaigns.length > 0) {
                sessionStorage.setItem('campaigns', JSON.stringify(campaigns))
                router.push({ name: 'dashboard' })
            }
        }
    } catch (error) {
        uploadError.value = error instanceof Error ? error.message : 'Upload failed'
    } finally {
        isUploading.value = false
    }
}

const viewDashboard = () => {
    if (uploadResults.value?.results && uploadResults.value.results.length > 0) {
        const campaigns = uploadResults.value.results
            .filter((r: UploadResult) => r.data?.campaign)
            .map((r: UploadResult) => r.data!.campaign!)

        if (campaigns.length > 0) {
            sessionStorage.setItem('campaigns', JSON.stringify(campaigns))
            router.push({ name: 'dashboard' })
        }
    }
}
</script>

<template>
    <main class="main-content">
        <div class="content-wrapper">
            <h1 class="page-title">Upload Email Reports</h1>
            <p class="page-description">
                Upload one or more MailChimp or MailerLite Classic reports (more platforms coming soon!)
            </p>

            <UploadSection @files-selected="handleFilesSelected" @upload="handleUpload"
                @validation-error="handleValidationError" />

            <div v-if="validationError" class="status-message warning">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                    stroke-width="2">
                    <path
                        d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
                    <line x1="12" y1="9" x2="12" y2="13" />
                    <line x1="12" y1="17" x2="12.01" y2="17" />
                </svg>
                <p>{{ validationError }}</p>
            </div>

            <div v-if="isUploading" class="status-message uploading">
                <div class="spinner"></div>
                <p>Uploading and parsing files...</p>
            </div>

            <div v-if="uploadError" class="status-message error">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                    stroke-width="2">
                    <circle cx="12" cy="12" r="10" />
                    <line x1="15" y1="9" x2="9" y2="15" />
                    <line x1="9" y1="9" x2="15" y2="15" />
                </svg>
                <p>{{ uploadError }}</p>
            </div>

            <div v-if="uploadResults" class="results">
                <h2 class="results-title">Upload Results</h2>

                <div v-if="uploadResults.results && uploadResults.results.length > 0" class="results-section success">
                    <h3>Successfully Parsed ({{ uploadResults.results.length }})</h3>
                    <ul class="results-list">
                        <li v-for="(result, index) in uploadResults.results" :key="index" class="result-item">
                            <svg class="check-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
                                stroke="currentColor" stroke-width="2">
                                <polyline points="20 6 9 17 4 12" />
                            </svg>
                            <div class="result-content">
                                <span class="result-filename">{{ result.filename }}</span>
                                <span class="result-details">
                                    {{ result.data?.campaign ? 1 : 0 }} campaign found
                                </span>
                            </div>
                        </li>
                    </ul>
                    <button @click="viewDashboard" class="dashboard-btn">View Dashboard</button>
                </div>

                <div v-if="uploadResults.errors && uploadResults.errors.length > 0"
                    class="results-section error-section">
                    <h3>Errors ({{ uploadResults.errors.length }})</h3>
                    <ul class="results-list">
                        <li v-for="(error, index) in uploadResults.errors" :key="index" class="result-item error-item">
                            <svg class="error-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
                                stroke="currentColor" stroke-width="2">
                                <circle cx="12" cy="12" r="10" />
                                <line x1="15" y1="9" x2="9" y2="15" />
                                <line x1="9" y1="9" x2="15" y2="15" />
                            </svg>
                            <div class="result-content">
                                <span class="result-filename">{{ error.filename }}</span>
                                <span class="result-error">{{ error.error }}</span>
                            </div>
                        </li>
                    </ul>
                </div>
            </div>
        </div>
    </main>
</template>

<style scoped>
.main-content {
    min-height: calc(100vh - var(--top-bar-height));
    justify-content: center;
    align-items: center;
    background-color: #fafafa;
}

.content-wrapper {
    max-width: 1200px;
    padding: 32px;
    margin: 0 auto;
}

.page-title {
    font-size: 36px;
    font-weight: 700;
    color: #222222;
    margin: 0 0 12px 0;
    text-align: center;
}

.page-description {
    font-size: 16px;
    color: #666666;
    margin: 0 0 48px 0;
    text-align: center;
}

.status-message {
    margin-top: 32px;
    padding: 24px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    gap: 16px;
    background-color: #ffffff;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.status-message.uploading {
    color: #222222;
}

.status-message.error {
    background-color: #fff5f5;
    color: #dd3333;
    border: 1px solid #dd3333;
}

.status-message.warning {
    background-color: #fffbf0;
    color: #ff9800;
    border: 1px solid #ff9800;
}

.status-message svg {
    width: 24px;
    height: 24px;
}

.status-message p {
    margin: 0;
    font-weight: 500;
}

.spinner {
    width: 24px;
    height: 24px;
    border: 3px solid #f3f3f3;
    border-top: 3px solid #dd3333;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% {
        transform: rotate(0deg);
    }

    100% {
        transform: rotate(360deg);
    }
}

.results {
    margin-top: 48px;
}

.results-title {
    font-size: 28px;
    font-weight: 700;
    color: #222222;
    margin: 0 0 24px 0;
    text-align: center;
}

.results-section {
    background-color: #ffffff;
    padding: 24px;
    border-radius: 8px;
    margin-bottom: 24px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.results-section h3 {
    margin: 0 0 16px 0;
    color: #222222;
    font-size: 18px;
    font-weight: 600;
}

.results-section.success {
    border-left: 4px solid #4caf50;
}

.results-section.error-section {
    border-left: 4px solid #dd3333;
}

.results-list {
    list-style: none;
    padding: 0;
    margin: 0 0 24px 0;
}

.dashboard-btn {
    width: 100%;
    padding: 14px;
    background-color: #dd3333;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: background-color 0.2s ease;
}

.dashboard-btn:hover {
    background-color: #cc2222;
}

.result-item {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 12px;
    background-color: #fafafa;
    border-radius: 6px;
    margin-bottom: 8px;
}

.check-icon {
    width: 20px;
    height: 20px;
    color: #4caf50;
    flex-shrink: 0;
    margin-top: 2px;
}

.error-icon {
    width: 20px;
    height: 20px;
    color: #dd3333;
    flex-shrink: 0;
    margin-top: 2px;
}

.result-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.result-filename {
    font-weight: 600;
    color: #222222;
}

.result-details {
    font-size: 14px;
    color: #666666;
}

.result-error {
    font-size: 14px;
    color: #dd3333;
}
</style>
