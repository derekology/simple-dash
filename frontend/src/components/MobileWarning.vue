<template>
    <div class="mobile-warning">
        <div class="mobile-content">
            <div class="icon">📱</div>
            <h1>Screen Too Small</h1>
            <p class="message">
                Simple Dash requires a wider screen to display the dashboard properly.
            </p>
            <p class="suggestion">
                Please use a tablet, laptop, or desktop computer to view your campaign analytics.
            </p>
            <div class="info-box">
                <p><strong>Minimum width required:</strong> 768px</p>
                <p><strong>Your current width:</strong> <span class="current-width">{{ screenWidth }}px</span></p>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';

const screenWidth = ref(window.innerWidth);

function updateWidth() {
    screenWidth.value = window.innerWidth;
}

onMounted(() => {
    window.addEventListener('resize', updateWidth);
});

onUnmounted(() => {
    window.removeEventListener('resize', updateWidth);
});
</script>

<style scoped>
.mobile-warning {
    padding: var(--spacing-xl);
    max-width: 600px;
    margin: 0 auto;
}

.mobile-content {
    background: white;
    border-radius: 12px;
    padding: var(--spacing-xl) var(--spacing-lg);
    text-align: center;
    box-shadow: var(--shadow-md);
}

.icon {
    font-size: 4rem;
    margin-bottom: var(--spacing-md);
}

h1 {
    font-size: 1.75rem;
    color: var(--color-text);
    margin: 0 0 var(--spacing-md) 0;
}

.message {
    font-size: var(--spacing-md);
    color: #555;
    margin: 0 0 var(--spacing-md) 0;
    line-height: 1.6;
}

.suggestion {
    font-size: 0.95rem;
    color: var(--color-text-light);
    margin: 0 0 var(--spacing-lg) 0;
    line-height: 1.6;
}

.info-box {
    background: var(--color-bg-warning-gradient);
    border-radius: 8px;
    padding: var(--spacing-md);
    margin-bottom: var(--spacing-lg);
    border-left: 5px solid var(--color-warning);
}

.info-box p {
    margin: var(--spacing-sm) 0;
    font-size: 0.9rem;
    color: var(--color-text-light);
}

.current-width {
    font-weight: bold;
    color: var(--color-primary);
}
</style>
