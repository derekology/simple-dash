<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
} from 'chart.js'
import { Line, Bar } from 'vue-chartjs'
import { platformMap } from '@/resources/maps'
import SearchDropdown from '@/components/SearchDropdown.vue'
import MultiSearchDropdown from '@/components/MultiSearchDropdown.vue'

import type { TooltipItem } from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
)

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

const router = useRouter()
const campaigns = ref<CampaignData[]>([])
const activeViewTab = ref<'individual' | 'trends'>('individual')
const activeCampaignTab = ref(0)
const selectedTrendCampaigns = ref<number[]>([])
const hasFailedUploads = ref(false)
const failedUploadCount = ref(0)

onMounted(() => {
  const campaignsJson = sessionStorage.getItem('campaigns')
  if (campaignsJson) {
    try {
      const parsedCampaigns = JSON.parse(campaignsJson) as CampaignData[]
      campaigns.value = parsedCampaigns.sort((a, b) =>
        new Date(a.sent_at).getTime() - new Date(b.sent_at).getTime()
      )
      if (campaigns.value.length > 1) {
        activeViewTab.value = 'trends'
        // Select all campaigns by default for trends
        selectedTrendCampaigns.value = campaigns.value.map((_, index) => index)
      }
    } catch (error) {
      console.error('Failed to parse campaigns:', error)
      router.push('/')
    }
  } else {
    router.push('/')
  }

  const failedUploadsJson = sessionStorage.getItem('failedUploads')
  if (failedUploadsJson) {
    try {
      const failedUploads = JSON.parse(failedUploadsJson)
      if (Array.isArray(failedUploads) && failedUploads.length > 0) {
        hasFailedUploads.value = true
        failedUploadCount.value = failedUploads.length
      }
    } catch (error) {
      console.error('Failed to parse failed uploads:', error)
    }
  }
})

const activeCampaign = computed(() => campaigns.value[activeCampaignTab.value])

const campaignDropdownOptions = computed(() => {
  return campaigns.value.map((campaign, index) => ({
    value: index,
    label: campaign.email_title || campaign.subject || `Campaign ${index + 1}`,
    subtitle: campaign.subject
  }))
})

const selectedTrendCampaignsData = computed(() => {
  return selectedTrendCampaigns.value
    .map(index => campaigns.value[index])
    .filter(Boolean)
})

// Aggregated metrics for selected trend campaigns
const aggregatedMetrics = computed(() => {
  const data = selectedTrendCampaignsData.value
  if (data.length === 0) {
    return {
      totalCampaigns: 0,
      avgDelivered: 0,
      avgOpens: 0,
      avgOpenRate: 0,
      avgClicks: 0,
      avgClickRate: 0,
      avgCtor: 0,
      avgUnsubscribes: 0,
      avgUnsubscribeRate: 0,
      avgHardBounces: 0,
      avgHardBounceRate: 0,
      avgSoftBounces: 0,
      avgSoftBounceRate: 0,
    }
  }

  const sum = (field: keyof CampaignData) => {
    return data.reduce((acc, c) => acc + (Number(c?.[field]) || 0), 0)
  }

  const avg = (field: keyof CampaignData) => {
    return sum(field) / data.length
  }

  return {
    totalCampaigns: data.length,
    avgDelivered: avg('delivered'),
    avgOpens: avg('opens'),
    avgOpenRate: avg('open_rate'),
    avgClicks: avg('clicks'),
    avgClickRate: avg('click_rate'),
    avgCtor: avg('ctor'),
    avgUnsubscribes: avg('unsubscribes'),
    avgUnsubscribeRate: avg('unsubscribe_rate'),
    avgHardBounces: avg('hard_bounces'),
    avgHardBounceRate: avg('hard_bounce_rate'),
    avgSoftBounces: avg('soft_bounces'),
    avgSoftBounceRate: avg('soft_bounce_rate'),
  }
})

const detectOutliers = () => {
  if (campaigns.value.length < 4) return [] // Need at least 4 campaigns for IQR

  const deliveries = campaigns.value.map(c => c?.delivered || 0).sort((a, b) => a - b)

  const q1Index = Math.floor(deliveries.length * 0.25)
  const q3Index = Math.floor(deliveries.length * 0.75)
  const q1 = deliveries[q1Index] ?? 0
  const q3 = deliveries[q3Index] ?? 0
  const iqr = q3 - q1

  const lowerBound = q1 - 1.5 * iqr
  const upperBound = q3 + 1.5 * iqr

  const outlierIndices: number[] = []
  campaigns.value.forEach((campaign, index) => {
    const delivered = campaign?.delivered || 0
    if (delivered < lowerBound || delivered > upperBound) {
      outlierIndices.push(index)
    }
  })

  return outlierIndices
}

