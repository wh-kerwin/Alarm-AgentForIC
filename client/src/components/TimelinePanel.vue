<script setup lang="ts">
import type { EventItem } from '../types'

defineProps<{ timeline: EventItem[] }>()
</script>

<template>
  <section class="panel timeline-panel">
    <div class="panel-head">
      <div>
        <p class="eyebrow">Event correlation</p>
        <h2>事件时间线</h2>
      </div>
    </div>
    <div v-if="timeline.length" class="timeline">
      <article v-for="event in timeline" :key="`${event.time}-${event.title}`" class="timeline-item">
        <div>
          <div class="timeline-time">{{ event.time }}</div>
          <span class="pill" :class="event.severity">{{ event.source }}</span>
        </div>
        <div>
          <strong>{{ event.event_type }} · {{ event.title }}</strong>
          <p>{{ event.description }}</p>
        </div>
      </article>
    </div>
    <p v-else class="empty">点击“生成根因分析”后展示事件时间线。</p>
  </section>
</template>

