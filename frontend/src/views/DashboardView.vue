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
      }
    } catch (error) {
      console.error('Failed to parse campaigns:', error)
      router.push('/')
    }
  } else {
    router.push('/')
  }
})

const activeCampaign = computed(() => campaigns.value[activeCampaignTab.value])

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
  if (campaigns.value.length <= 1) return null
  return {
    labels: campaigns.value.map(c => c.subject || 'Untitled'),
    datasets: [{
      label: 'Deliveries',
      data: campaigns.value.map(c => c.delivered),
      borderColor: '#dd3333',
      backgroundColor: 'rgba(221, 51, 51, 0.1)',
      tension: 0.4
    }]
  }
})

const opensTrend = computed(() => {
  if (campaigns.value.length <= 1) return null
  return {
    labels: campaigns.value.map(c => c.subject || 'Untitled'),
    datasets: [{
      label: 'Opens',
      data: campaigns.value.map(c => c.opens),
      borderColor: '#dd3333',
      backgroundColor: 'rgba(221, 51, 51, 0.1)',
      tension: 0.4
    }]
  }
})

const clicksTrend = computed(() => {
  if (campaigns.value.length <= 1) return null
  return {
    labels: campaigns.value.map(c => c.subject || 'Untitled'),
    datasets: [{
      label: 'Clicks',
      data: campaigns.value.map(c => c.clicks),
      borderColor: '#dd3333',
      backgroundColor: 'rgba(221, 51, 51, 0.1)',
      tension: 0.4
    }]
  }
})

const openRateTrend = computed(() => {
  if (campaigns.value.length <= 1) return null
  return {
    labels: campaigns.value.map(c => c.subject || 'Untitled'),
    datasets: [{
      label: 'Open Rate (%)',
      data: campaigns.value.map(c => c.open_rate ? c.open_rate * 100 : 0),
      borderColor: '#dd3333',
      backgroundColor: 'rgba(221, 51, 51, 0.1)',
      tension: 0.4
    }]
  }
})

const clickRateTrend = computed(() => {
  if (campaigns.value.length <= 1) return null
  return {
    labels: campaigns.value.map(c => c.subject || 'Untitled'),
    datasets: [{
      label: 'Click Rate (%)',
      data: campaigns.value.map(c => c.click_rate ? c.click_rate * 100 : 0),
      borderColor: '#dd3333',
      backgroundColor: 'rgba(221, 51, 51, 0.1)',
      tension: 0.4
    }]
  }
})

const ctorTrend = computed(() => {
  if (campaigns.value.length <= 1) return null
  return {
    labels: campaigns.value.map(c => c.subject || 'Untitled'),
    datasets: [{
      label: 'Click-to-Open Rate (%)',
      data: campaigns.value.map(c => c.ctor ? c.ctor * 100 : 0),
      borderColor: '#dd3333',
      backgroundColor: 'rgba(221, 51, 51, 0.1)',
      tension: 0.4
    }]
  }
})

const unsubscribeRateTrend = computed(() => {
  if (campaigns.value.length <= 1) return null
  return {
    labels: campaigns.value.map(c => c.subject || 'Untitled'),
    datasets: [{
      label: 'Unsubscribe Rate (%)',
      data: campaigns.value.map(c => c.unsubscribe_rate ? c.unsubscribe_rate * 100 : 0),
      borderColor: '#222222',
      backgroundColor: 'rgba(34, 34, 34, 0.1)',
      tension: 0.4
    }]
  }
})

const hardBounceRateTrend = computed(() => {
  if (campaigns.value.length <= 1) return null
  return {
    labels: campaigns.value.map(c => c.subject || 'Untitled'),
    datasets: [{
      label: 'Hard Bounce Rate (%)',
      data: campaigns.value.map(c => c.hard_bounce_rate ? c.hard_bounce_rate * 100 : 0),
      borderColor: '#666666',
      backgroundColor: 'rgba(102, 102, 102, 0.1)',
      tension: 0.4
    }]
  }
})

const softBounceRateTrend = computed(() => {
  if (campaigns.value.length <= 1) return null
  return {
    labels: campaigns.value.map(c => c.subject || 'Untitled'),
    datasets: [{
      label: 'Soft Bounce Rate (%)',
      data: campaigns.value.map(c => c.soft_bounce_rate ? c.soft_bounce_rate * 100 : 0),
      borderColor: '#999999',
      backgroundColor: 'rgba(153, 153, 153, 0.1)',
      tension: 0.4
    }]
  }
})