const detectLowVolume = () => {
  if (campaigns.value.length < 2) return []

  const delivered = campaigns.value
    .map(c => c?.delivered || 0)
    .filter(d => d > 0)

  if (delivered.length < 2) return []

  // Calculate median
  const sorted = [...delivered].sort((a, b) => a - b)
  const mid = Math.floor(sorted.length / 2)
  const median = sorted.length % 2 === 0
    ? ((sorted[mid - 1] ?? 0) + (sorted[mid] ?? 0)) / 2
    : (sorted[mid] ?? 0)

  // Threshold: less than 50% of median
  const threshold = median * 0.5

  const lowVolumeIndices: number[] = []
  campaigns.value.forEach((campaign, index) => {
    const delivered = campaign?.delivered || 0
    if (delivered > 0 && delivered < threshold) {
      lowVolumeIndices.push(index)
    }
  })

  return lowVolumeIndices
}

const toggleOutliers = () => {
  const outlierIndices = detectOutliers()

  if (outlierIndices.length === 0) {
    return
  }

  const anyOutlierSelected = outlierIndices.some(idx => selectedTrendCampaigns.value.includes(idx))

  if (anyOutlierSelected) {
    selectedTrendCampaigns.value = selectedTrendCampaigns.value.filter(
      idx => !outlierIndices.includes(idx)
    )
  } else {
    const newSelection = [...selectedTrendCampaigns.value]
    outlierIndices.forEach(idx => {
      if (!newSelection.includes(idx)) {
        newSelection.push(idx)
      }
    })
    selectedTrendCampaigns.value = newSelection
  }
}

const toggleLowVolume = () => {
  const lowVolumeIndices = detectLowVolume()

  if (lowVolumeIndices.length === 0) {
    return
  }

  const anyLowVolumeSelected = lowVolumeIndices.some(idx => selectedTrendCampaigns.value.includes(idx))

  if (anyLowVolumeSelected) {
    selectedTrendCampaigns.value = selectedTrendCampaigns.value.filter(
      idx => !lowVolumeIndices.includes(idx)
    )
  } else {
    const newSelection = [...selectedTrendCampaigns.value]
    lowVolumeIndices.forEach(idx => {
      if (!newSelection.includes(idx)) {
        newSelection.push(idx)
      }
    })
    selectedTrendCampaigns.value = newSelection
  }
}

const outliersInfo = computed(() => {
  if (campaigns.value.length < 4) {
    return {
      count: 0,
      anySelected: false,
      buttonText: 'Select Outliers'
    }
  }

  const outlierIndices = detectOutliers()
  const anySelected = outlierIndices.some(idx => selectedTrendCampaigns.value.includes(idx))

  return {
    count: outlierIndices.length,
    anySelected,
    buttonText: anySelected ? 'Remove Outliers' : 'Select Outliers'
  }
})

const lowVolumeInfo = computed(() => {
  if (campaigns.value.length < 2) {
    return {
      count: 0,
      anySelected: false,
      buttonText: 'Select Low Volume'
    }
  }

  const lowVolumeIndices = detectLowVolume()
  const anySelected = lowVolumeIndices.some(idx => selectedTrendCampaigns.value.includes(idx))

  return {
    count: lowVolumeIndices.length,
    anySelected,
    buttonText: anySelected ? 'Remove Low Volume' : 'Select Low Volume'
  }
})

const calculateTrendline = (dataPoints: number[]) => {
  const n = dataPoints.length
  if (n < 2) return dataPoints

  const xValues = Array.from({ length: n }, (_, i) => i)
  const sumX = xValues.reduce((sum, x) => sum + x, 0)
  const sumY = dataPoints.reduce((sum, y) => sum + y, 0)
  const sumXY = xValues.reduce((sum, x, i) => sum + x * (dataPoints[i] ?? 0), 0)
  const sumXX = xValues.reduce((sum, x) => sum + x * x, 0)

  const slope = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX)
  const intercept = (sumY - slope * sumX) / n

  return xValues.map(x => slope * x + intercept)
}

const formatPercent = (value: number | null) => {
  return value != null ? `${(value * 100).toFixed(2)}%` : 'N/A'
}

const formatNumber = (value: number | null) => {
  return value != null ? value.toLocaleString() : 'N/A'
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleString()
}

const mapPlatform = (platformKey: string) => {
  return platformMap[platformKey.toLowerCase() as keyof typeof platformMap] || platformKey
}

const engagementData = computed(() => {
  if (!activeCampaign.value) return null
  const c = activeCampaign.value
  return {
    labels: ['Delivered', 'Opened', 'Clicked'],
    datasets: [{
      label: 'Count',
      data: [c.delivered, c.opens, c.clicks],
      backgroundColor: ['#dd3333', '#ff6666', '#ff9999']
    }]
  }
})

const ratesData = computed(() => {
  if (!activeCampaign.value) return null
  const c = activeCampaign.value
  return {
    labels: ['Open Rate', 'Click Rate', 'CTOR'],
    datasets: [{
      label: 'Rate',
      data: [
        c.open_rate ? c.open_rate * 100 : 0,
        c.click_rate ? c.click_rate * 100 : 0,
        c.ctor ? c.ctor * 100 : 0
      ],
      backgroundColor: ['#dd3333', '#ff6666', '#ff9999']
    }]
  }
})

