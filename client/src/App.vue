<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { analyzeAlert, createKnowledgeCase, getAlerts, getAudit, getFeedback, getHealth, getRelatedKnowledgeCases, getRoles, submitFeedback } from './api'
import type { Alert, AnalysisResult, AuditRecord, FeedbackRecord, KnowledgeCase, RolePolicy } from './types'

const alerts = ref<Alert[]>([])
const roles = ref<RolePolicy[]>([])
const currentRole = ref('EE')
const selectedAlertId = ref('')
const analysis = ref<AnalysisResult | null>(null)
const feedbackHistory = ref<FeedbackRecord[]>([])
const relatedCases = ref<KnowledgeCase[]>([])
const auditHistory = ref<AuditRecord[]>([])
const apiStatus = ref('checking')
const isAnalyzing = ref(false)
const feedbackMessage = ref('')
const caseMessage = ref('')

const feedbackForm = reactive({
  selected_cause_rank: '',
  final_root_cause: '',
  action_taken: '',
  recurrence_risk: 'medium' as 'high' | 'medium' | 'low',
  notes: '',
})

const caseForm = reactive({
  root_cause: '',
  action: '',
  tags: '',
})

const selectedAlert = computed(() => alerts.value.find((alert) => alert.alert_id === selectedAlertId.value) ?? null)
const selectedRolePolicy = computed(() => roles.value.find((role) => role.role === currentRole.value) ?? null)

const metrics = computed(() => ({
  active: alerts.value.length,
  critical: alerts.value.filter((alert) => alert.severity === 'critical').length,
  high: alerts.value.filter((alert) => alert.severity === 'high').length,
  recommended: alerts.value.filter((alert) => alert.status === 'recommended').length,
}))

const scope = computed(() => {
  if (analysis.value?.impact_scope) return analysis.value.impact_scope
  if (!selectedAlert.value) return {}
  return {
    equipment: selectedAlert.value.equipment_id,
    chamber: selectedAlert.value.chamber_id,
    lot: selectedAlert.value.lot_id,
    wafer: selectedAlert.value.wafer_id,
    recipe: selectedAlert.value.recipe_id,
    product: selectedAlert.value.product_id,
  }
})

async function refreshAlerts() {
  alerts.value = await getAlerts(currentRole.value)
  if (!selectedAlertId.value && alerts.value.length > 0) {
    selectedAlertId.value = alerts.value[0].alert_id
  }
}

async function runAnalysis() {
  if (!selectedAlertId.value) return
  isAnalyzing.value = true
  try {
    analysis.value = await analyzeAlert(selectedAlertId.value, currentRole.value)
    await loadAudit()
  } finally {
    isAnalyzing.value = false
  }
}

async function loadFeedback() {
  if (!selectedAlertId.value) return
  feedbackHistory.value = await getFeedback(selectedAlertId.value, currentRole.value)
}

async function loadRelatedCases() {
  if (!selectedAlertId.value) return
  relatedCases.value = await getRelatedKnowledgeCases(selectedAlertId.value, currentRole.value)
}

async function loadAudit() {
  if (!selectedAlertId.value) return
  auditHistory.value = await getAudit(selectedAlertId.value, currentRole.value)
}

async function selectAlert(alertId: string) {
  selectedAlertId.value = alertId
  analysis.value = null
  feedbackMessage.value = ''
  caseMessage.value = ''
  feedbackForm.selected_cause_rank = ''
  feedbackForm.final_root_cause = ''
  feedbackForm.action_taken = ''
  feedbackForm.recurrence_risk = 'medium'
  feedbackForm.notes = ''
  caseForm.root_cause = ''
  caseForm.action = ''
  caseForm.tags = ''
  await runAnalysis()
  await loadFeedback()
  await loadRelatedCases()
  await loadAudit()
}

