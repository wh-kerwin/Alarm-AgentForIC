<script setup lang="ts">
import type { EvaluationMetrics } from '../types'

defineProps<{ metrics: EvaluationMetrics | null }>()

function pct(value: number) {
  return `${Math.round(value * 100)}%`
}
</script>

<template>
  <section class="evaluation-band">
    <div class="panel-head">
      <div>
        <p class="eyebrow">Evaluation</p>
        <h2>Agent 效果看板</h2>
      </div>
    </div>

    <template v-if="metrics">
      <div class="eval-grid">
        <div class="eval-card">
          <span>Total alerts</span>
          <strong>{{ metrics.summary.total_alerts }}</strong>
        </div>
        <div class="eval-card">
          <span>Feedback coverage</span>
          <strong>{{ pct(metrics.quality.feedback_coverage_rate) }}</strong>
        </div>
        <div class="eval-card">
          <span>Top 3 adoption</span>
          <strong>{{ pct(metrics.quality.top3_adoption_rate) }}</strong>
        </div>
        <div class="eval-card">
          <span>Unresolved high</span>
          <strong>{{ metrics.summary.unresolved_high_priority }}</strong>
        </div>
        <div class="eval-card">
          <span>Knowledge cases</span>
          <strong>{{ metrics.summary.knowledge_cases }}</strong>
        </div>
        <div class="eval-card">
          <span>Analysis requests</span>
          <strong>{{ metrics.summary.analysis_requests }}</strong>
        </div>
      </div>

      <div class="eval-details">
        <div>
          <h3>Recurrence risk</h3>
          <div class="sources">
            <span v-for="(count, risk) in metrics.risk.recurrence_risk" :key="risk" class="pill" :class="risk">
              {{ risk }}: {{ count }}
            </span>
            <span v-if="Object.keys(metrics.risk.recurrence_risk).length === 0" class="pill low">none</span>
          </div>
        </div>
        <div>
          <h3>Data gaps</h3>
          <div class="sources">
            <span class="pill critical">required: {{ metrics.risk.missing_required_sources_total }}</span>
            <span class="pill medium">optional: {{ metrics.risk.missing_optional_sources_total }}</span>
          </div>
        </div>
        <div>
          <h3>Open high-priority alerts</h3>
          <div class="sources">
            <span v-for="alertId in metrics.risk.unresolved_alert_ids" :key="alertId" class="pill critical">{{ alertId }}</span>
            <span v-if="metrics.risk.unresolved_alert_ids.length === 0" class="pill low">none</span>
          </div>
        </div>
      </div>

      <ol class="eval-notes">
        <li v-for="note in metrics.notes" :key="note">{{ note }}</li>
      </ol>
    </template>

    <p v-else class="empty">评估指标加载中。</p>
  </section>
</template>
