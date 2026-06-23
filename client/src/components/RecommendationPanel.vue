<script setup lang="ts">
import type { AnalysisResult } from '../types'

defineProps<{ analysis: AnalysisResult | null }>()
</script>

<template>
  <section class="panel side-panel">
    <div class="panel-head">
      <div>
        <p class="eyebrow">Recommended actions</p>
        <h2>处置建议</h2>
      </div>
    </div>
    <template v-if="analysis">
      <p class="safety-banner">
        <strong>Advisory only</strong>
        {{ analysis.safety_gate.message }}
      </p>
      <ol class="recommendation-list">
        <li v-for="item in analysis.handling_recommendations" :key="item">{{ item }}</li>
      </ol>
      <p class="evidence">
        <strong>升级建议</strong>
        {{ analysis.escalation.target_role }} · {{ analysis.escalation.reason }}
      </p>
      <div class="sources">
        <span v-for="source in analysis.data_sources" :key="source" class="pill">{{ source }}</span>
      </div>
    </template>
    <p v-else class="empty">分析完成后显示 SOP/OCAP 处置建议。</p>
  </section>
</template>

