<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import UploadSection from '@/components/UploadSection.vue'
import { generateDemoData } from '@/utils/demoData'

interface CampaignData {
    platform: string
    subject: string
    email_title: string
    unique_id?: string
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

const hasDataInSession = () => {
    const campaignsJson = sessionStorage.getItem('campaigns')
    if (!campaignsJson) return false
    try {
        const campaigns = JSON.parse(campaignsJson)
        return Array.isArray(campaigns) && campaigns.length > 0
    } catch {
        return false
    }
}

const loadDemoData = () => {
    sessionStorage.removeItem('campaigns')
    sessionStorage.removeItem('failedUploads')

    const demoCampaigns = generateDemoData(10)

    sessionStorage.setItem('campaigns', JSON.stringify(demoCampaigns))

    router.push({ name: 'dashboard' })
}

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
        sessionStorage.removeItem('failedUploads')

        const formData = new FormData()
        selectedFiles.value.forEach(file => {
            formData.append('files', file)
        })

        const response = await fetch('/parse', {
            method: 'POST',
            body: formData,
        })

        if (!response.ok) {
            const errorData = await response.json().catch(() => null)
            throw new Error(errorData?.detail || `Upload failed: ${response.statusText}`)
        }

        const data = await response.json()
        uploadResults.value = data

        // Check if we have any successful results
        const hasResults = data.results && data.results.length > 0
        const hasErrors = data.errors && data.errors.length > 0

        if (hasErrors) {
            sessionStorage.setItem('failedUploads', JSON.stringify(data.errors))
        }

        if (hasResults) {
            const campaigns = data.results
                .filter((r: UploadResult) => r.data?.campaign)
                .map((r: UploadResult) => r.data!.campaign!)

            if (campaigns.length > 0) {
                sessionStorage.setItem('campaigns', JSON.stringify(campaigns))

                // If we have errors but also results, we'll still go to dashboard
                // but the banner will show the errors
                router.push({ name: 'dashboard' })
            } else if (hasErrors) {
                // No valid campaigns, only show error message
                uploadError.value = 'All files failed to parse. Please check the errors below.'
            }
        } else if (hasErrors) {
            // No results at all, only errors
            uploadError.value = 'All files failed to parse. Please check the errors below.'
        } else {
            // No results and no errors - weird state
            uploadError.value = 'No data was parsed from the uploaded files.'
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

            <!-- <div class="info-banner">
                <p class="info-text">
                    If you upload files containing the same campaign, we'll
                    attempt to use the most recent version. For best results, please filter duplicate campaigns before
                    uploading.
                </p>
            </div> -->

            <div class="demo-banner">
                <p class="demo-text">
                    Want to see what simple dash can do?
                </p>
                <button @click="loadDemoData" class="demo-button">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                        stroke-width="2" class="demo-icon">
                        <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4" />
                        <polyline points="10 17 15 12 10 7" />
                        <line x1="15" y1="12" x2="3" y2="12" />
                    </svg>
                    Try it with sample data
                </button>
            </div>

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
                    <button v-if="hasDataInSession()" @click="viewDashboard" class="dashboard-btn">Go to
                        Dashboard</button>
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
    background-color: var(--color-bg);
}

.content-wrapper {
    max-width: 800px;
    padding: 32px;
    margin: 0 auto;
}

.page-title {
    font-size: 36px;
    font-weight: 700;
    color: var(--color-bg-dark);
    margin: 0 0 12px 0;
    text-align: center;
}

.page-description {
    font-size: 16px;
    color: var(--color-text-light);
    margin: 0 0 24px 0;
    text-align: center;
}

.demo-banner {
    background: var(--color-bg-info-gradient);
    padding: 24px 32px;
    border-radius: 12px;
    margin-top: 32px;
    text-align: center;
    /* box-shadow: 0 4px 16px var(--color-border-dark); */
    border: 1px solid var(--color-info);
}

.demo-text {
    margin: 0 0 16px 0;
    /* color: var(--color-text); */
    color: #0d47a1;
    font-size: 18px;
    font-weight: 600;
}

.demo-button {
    display: inline-flex;
    align-items: center;
    gap: 12px;
    padding: 14px 28px;
    background-color: #ffffff;
    /* color: #0d47a1; */
    border: none;
    border-radius: 8px;
    font-size: 16px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.3s ease;
    color: var(--color-text-light);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.demo-button:hover {
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25);
    background-color: #f8f9ff;
}

.demo-icon {
    width: 20px;
    height: 20px;
}

.info-banner {
    margin-top: 32px;
    padding: 16px 20px;
    border-radius: 8px;
    display: flex;
    align-items: flex-start;
    gap: 12px;
    background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
    border: 1px solid #2196f3;
    box-shadow: 0 2px 6px rgba(33, 150, 243, 0.1);
}

.info-text {
    margin: 0;
    font-size: 14px;
    line-height: 1.5;
    color: #0d47a1;
    text-align: center;
}

.status-message {
    margin-top: 32px;
    padding: 24px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    gap: 16px;
    background-color: var(--color-bg-white);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.status-message.uploading {
    color: var(--color-bg-dark);
}

.status-message.error {
    background-color: #fff5f5;
    color: var(--color-primary);
    border: 1px solid var(--color-primary);
}

.status-message.warning {
    background-color: var(--color-bg-warning-gradient);
    color: var(--color-warning);
    border: 1px solid var(--color-warning);
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
    border: 3px solid var(--color-border-light);
    border-top: 3px solid var(--color-primary);
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
    color: var(--color-bg-dark);
    margin: 0 0 24px 0;
    text-align: center;
}

.results-section {
    background-color: var(--color-bg-white);
    padding: 24px;
    border-radius: 8px;
    margin-bottom: 24px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.results-section h3 {
    margin: 0 0 16px 0;
    color: var(--color-bg-dark);
    font-size: 18px;
    font-weight: 600;
}

.results-section.success {
    border-left: 4px solid var(--color-success);
}

.results-section.error-section {
    border-left: 4px solid var(--color-primary);
}

.results-list {
    list-style: none;
    padding: 0;
    margin: 0 0 24px 0;
}

.dashboard-btn {
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
}

.dashboard-btn:hover {
    background-color: #cc2222;
}

.result-item {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 12px;
    background-color: var(--color-bg);
    border-radius: 6px;
    margin-bottom: 8px;
}

.check-icon {
    width: 20px;
    height: 20px;
    color: var(--color-success);
    flex-shrink: 0;
    margin-top: 2px;
}

.error-icon {
    width: 20px;
    height: 20px;
    color: var(--color-primary);
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
    color: var(--color-bg-dark);
}

.result-details {
    font-size: 14px;
    color: var(--color-text-light);
}

.result-error {
    font-size: 14px;
    color: var(--color-primary);
}
</style>
