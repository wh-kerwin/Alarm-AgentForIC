<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { analyzeAlert, createKnowledgeCase, getAlerts, getAudit, getEvaluation, getFeedback, getHealth, getRelatedKnowledgeCases, getRoles, submitFeedback } from './api'
import AlertSummary from './components/AlertSummary.vue'
import AuditPanel from './components/AuditPanel.vue'
import ContextPolicyPanel from './components/ContextPolicyPanel.vue'
import FeedbackPanel from './components/FeedbackPanel.vue'
import EvaluationDashboard from './components/EvaluationDashboard.vue'
import KnowledgeCasesPanel from './components/KnowledgeCasesPanel.vue'
import LlmExplanationPanel from './components/LlmExplanationPanel.vue'
import RecommendationPanel from './components/RecommendationPanel.vue'
import RoleSafetyPanel from './components/RoleSafetyPanel.vue'
import RootCausesPanel from './components/RootCausesPanel.vue'
import Sidebar from './components/Sidebar.vue'
import TimelinePanel from './components/TimelinePanel.vue'
import type { Alert, AnalysisResult, AuditRecord, EvaluationMetrics, FeedbackRecord, KnowledgeCase, RolePolicy } from './types'

const alerts = ref<Alert[]>([])
const roles = ref<RolePolicy[]>([])
const currentRole = ref('EE')
const selectedAlertId = ref('')
const analysis = ref<AnalysisResult | null>(null)
const feedbackHistory = ref<FeedbackRecord[]>([])
const relatedCases = ref<KnowledgeCase[]>([])
const auditHistory = ref<AuditRecord[]>([])
const evaluation = ref<EvaluationMetrics | null>(null)
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

async function loadEvaluation() {
  evaluation.value = await getEvaluation(currentRole.value)
}

async function runAnalysis() {
  if (!selectedAlertId.value) return
  isAnalyzing.value = true
  try {
    analysis.value = await analyzeAlert(selectedAlertId.value, currentRole.value)
    await loadAudit()
    await loadEvaluation()
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

function resetForms() {
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
}

async function selectAlert(alertId: string) {
  selectedAlertId.value = alertId
  analysis.value = null
  resetForms()
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
  await loadEvaluation()
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
  await loadEvaluation()
}

async function changeRole(role: string) {
  currentRole.value = role
  await refreshAlerts()
  if (selectedAlertId.value) {
    await runAnalysis()
    await loadFeedback()
    await loadRelatedCases()
    await loadAudit()
    await loadEvaluation()
  }
}

onMounted(async () => {
  roles.value = await getRoles(currentRole.value)
  try {
    const health = await getHealth(currentRole.value)
    apiStatus.value = `API ${health.status}`
  } catch {
    apiStatus.value = 'API offline'
  }

  await refreshAlerts()
  await loadEvaluation()
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
    <Sidebar
      :alerts="alerts"
      :roles="roles"
      :current-role="currentRole"
      :selected-alert-id="selectedAlertId"
      :selected-role-policy="selectedRolePolicy"
      :metrics="metrics"
      @refresh="refreshAlerts"
      @select-alert="selectAlert"
      @change-role="changeRole"
    />

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

      <AlertSummary v-if="selectedAlert" :alert="selectedAlert" :scope="scope" />
      <EvaluationDashboard :metrics="evaluation" />

      <div class="grid">
        <div class="main-stack">
          <TimelinePanel :timeline="analysis?.timeline ?? []" />
          <RootCausesPanel :candidates="analysis?.root_cause_candidates ?? []" />
        </div>

        <div class="side-stack">
          <RecommendationPanel :analysis="analysis" />
          <RoleSafetyPanel :analysis="analysis" />
          <LlmExplanationPanel :explanation="analysis?.llm_explanation ?? null" />
          <ContextPolicyPanel :analysis="analysis" />
          <KnowledgeCasesPanel
            :cases="relatedCases"
            :form="caseForm"
            :message="caseMessage"
            @submit="submitKnowledgeCase"
          />
          <FeedbackPanel
            :form="feedbackForm"
            :message="feedbackMessage"
            :history="feedbackHistory"
            @submit="submitEngineerFeedback"
          />
          <AuditPanel :history="auditHistory" />
        </div>
      </div>
    </main>
  </div>
</template>
