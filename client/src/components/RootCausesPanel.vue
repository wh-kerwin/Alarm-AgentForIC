<script setup lang="ts">
import type { RootCauseCandidate } from '../types'

defineProps<{ candidates: RootCauseCandidate[] }>()
</script>

<template>
  <section class="panel rca-panel">
    <div class="panel-head">
      <div>
        <p class="eyebrow">Root cause candidates</p>
        <h2>Top 根因候选</h2>
      </div>
    </div>
    <div v-if="candidates.length" class="root-causes">
      <article v-for="candidate in candidates" :key="candidate.rank" class="candidate">
        <div class="candidate-top">
          <span class="rank">{{ candidate.rank }}</span>
          <div class="candidate-body">
            <div class="candidate-meta">
              <span class="pill" :class="candidate.confidence">{{ candidate.confidence.toUpperCase() }}</span>
              <span class="pill">{{ candidate.category }}</span>
            </div>
            <h3>{{ candidate.cause }}</h3>
            <div class="evidence-grid">
              <div v-for="item in candidate.evidence" :key="`${candidate.rank}-${item.label}`" class="evidence">
                <strong>{{ item.label }} · {{ item.source }}</strong>
                <p>{{ item.detail }}</p>
                <span>strength: {{ item.strength }}</span>
              </div>
            </div>
            <ol class="action-list">
              <li v-for="step in candidate.verification_steps" :key="step">{{ step }}</li>
            </ol>
          </div>
        </div>
      </article>
    </div>
    <p v-else class="empty">尚未生成根因候选。</p>
  </section>
</template>