const negativeMetricsData = computed(() => {
  if (!activeCampaign.value) return null
  const c = activeCampaign.value
  return {
    labels: ['Unsubscribes', 'Hard Bounces', 'Soft Bounces'],
    datasets: [{
      label: 'Count',
      data: [c.unsubscribes || 0, c.hard_bounces || 0, c.soft_bounces || 0],
      backgroundColor: ['#222222', '#666666', '#999999']
    }]
  }
})

const deliveriesTrend = computed(() => {
  if (selectedTrendCampaignsData.value.length === 0) return null
  const data = selectedTrendCampaignsData.value.map(c => c?.delivered || 0)
  const trendline = calculateTrendline(data)

  return {
    labels: selectedTrendCampaignsData.value.map(c => c?.email_title || c?.subject || 'Untitled'),
    datasets: [
      {
        label: 'Deliveries',
        data: data,
        borderColor: '#dd3333',
        backgroundColor: 'rgba(221, 51, 51, 0.1)',
        tension: 0.4,
        pointRadius: 4,
        pointHoverRadius: 6
      },
      {
        label: 'Trend',
        data: trendline,
        borderColor: '#222222',
        backgroundColor: 'transparent',
        borderDash: [5, 5],
        borderWidth: 2,
        pointRadius: 0,
        pointHoverRadius: 0,
        tension: 0
      }
    ]
  }
})

const opensTrend = computed(() => {
  if (selectedTrendCampaignsData.value.length === 0) return null
  const data = selectedTrendCampaignsData.value.map(c => c?.opens || 0)
  const trendline = calculateTrendline(data)

  return {
    labels: selectedTrendCampaignsData.value.map(c => c?.email_title || c?.subject || 'Untitled'),
    datasets: [
      {
        label: 'Opens',
        data: data,
        borderColor: '#dd3333',
        backgroundColor: 'rgba(221, 51, 51, 0.1)',
        tension: 0.4,
        pointRadius: 4,
        pointHoverRadius: 6
      },
      {
        label: 'Trend',
        data: trendline,
        borderColor: '#222222',
        backgroundColor: 'transparent',
        borderDash: [5, 5],
        borderWidth: 2,
        pointRadius: 0,
        pointHoverRadius: 0,
        tension: 0
      }
    ]
  }
})

const clicksTrend = computed(() => {
  if (selectedTrendCampaignsData.value.length === 0) return null
  const data = selectedTrendCampaignsData.value.map(c => c?.clicks || 0)
  const trendline = calculateTrendline(data)

  return {
    labels: selectedTrendCampaignsData.value.map(c => c?.email_title || c?.subject || 'Untitled'),
    datasets: [
      {
        label: 'Clicks',
        data: data,
        borderColor: '#dd3333',
        backgroundColor: 'rgba(221, 51, 51, 0.1)',
        tension: 0.4,
        pointRadius: 4,
        pointHoverRadius: 6
      },
      {
        label: 'Trend',
        data: trendline,
        borderColor: '#222222',
        backgroundColor: 'transparent',
        borderDash: [5, 5],
        borderWidth: 2,
        pointRadius: 0,
        pointHoverRadius: 0,
        tension: 0
      }
    ]
  }
})

const openRateTrend = computed(() => {
  if (selectedTrendCampaignsData.value.length === 0) return null
  const data = selectedTrendCampaignsData.value.map(c => c?.open_rate ? c.open_rate * 100 : 0)
  const trendline = calculateTrendline(data)

  return {
    labels: selectedTrendCampaignsData.value.map(c => c?.email_title || c?.subject || 'Untitled'),
    datasets: [
      {
        label: 'Open Rate (%)',
        data: data,
        borderColor: '#dd3333',
        backgroundColor: 'rgba(221, 51, 51, 0.1)',
        tension: 0.4,
        pointRadius: 4,
        pointHoverRadius: 6
      },
      {
        label: 'Trend',
        data: trendline,
        borderColor: '#222222',
        backgroundColor: 'transparent',
        borderDash: [5, 5],
        borderWidth: 2,
        pointRadius: 0,
        pointHoverRadius: 0,
        tension: 0
      }
    ]
  }
})

const clickRateTrend = computed(() => {
  if (selectedTrendCampaignsData.value.length === 0) return null
  const data = selectedTrendCampaignsData.value.map(c => c?.click_rate ? c.click_rate * 100 : 0)
  const trendline = calculateTrendline(data)

  return {
    labels: selectedTrendCampaignsData.value.map(c => c?.email_title || c?.subject || 'Untitled'),
    datasets: [
      {
        label: 'Click Rate (%)',
        data: data,
        borderColor: '#dd3333',
        backgroundColor: 'rgba(221, 51, 51, 0.1)',
        tension: 0.4,
        pointRadius: 4,
        pointHoverRadius: 6
      },
      {
        label: 'Trend',
        data: trendline,
        borderColor: '#222222',
        backgroundColor: 'transparent',
        borderDash: [5, 5],
        borderWidth: 2,
        pointRadius: 0,
        pointHoverRadius: 0,
        tension: 0
      }
    ]
  }
})

