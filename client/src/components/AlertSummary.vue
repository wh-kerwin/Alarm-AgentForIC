<script setup lang="ts">
import type { Alert } from '../types'

defineProps<{
  alert: Alert
  scope: Record<string, string>
}>()
</script>

<template>
  <section class="alert-summary">
    <div class="summary-title">
      <div class="summary-meta">
        <span class="pill" :class="alert.severity">{{ alert.severity.toUpperCase() }}</span>
        <span class="pill">{{ alert.owner_role }}</span>
        <span class="pill">{{ alert.current_state }}</span>
        <span class="pill">{{ alert.alert_id }}</span>
      </div>
      <h2>{{ alert.alarm_message }}</h2>
      <p>{{ alert.summary }}</p>
    </div>
    <div class="scope-grid">
      <div v-for="(value, key) in scope" :key="key" class="scope-item">
        <span>{{ key }}</span>
        <strong>{{ value }}</strong>
      </div>
    </div>
  </section>
</template>