async function submitEngineerFeedback() {
  if (!selectedAlertId.value) return
  await submitFeedback(selectedAlertId.value, {
    selected_cause_rank: feedbackForm.selected_cause_rank ? Number(feedbackForm.selected_cause_rank) : null,
    final_root_cause: feedbackForm.final_root_cause,
    action_taken: feedbackForm.action_taken,
    recurrence_risk: feedbackForm.recurrence_risk,
    notes: feedbackForm.notes,
  }, currentRole.value)
  feedbackMessage.value = '反馈已写入案例闭环。'
  feedbackForm.selected_cause_rank = ''
  feedbackForm.final_root_cause = ''
  feedbackForm.action_taken = ''
  feedbackForm.recurrence_risk = 'medium'
  feedbackForm.notes = ''
  await loadFeedback()
  await loadAudit()
}

async function submitKnowledgeCase() {
  if (!selectedAlert.value) return
  await createKnowledgeCase({
    alarm_code: selectedAlert.value.alarm_code,
    equipment_family: selectedAlert.value.equipment_id.split('-')[0],
    root_cause: caseForm.root_cause,
    action: caseForm.action,
    tags: caseForm.tags.split(',').map((tag) => tag.trim()).filter(Boolean),
    source: 'engineer',
    alert_id: selectedAlert.value.alert_id,
  }, currentRole.value)
  caseMessage.value = '案例已加入知识库，并会被后续分析复用。'
  caseForm.root_cause = ''
  caseForm.action = ''
  caseForm.tags = ''
  await loadRelatedCases()
  await runAnalysis()
  await loadAudit()
}

async function changeRole() {
  await refreshAlerts()
  if (selectedAlertId.value) {
    await runAnalysis()
    await loadFeedback()
    await loadRelatedCases()
    await loadAudit()
  }
}

onMounted(async () => {
  try {
    roles.value = await getRoles(currentRole.value)
    const health = await getHealth(currentRole.value)
    apiStatus.value = `API ${health.status}`
  } catch {
    apiStatus.value = 'API offline'
  }

  await refreshAlerts()
  if (selectedAlertId.value) {
    await runAnalysis()
    await loadFeedback()
    await loadRelatedCases()
    await loadAudit()
  }
})
</script>