const ctorTrend = computed(() => {
  if (selectedTrendCampaignsData.value.length === 0) return null
  const data = selectedTrendCampaignsData.value.map(c => c?.ctor ? c.ctor * 100 : 0)
  const trendline = calculateTrendline(data)

  return {
    labels: selectedTrendCampaignsData.value.map(c => c?.email_title || c?.subject || 'Untitled'),
    datasets: [
      {
        label: 'Click-to-Open Rate (%)',
        data: data,
        borderColor: '#dd3333',
        backgroundColor: 'rgba(221, 51, 51, 0.1)',
        tension: 0.4,
        pointRadius: 4,
        pointHoverRadius: 6
      },
      {
        label: 'Trend',
        data: trendline,
        borderColor: '#222222',
        backgroundColor: 'transparent',
        borderDash: [5, 5],
        borderWidth: 2,
        pointRadius: 0,
        pointHoverRadius: 0,
        tension: 0
      }
    ]
  }
})

const unsubscribeRateTrend = computed(() => {
  if (selectedTrendCampaignsData.value.length === 0) return null
  const data = selectedTrendCampaignsData.value.map(c => c?.unsubscribe_rate ? c.unsubscribe_rate * 100 : 0)
  const trendline = calculateTrendline(data)

  return {
    labels: selectedTrendCampaignsData.value.map(c => c?.email_title || c?.subject || 'Untitled'),
    datasets: [
      {
        label: 'Unsubscribe Rate (%)',
        data: data,
        borderColor: '#999999',
        backgroundColor: 'rgba(34, 34, 34, 0.1)',
        tension: 0.4,
        pointRadius: 4,
        pointHoverRadius: 6
      },
      {
        label: 'Trend',
        data: trendline,
        borderColor: '#222222',
        backgroundColor: 'transparent',
        borderDash: [5, 5],
        borderWidth: 2,
        pointRadius: 0,
        pointHoverRadius: 0,
        tension: 0
      }
    ]
  }
})

const hardBounceRateTrend = computed(() => {
  if (selectedTrendCampaignsData.value.length === 0) return null
  const data = selectedTrendCampaignsData.value.map(c => c?.hard_bounce_rate ? c.hard_bounce_rate * 100 : 0)
  const trendline = calculateTrendline(data)

  return {
    labels: selectedTrendCampaignsData.value.map(c => c?.email_title || c?.subject || 'Untitled'),
    datasets: [
      {
        label: 'Hard Bounce Rate (%)',
        data: data,
        borderColor: '#666666',
        backgroundColor: 'rgba(102, 102, 102, 0.1)',
        tension: 0.4,
        pointRadius: 4,
        pointHoverRadius: 6
      },
      {
        label: 'Trend',
        data: trendline,
        borderColor: '#222222',
        backgroundColor: 'transparent',
        borderDash: [5, 5],
        borderWidth: 2,
        pointRadius: 0,
        pointHoverRadius: 0,
        tension: 0
      }
    ]
  }
})

const softBounceRateTrend = computed(() => {
  if (selectedTrendCampaignsData.value.length === 0) return null
  const data = selectedTrendCampaignsData.value.map(c => c?.soft_bounce_rate ? c.soft_bounce_rate * 100 : 0)
  const trendline = calculateTrendline(data)

  return {
    labels: selectedTrendCampaignsData.value.map(c => c?.email_title || c?.subject || 'Untitled'),
    datasets: [
      {
        label: 'Soft Bounce Rate (%)',
        data: data,
        borderColor: '#222222',
        backgroundColor: 'rgba(153, 153, 153, 0.1)',
        tension: 0.4,
        pointRadius: 4,
        pointHoverRadius: 6
      },
      {
        label: 'Trend',
        data: trendline,
        borderColor: '#222222',
        backgroundColor: 'transparent',
        borderDash: [5, 5],
        borderWidth: 2,
        pointRadius: 0,
        pointHoverRadius: 0,
        tension: 0
      }
    ]
  }
})

