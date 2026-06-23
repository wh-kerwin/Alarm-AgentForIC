<script setup lang="ts">
import type { AuditRecord } from '../types'

defineProps<{ history: AuditRecord[] }>()
</script>

<template>
  <section class="panel audit-panel">
    <div class="panel-head">
      <div>
        <p class="eyebrow">Audit trail</p>
        <h2>审计记录</h2>
      </div>
    </div>
    <div class="feedback-history">
      <div v-for="row in history" :key="row.audit_id" class="feedback-item">
        <strong>{{ row.action }} · {{ row.role }}</strong>
        <p>{{ row.summary }}</p>
        <span class="pill">{{ row.audit_id }}</span>
        <span class="pill">{{ row.created_at }}</span>
      </div>
      <p v-if="history.length === 0" class="empty">暂无审计记录。</p>
    </div>
  </section>
</template>
