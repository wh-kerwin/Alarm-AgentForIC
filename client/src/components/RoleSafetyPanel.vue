<script setup lang="ts">
import type { AnalysisResult } from '../types'

defineProps<{ analysis: AnalysisResult | null }>()
</script>

<template>
  <section class="panel role-safety-panel">
    <div class="panel-head">
      <div>
        <p class="eyebrow">Role safety</p>
        <h2>角色与安全边界</h2>
      </div>
    </div>
    <template v-if="analysis">
      <div class="policy-box">
        <div class="scope-item"><span>role</span><strong>{{ analysis.role_context.label }}</strong></div>
        <div class="scope-item"><span>owner match</span><strong>{{ analysis.role_context.is_owner_role ? 'yes' : 'no' }}</strong></div>
      </div>
      <p class="evidence">
        <strong>角色关注点</strong>
        {{ analysis.role_context.focus }}
      </p>
      <div class="policy-section">
        <strong>升级对象</strong>
        <div class="sources">
          <span v-for="target in analysis.role_context.escalation_targets" :key="target" class="pill">{{ target }}</span>
        </div>
      </div>
      <div class="policy-section">
        <strong>禁止自动执行</strong>
        <div class="sources">
          <span v-for="action in analysis.safety_gate.blocked_actions" :key="action" class="pill critical">{{ action }}</span>
        </div>
      </div>
    </template>
    <p v-else class="empty">分析完成后显示角色安全边界。</p>
  </section>
</template>