const heatmapData = computed(() => {
  if (selectedTrendCampaignsData.value.length === 0) return null

  const daysOfWeek = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
  const hours = Array.from({ length: 24 }, (_, i) => i)

  const grid: { count: number; totalOpenRate: number; totalDelivered: number; campaigns: string[] }[][] =
    daysOfWeek.map(() => hours.map(() => ({ count: 0, totalOpenRate: 0, totalDelivered: 0, campaigns: [] })))

  selectedTrendCampaignsData.value.forEach(campaign => {
    if (!campaign) return
    const date = new Date(campaign.sent_at)
    const day = date.getDay()
    const hour = date.getHours()

    if (!grid[day] || !grid[day][hour]) return

    grid[day][hour].count++
    grid[day][hour].totalOpenRate += (campaign.open_rate || 0) * 100
    grid[day][hour].totalDelivered += campaign.delivered || 0
    grid[day][hour].campaigns.push(campaign.email_title || campaign.subject || 'Untitled')
  })

  const cells = grid.flatMap((dayRow, dayIndex) =>
    dayRow.map((cell, hourIndex) => ({
      day: daysOfWeek[dayIndex],
      hour: hourIndex,
      avgOpenRate: cell.count > 0 ? cell.totalOpenRate / cell.count : 0,
      totalDelivered: cell.totalDelivered,
      count: cell.count,
      campaigns: cell.campaigns
    }))
  ).filter(cell => cell.count > 0)

  return { daysOfWeek, hours, cells }
})

const getHeatmapCellStyle = (dayIndex: number, hour: number) => {
  const cell = heatmapData.value?.cells.find(
    c => c.day === heatmapData.value!.daysOfWeek[dayIndex] && c.hour === hour
  )

  if (!cell || cell.count === 0) {
    return { backgroundColor: '#f5f5f5' }
  }

  const intensity = Math.min(cell.avgOpenRate / 100, 1)
  return { backgroundColor: `rgba(221, 51, 51, ${0.2 + intensity * 0.8})` }
}

const getHeatmapCellValue = (dayIndex: number, hour: number) => {
  const cell = heatmapData.value?.cells.find(
    c => c.day === heatmapData.value!.daysOfWeek[dayIndex] && c.hour === hour
  )

  if (!cell || cell.count === 0) return ''
  return `${cell.avgOpenRate.toFixed(1)}%`
}

const getHeatmapCellTooltip = (dayIndex: number, hour: number) => {
  const cell = heatmapData.value?.cells.find(
    c => c.day === heatmapData.value!.daysOfWeek[dayIndex] && c.hour === hour
  )

  if (!cell || cell.count === 0) return 'No campaigns sent at this time'

  const campaigns = cell.campaigns.join(', ')
  return `${heatmapData.value!.daysOfWeek[dayIndex]} ${hour}:00\nAvg Open Rate: ${cell.avgOpenRate.toFixed(1)}%\nTotal Delivered: ${cell.totalDelivered.toLocaleString()}\nCampaigns (${cell.count}): ${campaigns}`
}

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    }
  }
}

const trendChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: true,
      position: 'top' as const
    },
    tooltip: {
      callbacks: {
        title: (context: TooltipItem<'line'>[]) => {
          return context[0]?.label ?? ''
        }
      }
    }
  },
  scales: {
    x: {
      display: false
    },
    y: {
      beginAtZero: true
    }
  }
}
</script>

