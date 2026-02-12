<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import MobileWarning from './components/MobileWarning.vue';

const router = useRouter()
const route = useRoute()
const hasSavedCampaigns = ref(false)
const previousRoute = ref<string>('/')
const screenWidth = ref(window.innerWidth)

const MOBILE_BREAKPOINT = 768
const isMobile = computed(() => screenWidth.value < MOBILE_BREAKPOINT)

function updateScreenWidth() {
  screenWidth.value = window.innerWidth
}

onMounted(() => {
  const campaignsJson = sessionStorage.getItem('campaigns')
  hasSavedCampaigns.value = !!campaignsJson
  window.addEventListener('resize', updateScreenWidth)
})

onUnmounted(() => {
  window.removeEventListener('resize', updateScreenWidth)
})

watch(() => route.path, (newPath, oldPath) => {
  if (newPath === '/help' && oldPath) {
    previousRoute.value = oldPath
  }
})

function goToWebsite() {
  window.open('https://derekw.co/?utm_medium=referral&utm_source=simple-dash', '_blank');
}

function goBack() {
  router.push(previousRoute.value)
}
</script>

<template>
  <MobileWarning v-if="isMobile" />
  <div v-else>
    <header class="top-bar">
      <h1 class="logo"><span class="logo-highlight">::</span>simple dash<span class="byline" @click="goToWebsite">by
          derekw</span></h1>
      <div class="nav">
        <button v-if="$route.path === '/help'" class="nav-button" title="Back" @click="goBack">
          {{ previousRoute === '/dashboard' ? 'back to dashboard' : 'back to upload' }}
        </button>
        <button v-else-if="$route.path === '/dashboard'" class="nav-button" title="Upload" @click="$router.push('/')">
          back to upload
        </button>
        <button v-else-if="$route.path === '/' && hasSavedCampaigns" class="nav-button" title="Dashboard"
          @click="$router.push('/dashboard')">
          go to dashboard
        </button>
        <button v-if="$route.path !== '/help'" class="nav-button" title="Help / About" @click="$router.push('/help')">
          help / about
        </button>
      </div>
    </header>

    <div class="content">
      <RouterView />
    </div>
  </div>
</template>

<style>
.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--color-bg-dark);
  color: var(--color-text-white);
  box-shadow: var(--shadow-md);
  border-top: 5px solid var(--color-primary);
  height: var(--top-bar-height);
}

.logo {
  pointer-events: none;
  user-select: none;
  margin: var(--spacing-sm) 0.75rem;
  font-size: 1.25rem;
  font-weight: 500;
  letter-spacing: 0.5px;
}

.logo-highlight {
  color: var(--color-primary);
  font-weight: 900;
  margin-right: var(--radius-sm);
  font-size: 0.75rem;
}

.byline {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  margin-left: var(--radius-sm);
  cursor: pointer;
  pointer-events: auto;
  font-style: italic;
  transition: var(--slow-transition);
}

.byline:hover {
  color: var(--color-text-white);
}

.nav {
  display: flex;
  align-items: center;
  height: 100%;
}

.nav-button {
  min-width: 100px;
  padding: var(--spacing-sm) 0.75rem;
  height: 100%;
  border: 0;
  background: var(--color-bg-dark);
  color: var(--color-text-white);
  cursor: pointer;
  transition: var(--slow-transition);
}

.nav-button:hover {
  background: var(--color-bg-hover);
}

.content {
  height: calc(100vh - var(--top-bar-height));
  overflow-y: auto;
}
</style>