const heatmapData = computed(() => {
  if (campaigns.value.length <= 1) return null

  const daysOfWeek = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
  const hours = Array.from({ length: 24 }, (_, i) => i)

  const grid: { count: number; totalOpenRate: number; campaigns: string[] }[][] =
    daysOfWeek.map(() => hours.map(() => ({ count: 0, totalOpenRate: 0, campaigns: [] })))

  campaigns.value.forEach(campaign => {
    const date = new Date(campaign.sent_at)
    const day = date.getDay()
    const hour = date.getHours()

    if (!grid[day] || !grid[day][hour]) return

    grid[day][hour].count++
    grid[day][hour].totalOpenRate += (campaign.open_rate || 0) * 100
    grid[day][hour].campaigns.push(campaign.subject || 'Untitled')
  })

  const cells = grid.flatMap((dayRow, dayIndex) =>
    dayRow.map((cell, hourIndex) => ({
      day: daysOfWeek[dayIndex],
      hour: hourIndex,
      avgOpenRate: cell.count > 0 ? cell.totalOpenRate / cell.count : 0,
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
  return `${heatmapData.value!.daysOfWeek[dayIndex]} ${hour}:00\nAvg Open Rate: ${cell.avgOpenRate.toFixed(1)}%\nCampaigns (${cell.count}): ${campaigns}`
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
          <!-- Campaign Tabs -->
          <div v-if="campaigns.length > 1" class="tabs">
            <button v-for="(campaign, index) in campaigns" :key="index"
              :class="['tab', { active: activeCampaignTab === index }]" @click="activeCampaignTab = index">
              {{ campaign.subject || `Campaign ${index + 1}` }}
            </button>
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

          <!-- Negative Metrics Section -->
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

        <!-- Trends View -->
        <div v-if="activeViewTab === 'trends' && campaigns.length > 1" class="trends-section">
          <h2 class="section-title">Trends Over Time</h2>

          <div class="charts-grid">
            <div class="chart-card wide">
              <h3>Deliveries</h3>
              <div class="chart-container">
                <Line v-if="deliveriesTrend" :data="deliveriesTrend" :options="trendChartOptions" />
              </div>
            </div>

            <div class="chart-card wide">
              <h3>Opens</h3>
              <div class="chart-container">
                <Line v-if="opensTrend" :data="opensTrend" :options="trendChartOptions" />
              </div>
            </div>

            <div class="chart-card wide">
              <h3>Clicks</h3>
              <div class="chart-container">
                <Line v-if="clicksTrend" :data="clicksTrend" :options="trendChartOptions" />
              </div>
            </div>

            <div class="chart-card">
              <h3>Open Rate</h3>
              <div class="chart-container">
                <Line v-if="openRateTrend" :data="openRateTrend" :options="trendChartOptions" />
              </div>
            </div>

            <div class="chart-card">
              <h3>Click Rate</h3>
              <div class="chart-container">
                <Line v-if="clickRateTrend" :data="clickRateTrend" :options="trendChartOptions" />
              </div>
            </div>

            <div class="chart-card">
              <h3>CTOR</h3>
              <div class="chart-container">
                <Line v-if="ctorTrend" :data="ctorTrend" :options="trendChartOptions" />
              </div>
            </div>

            <div class="chart-card">
              <h3>Unsubscribe Rate</h3>
              <div class="chart-container">
                <Line v-if="unsubscribeRateTrend" :data="unsubscribeRateTrend" :options="trendChartOptions" />
              </div>
            </div>

            <div class="chart-card">
              <h3>Hard Bounce Rate</h3>
              <div class="chart-container">
                <Line v-if="hardBounceRateTrend" :data="hardBounceRateTrend" :options="trendChartOptions" />
              </div>
            </div>

            <div class="chart-card">
              <h3>Soft Bounce Rate</h3>
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
  background-color: #fafafa;
}

.content-wrapper {
  max-width: 1200px;
  padding: 32px;
  margin: 0 auto;
}

.view-tabs {
  display: flex;
  gap: 0;
  margin-bottom: 32px;
  justify-content: start;
  border-bottom: 3px solid #e0e0e0;
}

.view-tab {
  padding: 16px 32px;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  font-size: 16px;
  font-weight: 600;
  color: #666666;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-bottom: -3px;
}

.view-tab:hover {
  color: #dd3333;
}

.view-tab.active {
  color: #dd3333;
  border-bottom-color: #dd3333;
}

.tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  overflow-x: auto;
  padding-bottom: 8px;
  justify-content: start;
}

.tab {
  padding: 12px 24px;
  background-color: #ffffff;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-weight: 500;
  color: #222222;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.tab:hover {
  border-color: #dd3333;
}

.tab.active {
  background-color: #dd3333;
  border-color: #dd3333;
  color: #ffffff;
}

.campaign-info {
  background-color: #ffffff;
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
  color: #666666;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-value {
  font-size: 16px;
  font-weight: 600;
  color: #222222;
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
  background-color: #ffffff;
  padding: 20px;
  border-radius: 8px;
  border-left: 4px solid #dd3333;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.stat-card.negative {
  border-left-color: #666666;
}

.stat-header h3 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #666666;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #222222;
  margin-bottom: 4px;
}

.stat-rate {
  font-size: 16px;
  font-weight: 500;
  color: #dd3333;
}

.stat-card.negative .stat-rate {
  color: #666666;
}

.section-title {
  font-size: 24px;
  font-weight: 700;
  color: #222222;
  margin: 0 0 24px 0;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 24px;
}

.chart-card {
  background-color: #ffffff;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chart-card.wide {
  grid-column: 1 / -1;
}

.chart-card h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 600;
  color: #222222;
}

.chart-container {
  height: 300px;
  position: relative;
}

.trends-section {
  margin-top: 48px;
}

.heatmap-section {
  margin-top: 48px;
}

.section-description {
  font-size: 14px;
  color: #666666;
  margin: -16px 0 24px 0;
}

.heatmap-container {
  background-color: #ffffff;
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
  color: #666666;
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
  color: #666666;
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
  border: 1px solid #e0e0e0;
}

.cell-value {
  font-size: 11px;
  font-weight: 600;
  color: #222222;
}

.heatmap-legend {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #e0e0e0;
}

.legend-label {
  font-size: 14px;
  font-weight: 600;
  color: #666666;
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
  border: 1px solid #e0e0e0;
}

.legend-text {
  font-size: 12px;
  color: #666666;
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