<template>
  <div class="dashboard-view">
    <main class="main-content">
      <div v-if="hasFailedUploads" class="failed-upload-banner">
        <div class="failed-upload-banner-content">
          <span class="failed-upload-icon">⚠️</span>
          <span class="failed-upload-text">
            {{ failedUploadCount }} {{ failedUploadCount === 1 ? 'file' : 'files' }} failed to upload. Only successfully
            parsed campaigns are shown.
          </span>
        </div>
      </div>
      <div class="content-wrapper">
        <div class="view-tabs">
          <button :class="['view-tab', { active: activeViewTab === 'individual' }]"
            @click="activeViewTab = 'individual'">
            Individual Campaigns
          </button>
          <button v-if="campaigns.length > 1" :class="['view-tab', { active: activeViewTab === 'trends' }]"
            @click="activeViewTab = 'trends'">
            Trends Across Campaigns
          </button>
        </div>

        <!-- Individual Campaign View -->
        <div v-if="activeViewTab === 'individual'">
          <!-- Campaign Dropdown -->
          <div v-if="campaigns.length > 0" class="campaign-selector">
            <SearchDropdown :options="campaignDropdownOptions" v-model="activeCampaignTab"
              placeholder="Select a campaign..." />
          </div>

          <div v-if="activeCampaign" class="campaign-info">
            <div class="info-grid">
              <div class="info-card">
                <span class="info-label">Platform</span>
                <span class="info-value">{{ mapPlatform(activeCampaign.platform) }}</span>
              </div>
              <div class="info-card">
                <span class="info-label">Subject</span>
                <span class="info-value">{{ activeCampaign.subject }}</span>
              </div>
              <div class="info-card">
                <span class="info-label">Sent At</span>
                <span class="info-value">{{ formatDate(activeCampaign.sent_at) }}</span>
              </div>
            </div>
          </div>

          <!-- Positive Metrics Section -->
          <div v-if="activeCampaign" class="metrics-section">
            <h2 class="section-title">Positive Metrics</h2>
            <div class="metrics-row">
              <div class="stats-column">
                <div class="stat-card">
                  <div class="stat-header">
                    <h3>Deliveries</h3>
                  </div>
                  <div class="stat-value">{{ formatNumber(activeCampaign.delivered) }}</div>
                </div>

                <div class="stat-card">
                  <div class="stat-header">
                    <h3>Opens</h3>
                  </div>
                  <div class="stat-value">{{ formatNumber(activeCampaign.opens) }}</div>
                  <div class="stat-rate">{{ formatPercent(activeCampaign.open_rate) }}</div>
                </div>

                <div class="stat-card">
                  <div class="stat-header">
                    <h3>Clicks</h3>
                  </div>
                  <div class="stat-value">{{ formatNumber(activeCampaign.clicks) }}</div>
                  <div class="stat-rate">{{ formatPercent(activeCampaign.click_rate) }}</div>
                </div>

                <div class="stat-card">
                  <div class="stat-header">
                    <h3>Click-to-Open Rate</h3>
                  </div>
                  <div class="stat-value">{{ formatPercent(activeCampaign.ctor) }}</div>
                </div>
              </div>

              <div class="charts-column">
                <div class="chart-card">
                  <h3>Engagement Funnel</h3>
                  <div class="chart-container">
                    <Bar v-if="engagementData" :data="engagementData" :options="chartOptions" />
                  </div>
                </div>

                <div class="chart-card">
                  <h3>Engagement Rates</h3>
                  <div class="chart-container">
                    <Bar v-if="ratesData" :data="ratesData" :options="chartOptions" />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-if="activeCampaign" class="metrics-section">
            <h2 class="section-title">Negative Metrics</h2>
            <div class="metrics-row">
              <div class="stats-column">
                <div class="stat-card negative">
                  <div class="stat-header">
                    <h3>Unsubscribes</h3>
                  </div>
                  <div class="stat-value">{{ formatNumber(activeCampaign.unsubscribes) }}</div>
                  <div class="stat-rate">{{ formatPercent(activeCampaign.unsubscribe_rate) }}</div>
                </div>

                <div class="stat-card negative">
                  <div class="stat-header">
                    <h3>Hard Bounces</h3>
                  </div>
                  <div class="stat-value">{{ formatNumber(activeCampaign.hard_bounces) }}</div>
                  <div class="stat-rate">{{ formatPercent(activeCampaign.hard_bounce_rate) }}</div>
                </div>

                <div class="stat-card negative">
                  <div class="stat-header">
                    <h3>Soft Bounces</h3>
                  </div>
                  <div class="stat-value">{{ formatNumber(activeCampaign.soft_bounces) }}</div>
                  <div class="stat-rate">{{ formatPercent(activeCampaign.soft_bounce_rate) }}</div>
                </div>
              </div>

              <div class="charts-column">
                <div class="chart-card">
                  <h3>Negative Metrics</h3>
                  <div class="chart-container">
                    <Bar v-if="negativeMetricsData" :data="negativeMetricsData" :options="chartOptions" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="activeViewTab === 'trends' && campaigns.length > 1" class="trends-section">
          <div class="campaign-selector">
            <MultiSearchDropdown :options="campaignDropdownOptions" v-model="selectedTrendCampaigns"
              :show-outliers="true" :outliers-count="outliersInfo.count" :outliers-button-text="outliersInfo.buttonText"
              :show-low-volume="true" :low-volume-count="lowVolumeInfo.count" :low-volume-button-text="lowVolumeInfo.buttonText"
              @toggle-outliers="toggleOutliers" @toggle-low-volume="toggleLowVolume" />
          </div>

          <div class="charts-grid">
            <div class="chart-card wide">
              <div class="chart-header">
                <h3>Deliveries</h3>
                <div class="chart-metrics">
                  <span class="metric-label">Average:</span>
                  <span class="metric-value">{{ formatNumber(aggregatedMetrics.avgDelivered) }}</span>
                </div>
              </div>
              <div class="chart-container">
                <Line v-if="deliveriesTrend" :data="deliveriesTrend" :options="trendChartOptions" />
              </div>
            </div>

            <div class="chart-card wide">
              <div class="chart-header">
                <h3>Opens</h3>
                <div class="chart-metrics">
                  <span class="metric-label">Average:</span>
                  <span class="metric-value">{{ formatNumber(aggregatedMetrics.avgOpens) }}</span>
                </div>
              </div>
              <div class="chart-container">
                <Line v-if="opensTrend" :data="opensTrend" :options="trendChartOptions" />
              </div>
            </div>

            <div class="chart-card wide">
              <div class="chart-header">
                <h3>Clicks</h3>
                <div class="chart-metrics">
                  <span class="metric-label">Average:</span>
                  <span class="metric-value">{{ formatNumber(aggregatedMetrics.avgClicks) }}</span>
                </div>
              </div>
              <div class="chart-container">
                <Line v-if="clicksTrend" :data="clicksTrend" :options="trendChartOptions" />
              </div>
            </div>

            <div class="chart-card">
              <div class="chart-header">
                <h3>Open Rate</h3>
                <div class="chart-metrics">
                  <span class="metric-label">Avg Rate:</span>
                  <span class="metric-value">{{ formatPercent(aggregatedMetrics.avgOpenRate) }}</span>
                </div>
              </div>
              <div class="chart-container">
                <Line v-if="openRateTrend" :data="openRateTrend" :options="trendChartOptions" />
              </div>
            </div>

            <div class="chart-card">
              <div class="chart-header">
                <h3>Click Rate</h3>
                <div class="chart-metrics">
                  <span class="metric-label">Avg Rate:</span>
                  <span class="metric-value">{{ formatPercent(aggregatedMetrics.avgClickRate) }}</span>
                </div>
              </div>
              <div class="chart-container">
                <Line v-if="clickRateTrend" :data="clickRateTrend" :options="trendChartOptions" />
              </div>
            </div>

            <div class="chart-card">
              <div class="chart-header">
                <h3>CTOR</h3>
                <div class="chart-metrics">
                  <span class="metric-label">Avg Rate:</span>
                  <span class="metric-value">{{ formatPercent(aggregatedMetrics.avgCtor) }}</span>
                </div>
              </div>
              <div class="chart-container">
                <Line v-if="ctorTrend" :data="ctorTrend" :options="trendChartOptions" />
              </div>
            </div>

            <div class="chart-card">
              <div class="chart-header">
                <h3>Unsubscribe %</h3>
                <div class="chart-metrics-group">
                  <div class="chart-metrics">
                    <span class="metric-label">Avg Rate:</span>
                    <span class="metric-value">{{ formatPercent(aggregatedMetrics.avgUnsubscribeRate) }}</span>
                  </div>
                  <div class="chart-metrics">
                    <span class="metric-label">Avg Count:</span>
                    <span class="metric-value">{{ formatNumber(aggregatedMetrics.avgUnsubscribes) }}</span>
                  </div>
                </div>
              </div>
              <div class="chart-container">
                <Line v-if="unsubscribeRateTrend" :data="unsubscribeRateTrend" :options="trendChartOptions" />
              </div>
            </div>

            <div class="chart-card">
              <div class="chart-header">
                <h3>Hard Bounce %</h3>
                <div class="chart-metrics-group">
                  <div class="chart-metrics">
                    <span class="metric-label">Avg Rate:</span>
                    <span class="metric-value">{{ formatPercent(aggregatedMetrics.avgHardBounceRate) }}</span>
                  </div>
                  <div class="chart-metrics">
                    <span class="metric-label">Avg Count:</span>
                    <span class="metric-value">{{ formatNumber(aggregatedMetrics.avgHardBounces) }}</span>
                  </div>
                </div>
              </div>
              <div class="chart-container">
                <Line v-if="hardBounceRateTrend" :data="hardBounceRateTrend" :options="trendChartOptions" />
              </div>
            </div>

            <div class="chart-card">
              <div class="chart-header">
                <h3>Soft Bounce %</h3>
                <div class="chart-metrics-group">
                  <div class="chart-metrics">
                    <span class="metric-label">Avg Rate:</span>
                    <span class="metric-value">{{ formatPercent(aggregatedMetrics.avgSoftBounceRate) }}</span>
                  </div>
                  <div class="chart-metrics">
                    <span class="metric-label">Avg Count:</span>
                    <span class="metric-value">{{ formatNumber(aggregatedMetrics.avgSoftBounces) }}</span>
                  </div>
                </div>
              </div>
              <div class="chart-container">
                <Line v-if="softBounceRateTrend" :data="softBounceRateTrend" :options="trendChartOptions" />
              </div>
            </div>
          </div>

          <div v-if="heatmapData" class="heatmap-section">
            <h2 class="section-title">Send Time to Open Rate</h2>
            <p class="section-description">Darker cells indicate higher open rates at that day/time combination. Hover
              for more details.</p>

            <div class="heatmap-container">
              <div class="heatmap-grid">
                <div class="heatmap-y-axis">
                  <div class="y-axis-label"></div>
                  <div v-for="hour in 24" :key="hour" class="y-axis-label">
                    {{ hour - 1 }}:00
                  </div>
                </div>

                <div class="heatmap-content">
                  <div class="heatmap-x-axis">
                    <div v-for="day in heatmapData.daysOfWeek" :key="day" class="x-axis-label">
                      {{ day }}
                    </div>
                  </div>

                  <div class="heatmap-rows">
                    <div v-for="hour in 24" :key="hour" class="heatmap-row">
                      <div v-for="(day, dayIndex) in heatmapData.daysOfWeek" :key="day" class="heatmap-cell"
                        :style="getHeatmapCellStyle(dayIndex, hour - 1)"
                        :title="getHeatmapCellTooltip(dayIndex, hour - 1)">
                        <span class="cell-value">{{ getHeatmapCellValue(dayIndex, hour - 1) }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div class="heatmap-legend">
                <span class="legend-label">Open Rate:</span>
                <div class="legend-gradient">
                  <span class="legend-text">0%</span>
                  <div class="legend-bar"></div>
                  <span class="legend-text">High</span>
                </div>
              </div>

            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.main-content {
  background-color: var(--color-bg);
}

.content-wrapper {
  max-width: 1200px;
  padding: 32px;
  margin: 0 auto;
}

.failed-upload-banner {
  background: var(--color-bg-warning-gradient);
  padding: 0.5rem 1rem;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: relative;
  z-index: 10;
  height: var(--top-banner-height)
}

.failed-upload-banner-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.failed-upload-icon {
  font-size: 1.25rem;
  margin-top: -5px;
}

.failed-upload-text {
  font-size: 0.95rem;
  font-weight: 500;
}

.view-tabs {
  display: flex;
  gap: 0;
  margin-bottom: 32px;
  justify-content: start;
  border-bottom: 3px solid var(--color-border-light);
}

.view-tab {
  padding: 16px 32px;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-light);
  cursor: pointer;
  transition: all 0.2s ease;
  margin-bottom: -3px;
}

