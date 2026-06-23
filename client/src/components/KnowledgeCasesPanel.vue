<script setup lang="ts">
import type { KnowledgeCase } from '../types'

defineProps<{
  cases: KnowledgeCase[]
  form: {
    root_cause: string
    action: string
    tags: string
  }
  message: string
}>()

const emit = defineEmits<{ submit: [] }>()
</script>

<template>
  <section class="panel cases-panel">
    <div class="panel-head">
      <div>
        <p class="eyebrow">Knowledge base</p>
        <h2>相关案例库</h2>
      </div>
    </div>

    <div class="case-list">
      <article v-for="item in cases" :key="item.case_id" class="case-item">
        <div class="candidate-meta">
          <span class="pill">{{ item.case_id }}</span>
          <span class="pill">{{ item.source }}</span>
        </div>
        <strong>{{ item.root_cause }}</strong>
        <p>{{ item.action }}</p>
        <div class="sources">
          <span v-for="tag in item.tags" :key="`${item.case_id}-${tag}`" class="pill">{{ tag }}</span>
        </div>
      </article>
      <p v-if="cases.length === 0" class="empty">当前告警暂无匹配历史案例。</p>
    </div>

    <form class="feedback-form case-form" @submit.prevent="emit('submit')">
      <label>
        新案例根因
        <textarea v-model="form.root_cause" rows="2" required placeholder="沉淀工程确认后的根因"></textarea>
      </label>
      <label>
        标准处置动作
        <textarea v-model="form.action" rows="2" required placeholder="沉淀可复用的检查/恢复动作"></textarea>
      </label>
      <label>
        标签
        <input v-model="form.tags" placeholder="vacuum, pm, etch" />
      </label>
      <button type="submit" class="secondary-button">加入案例库</button>
      <p class="form-message">{{ message }}</p>
    </form>
  </section>
</template>