<template>
  <div class="shell">
    <aside class="rail">
      <div class="brand">
        <span class="brand-mark"></span>
        <div>
          <strong>Alarm-AgentForIC</strong>
          <small>Semiconductor Alert RCA</small>
        </div>
      </div>

      <section class="role-panel">
        <label>
          当前角色
          <select v-model="currentRole" @change="changeRole">
            <option v-for="role in roles" :key="role.role" :value="role.role">{{ role.label }}</option>
          </select>
        </label>
        <p v-if="selectedRolePolicy">{{ selectedRolePolicy.focus }}</p>
      </section>

      <section class="metric-stack">
        <div class="metric">
          <span>Active alerts</span>
          <strong>{{ metrics.active }}</strong>
        </div>
        <div class="metric">
          <span>Critical</span>
          <strong>{{ metrics.critical }}</strong>
        </div>
        <div class="metric">
          <span>High</span>
          <strong>{{ metrics.high }}</strong>
        </div>
        <div class="metric">
          <span>Recommended</span>
          <strong>{{ metrics.recommended }}</strong>
        </div>
      </section>

      <section class="alert-queue">
        <div class="section-title">
          <span>告警队列</span>
          <button class="icon-button" title="刷新" @click="refreshAlerts">↻</button>
        </div>

        <div class="alert-list">
          <button
            v-for="alert in alerts"
            :key="alert.alert_id"
            class="alert-card"
            :class="{ active: alert.alert_id === selectedAlertId }"
            @click="selectAlert(alert.alert_id)"
          >
            <div class="card-meta">
              <span class="pill" :class="alert.severity">{{ alert.severity.toUpperCase() }}</span>
              <span class="pill">{{ alert.source }}</span>
              <span class="pill">{{ alert.status }}</span>
            </div>
            <strong>{{ alert.equipment_id }} / {{ alert.chamber_id }}</strong>
            <p>{{ alert.alarm_code }} · {{ alert.timestamp }}</p>
            <p>{{ alert.summary }}</p>
          </button>
        </div>
      </section>
    </aside>

    <main class="workbench">
      <header class="topbar">
        <div>
          <p class="eyebrow">半导体异常告警与根因分析 Agent</p>
          <h1>{{ selectedAlert ? `${selectedAlert.equipment_id} ${selectedAlert.alarm_code}` : '设备告警工作台' }}</h1>
        </div>
        <div class="topbar-actions">
          <span class="status-pill" :class="{ ok: apiStatus.includes('ok') }">{{ apiStatus }}</span>
          <button class="primary-button" :disabled="isAnalyzing" @click="runAnalysis">
            {{ isAnalyzing ? '分析中' : '生成根因分析' }}
          </button>
        </div>
      </header>

      <section v-if="selectedAlert" class="alert-summary">
        <div class="summary-title">
          <div class="summary-meta">
            <span class="pill" :class="selectedAlert.severity">{{ selectedAlert.severity.toUpperCase() }}</span>
            <span class="pill">{{ selectedAlert.owner_role }}</span>
            <span class="pill">{{ selectedAlert.current_state }}</span>
            <span class="pill">{{ selectedAlert.alert_id }}</span>
          </div>
          <h2>{{ selectedAlert.alarm_message }}</h2>
          <p>{{ selectedAlert.summary }}</p>
        </div>
        <div class="scope-grid">
          <div v-for="(value, key) in scope" :key="key" class="scope-item">
            <span>{{ key }}</span>
            <strong>{{ value }}</strong>
          </div>
        </div>
      </section>

      <div class="grid">
        <section class="panel timeline-panel">
          <div class="panel-head">
            <div>
              <p class="eyebrow">Event correlation</p>
              <h2>事件时间线</h2>
            </div>
          </div>
          <div v-if="analysis?.timeline.length" class="timeline">
            <article v-for="event in analysis.timeline" :key="`${event.time}-${event.title}`" class="timeline-item">
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

        <section class="panel rca-panel">
          <div class="panel-head">
            <div>
              <p class="eyebrow">Root cause candidates</p>
              <h2>Top 根因候选</h2>
            </div>
          </div>
          <div v-if="analysis?.root_cause_candidates.length" class="root-causes">
            <article v-for="candidate in analysis.root_cause_candidates" :key="candidate.rank" class="candidate">
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

        <section class="panel role-safety-panel">
          <div class="panel-head">
            <div>
              <p class="eyebrow">Role safety</p>
              <h2>角色与安全边界</h2>
            </div>
          </div>
          <template v-if="analysis">
            <div class="policy-box">
              <div class="scope-item">
                <span>role</span>
                <strong>{{ analysis.role_context.label }}</strong>
              </div>
              <div class="scope-item">
                <span>owner match</span>
                <strong>{{ analysis.role_context.is_owner_role ? 'yes' : 'no' }}</strong>
              </div>
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

        <section class="panel policy-panel">
          <div class="panel-head">
            <div>
              <p class="eyebrow">Context policy</p>
              <h2>上下文收集策略</h2>
            </div>
          </div>
          <template v-if="analysis">
            <div class="policy-box">
              <div class="scope-item">
                <span>policy</span>
                <strong>{{ analysis.collection_status.policy.policy_id }}</strong>
              </div>
              <div class="scope-item">
                <span>time window</span>
                <strong>{{ analysis.collection_status.policy.time_window_minutes }} min</strong>
              </div>
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
                <span
                  v-for="source in analysis.collection_status.missing_required_sources"
                  :key="source"
                  class="pill critical"
                >
                  {{ source }}
                </span>
                <span v-if="analysis.collection_status.missing_required_sources.length === 0" class="pill low">none</span>
              </div>
            </div>
            <div class="policy-section">
              <strong>缺少可选源</strong>
              <div class="sources">
                <span
                  v-for="source in analysis.collection_status.missing_optional_sources"
                  :key="source"
                  class="pill medium"
                >
                  {{ source }}
                </span>
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

        <section class="panel cases-panel">
          <div class="panel-head">
            <div>
              <p class="eyebrow">Knowledge base</p>
              <h2>相关案例库</h2>
            </div>
          </div>

          <div class="case-list">
            <article v-for="item in relatedCases" :key="item.case_id" class="case-item">
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
            <p v-if="relatedCases.length === 0" class="empty">当前告警暂无匹配历史案例。</p>
          </div>

          <form class="feedback-form case-form" @submit.prevent="submitKnowledgeCase">
            <label>
              新案例根因
              <textarea v-model="caseForm.root_cause" rows="2" required placeholder="沉淀工程确认后的根因"></textarea>
            </label>
            <label>
              标准处置动作
              <textarea v-model="caseForm.action" rows="2" required placeholder="沉淀可复用的检查/恢复动作"></textarea>
            </label>
            <label>
              标签
              <input v-model="caseForm.tags" placeholder="vacuum, pm, etch" />
            </label>
            <button type="submit" class="secondary-button">加入案例库</button>
            <p class="form-message">{{ caseMessage }}</p>
          </form>
        </section>

        <section class="panel feedback-panel">
          <div class="panel-head">
            <div>
              <p class="eyebrow">Human feedback loop</p>
              <h2>工程师反馈</h2>
            </div>
          </div>

          <form class="feedback-form" @submit.prevent="submitEngineerFeedback">
            <label>
              采纳根因
              <select v-model="feedbackForm.selected_cause_rank">
                <option value="">未选择</option>
                <option value="1">Rank 1</option>
                <option value="2">Rank 2</option>
                <option value="3">Rank 3</option>
              </select>
            </label>
            <label>
              最终根因
              <textarea v-model="feedbackForm.final_root_cause" rows="3" required placeholder="记录工程确认后的真实根因"></textarea>
            </label>
            <label>
              已执行动作
              <textarea v-model="feedbackForm.action_taken" rows="3" required placeholder="记录 hold、检查、恢复、升级等动作"></textarea>
            </label>
            <label>
              复发风险
              <select v-model="feedbackForm.recurrence_risk">
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="low">Low</option>
              </select>
            </label>
            <label>
              备注
              <textarea v-model="feedbackForm.notes" rows="2" placeholder="补充证据、不确定性或后续计划"></textarea>
            </label>
            <button type="submit" class="secondary-button">写入反馈闭环</button>
            <p class="form-message">{{ feedbackMessage }}</p>
          </form>

          <div class="feedback-history">
            <div v-for="row in feedbackHistory" :key="row.feedback_id" class="feedback-item">
              <strong>{{ row.final_root_cause }}</strong>
              <p>{{ row.action_taken }}</p>
              <span class="pill" :class="row.recurrence_risk">{{ row.recurrence_risk }}</span>
              <span class="pill">{{ row.created_at }}</span>
            </div>
            <p v-if="feedbackHistory.length === 0" class="empty">暂无工程师反馈。</p>
          </div>
        </section>

        <section class="panel audit-panel">
          <div class="panel-head">
            <div>
              <p class="eyebrow">Audit trail</p>
              <h2>审计记录</h2>
            </div>
          </div>
          <div class="feedback-history">
            <div v-for="row in auditHistory" :key="row.audit_id" class="feedback-item">
              <strong>{{ row.action }} · {{ row.role }}</strong>
              <p>{{ row.summary }}</p>
              <span class="pill">{{ row.audit_id }}</span>
              <span class="pill">{{ row.created_at }}</span>
            </div>
            <p v-if="auditHistory.length === 0" class="empty">暂无审计记录。</p>
          </div>
        </section>
      </div>
    </main>
  </div>
</template>