.view-tab:hover {
  color: var(--color-primary);
}

.view-tab.active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}

.campaign-selector {
  margin-bottom: 24px;
  max-width: 600px;
}

.campaign-info {
  background-color: var(--color-bg-white);
  padding: 24px;
  border-radius: 8px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.info-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-light);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-value {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-bg-dark);
}

.metrics-section {
  margin-bottom: 48px;
}

.metrics-row {
  display: grid;
  grid-template-columns: 350px 1fr;
  gap: 32px;
  align-items: start;
}

.stats-column {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.charts-column {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.stat-card {
  background-color: var(--color-bg-white);
  padding: 20px;
  border-radius: 8px;
  border-left: 4px solid var(--color-primary);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.stat-card.negative {
  border-left-color: var(--color-text-light);
}

.stat-header h3 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-light);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: var(--color-bg-dark);
  margin-bottom: 4px;
}

.stat-rate {
  font-size: 16px;
  font-weight: 500;
  color: var(--color-primary);
}

.stat-card.negative .stat-rate {
  color: var(--color-text-light);
}

.section-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-bg-dark);
  margin: 0 0 24px 0;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 24px;
}

.chart-card {
  background-color: var(--color-bg-white);
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chart-card.wide {
  grid-column: 1 / -1;
}

.chart-container {
  height: 300px;
  position: relative;
}

.trends-section {
  margin-top: 48px;
}

.aggregated-summary {
  display: flex;
  gap: 16px;
  margin-bottom: 32px;
  justify-content: center;
}

.summary-card {
  background-color: var(--color-bg-white);
  padding: 20px 32px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  text-align: center;
  border-top: 4px solid var(--color-primary);
}

.summary-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-light);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
}

