<script setup lang="ts">
import type { Alert, RolePolicy } from '../types'

defineProps<{
  alerts: Alert[]
  roles: RolePolicy[]
  currentRole: string
  selectedAlertId: string
  selectedRolePolicy: RolePolicy | null
  metrics: {
    active: number
    critical: number
    high: number
    recommended: number
  }
}>()

const emit = defineEmits<{
  refresh: []
  selectAlert: [alertId: string]
  changeRole: [role: string]
}>()
</script>

<template>
  <aside class="rail">
    <div class="brand">
      <span class="brand-mark"></span>
      <div>
        <strong>Alarm-AgentForIC</strong>
        <small>Semiconductor Alert RCA</small>
      </div>
    </div>

    <section class="role-panel">
      <label>
        当前角色
        <select :value="currentRole" @change="emit('changeRole', ($event.target as HTMLSelectElement).value)">
          <option v-for="role in roles" :key="role.role" :value="role.role">{{ role.label }}</option>
        </select>
      </label>
      <p v-if="selectedRolePolicy">{{ selectedRolePolicy.focus }}</p>
    </section>

    <section class="metric-stack">
      <div class="metric"><span>Active alerts</span><strong>{{ metrics.active }}</strong></div>
      <div class="metric"><span>Critical</span><strong>{{ metrics.critical }}</strong></div>
      <div class="metric"><span>High</span><strong>{{ metrics.high }}</strong></div>
      <div class="metric"><span>Recommended</span><strong>{{ metrics.recommended }}</strong></div>
    </section>

    <section class="alert-queue">
      <div class="section-title">
        <span>告警队列</span>
        <button class="icon-button" title="刷新" @click="emit('refresh')">↻</button>
      </div>

      <div class="alert-list">
        <button
          v-for="alert in alerts"
          :key="alert.alert_id"
          class="alert-card"
          :class="{ active: alert.alert_id === selectedAlertId }"
          @click="emit('selectAlert', alert.alert_id)"
        >
          <div class="card-meta">
            <span class="pill" :class="alert.severity">{{ alert.severity.toUpperCase() }}</span>
            <span class="pill">{{ alert.source }}</span>
            <span class="pill">{{ alert.status }}</span>
          </div>
          <strong>{{ alert.equipment_id }} / {{ alert.chamber_id }}</strong>
          <p>{{ alert.alarm_code }} · {{ alert.timestamp }}</p>
          <p>{{ alert.summary }}</p>
        </button>
      </div>
    </section>
  </aside>
</template>

