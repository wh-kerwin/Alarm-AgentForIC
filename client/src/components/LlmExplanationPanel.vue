<script setup lang="ts">
import type { LlmExplanation } from '../types'

defineProps<{ explanation: LlmExplanation | null }>()
</script>

<template>
  <section class="panel llm-panel">
    <div class="panel-head">
      <div>
        <p class="eyebrow">LLM explanation</p>
        <h2>证据解释层</h2>
      </div>
    </div>
    <template v-if="explanation">
      <div class="candidate-meta">
        <span class="pill">{{ explanation.provider }}</span>
        <span class="pill" :class="explanation.status === 'generated' ? 'low' : 'medium'">{{ explanation.status }}</span>
        <span class="pill">{{ explanation.model }}</span>
      </div>
      <p class="evidence">
        <strong>解释摘要</strong>
        {{ explanation.summary }}
      </p>
      <div v-if="explanation.evidence_notes.length" class="policy-section">
        <strong>证据说明</strong>
        <ol class="recommendation-list">
          <li v-for="item in explanation.evidence_notes" :key="item">{{ item }}</li>
        </ol>
      </div>
      <div v-if="explanation.uncertainty.length" class="policy-section">
        <strong>不确定性</strong>
        <ol class="recommendation-list">
          <li v-for="item in explanation.uncertainty" :key="item">{{ item }}</li>
        </ol>
      </div>
      <div v-if="explanation.suggested_next_questions.length" class="policy-section">
        <strong>建议追问</strong>
        <ol class="recommendation-list">
          <li v-for="item in explanation.suggested_next_questions" :key="item">{{ item }}</li>
        </ol>
      </div>
      <p class="safety-banner">
        <strong>Evidence-only</strong>
        {{ explanation.safety_note }}
      </p>
    </template>
    <p v-else class="empty">分析完成后显示 LLM 证据解释。</p>
  </section>
</template>

