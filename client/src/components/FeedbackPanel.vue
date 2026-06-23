<script setup lang="ts">
import type { FeedbackRecord } from '../types'

defineProps<{
  form: {
    selected_cause_rank: string
    final_root_cause: string
    action_taken: string
    recurrence_risk: 'high' | 'medium' | 'low'
    notes: string
  }
  message: string
  history: FeedbackRecord[]
}>()

const emit = defineEmits<{ submit: [] }>()
</script>

<template>
  <section class="panel feedback-panel">
    <div class="panel-head">
      <div>
        <p class="eyebrow">Human feedback loop</p>
        <h2>工程师反馈</h2>
      </div>
    </div>

    <form class="feedback-form" @submit.prevent="emit('submit')">
      <label>
        采纳根因
        <select v-model="form.selected_cause_rank">
          <option value="">未选择</option>
          <option value="1">Rank 1</option>
          <option value="2">Rank 2</option>
          <option value="3">Rank 3</option>
        </select>
      </label>
      <label>
        最终根因
        <textarea v-model="form.final_root_cause" rows="3" required placeholder="记录工程确认后的真实根因"></textarea>
      </label>
      <label>
        已执行动作
        <textarea v-model="form.action_taken" rows="3" required placeholder="记录 hold、检查、恢复、升级等动作"></textarea>
      </label>
      <label>
        复发风险
        <select v-model="form.recurrence_risk">
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="low">Low</option>
        </select>
      </label>
      <label>
        备注
        <textarea v-model="form.notes" rows="2" placeholder="补充证据、不确定性或后续计划"></textarea>
      </label>
      <button type="submit" class="secondary-button">写入反馈闭环</button>
      <p class="form-message">{{ message }}</p>
    </form>

    <div class="feedback-history">
      <div v-for="row in history" :key="row.feedback_id" class="feedback-item">
        <strong>{{ row.final_root_cause }}</strong>
        <p>{{ row.action_taken }}</p>
        <span class="pill" :class="row.recurrence_risk">{{ row.recurrence_risk }}</span>
        <span class="pill">{{ row.created_at }}</span>
      </div>
      <p v-if="history.length === 0" class="empty">暂无工程师反馈。</p>
    </div>
  </section>
</template>

