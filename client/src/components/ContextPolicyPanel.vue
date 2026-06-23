<script setup lang="ts">
import type { AnalysisResult } from '../types'

defineProps<{ analysis: AnalysisResult | null }>()
</script>

<template>
  <section class="panel policy-panel">
    <div class="panel-head">
      <div>
        <p class="eyebrow">Context policy</p>
        <h2>上下文收集策略</h2>
      </div>
    </div>
    <template v-if="analysis">
      <div class="policy-box">
        <div class="scope-item"><span>policy</span><strong>{{ analysis.collection_status.policy.policy_id }}</strong></div>
        <div class="scope-item"><span>time window</span><strong>{{ analysis.collection_status.policy.time_window_minutes }} min</strong></div>
      </div>
      <div class="policy-section">
        <strong>已收集</strong>
        <div class="sources">
          <span v-for="source in analysis.collection_status.collected_sources" :key="source" class="pill">{{ source }}</span>
        </div>
      </div>
      <div class="policy-section">
        <strong>缺少必需源</strong>
        <div class="sources">
          <span v-for="source in analysis.collection_status.missing_required_sources" :key="source" class="pill critical">{{ source }}</span>
          <span v-if="analysis.collection_status.missing_required_sources.length === 0" class="pill low">none</span>
        </div>
      </div>
      <div class="policy-section">
        <strong>缺少可选源</strong>
        <div class="sources">
          <span v-for="source in analysis.collection_status.missing_optional_sources" :key="source" class="pill medium">{{ source }}</span>
          <span v-if="analysis.collection_status.missing_optional_sources.length === 0" class="pill low">none</span>
        </div>
      </div>
      <p v-for="note in analysis.collection_status.fallback_notes" :key="note" class="evidence">
        <strong>降级说明</strong>
        {{ note }}
      </p>
    </template>
    <p v-else class="empty">分析完成后显示上下文收集策略。</p>
  </section>
</template>