.summary-value {
  font-size: 36px;
  font-weight: 700;
  color: var(--color-primary);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  gap: 4px;
}

.chart-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--color-bg-dark);
}

.chart-metrics-group {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
}

.chart-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 4px 8px;
  align-items: end;
  justify-content: flex-end;
}

.metric-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-light);
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.metric-value {
  font-size: 14px;
  font-weight: 700;
  color: #000000;
}

.heatmap-section {
  margin-top: 48px;
}

.section-description {
  font-size: 14px;
  color: var(--color-text-light);
  margin: -16px 0 24px 0;
}

.heatmap-container {
  background-color: var(--color-bg-white);
  padding: 32px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.heatmap-grid {
  display: flex;
  gap: 16px;
  overflow-x: auto;
}

.heatmap-y-axis {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.y-axis-label {
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 8px;
  font-size: 11px;
  color: var(--color-text-light);
  font-weight: 500;
  min-width: 45px;
}

.heatmap-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.heatmap-x-axis {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
  margin-bottom: 8px;
}

.x-axis-label {
  text-align: center;
  font-size: 12px;
  color: var(--color-text-light);
  font-weight: 600;
}

.heatmap-rows {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding-top: 12px;
}

.heatmap-row {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}

.heatmap-cell {
  aspect-ratio: 1;
  width: 100%;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: transform 0.2s ease;
  border: 1px solid var(--color-border-light);
}

.cell-value {
  font-size: 11px;
  font-weight: 600;
  color: var(--color-bg-dark);
}

.heatmap-legend {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid var(--color-border-light);
}

.legend-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-light);
}

.legend-gradient {
  display: flex;
  align-items: center;
  gap: 12px;
}

.legend-bar {
  width: 200px;
  height: 20px;
  background: linear-gradient(to right,
      rgba(221, 51, 51, 0.2) 0%,
      rgba(221, 51, 51, 1) 100%);
  border-radius: 4px;
  border: 1px solid var(--color-border-light);
}

.legend-text {
  font-size: 12px;
  color: var(--color-text-light);
}

@media (max-width: 768px) {
  .metrics-row {
    grid-template-columns: 1fr;
  }

  .charts-grid {
    grid-template-columns: 1fr;
  }

  .chart-card.wide {
    grid-column: 1;
  }
}
</style>
