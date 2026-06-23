import type { Alert, AnalysisResult, AuditRecord, EvaluationMetrics, FeedbackRecord, KnowledgeCase, RolePolicy } from './types'

async function request<T>(path: string, role: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(path, {
    headers: { 'Content-Type': 'application/json', 'X-Agent-Role': role },
    ...options,
  })

  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    throw new Error(body.error || `HTTP ${response.status}`)
  }

  return response.json() as Promise<T>
}

export function getHealth(role: string) {
  return request<{ status: string; version: string }>('/api/health', role)
}

export function getRoles(role: string) {
  return request<RolePolicy[]>('/api/roles', role)
}

export function getAlerts(role: string) {
  return request<Alert[]>('/api/alerts', role)
}

export function getEvaluation(role: string) {
  return request<EvaluationMetrics>('/api/evaluation', role)
}

export function analyzeAlert(alertId: string, role: string) {
  return request<AnalysisResult>(`/api/alerts/${alertId}/analyze`, role, { method: 'POST' })
}

export function getFeedback(alertId: string, role: string) {
  return request<FeedbackRecord[]>(`/api/alerts/${alertId}/feedback`, role)
}

export function getAudit(alertId: string, role: string) {
  return request<AuditRecord[]>(`/api/alerts/${alertId}/audit`, role)
}

export function getRelatedKnowledgeCases(alertId: string, role: string) {
  return request<KnowledgeCase[]>(`/api/alerts/${alertId}/knowledge-cases`, role)
}

export function submitFeedback(alertId: string, payload: {
  selected_cause_rank: number | null
  final_root_cause: string
  action_taken: string
  recurrence_risk: 'high' | 'medium' | 'low'
  notes: string
}, role: string) {
  return request<FeedbackRecord>(`/api/alerts/${alertId}/feedback`, role, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function createKnowledgeCase(payload: {
  alarm_code: string
  equipment_family: string
  root_cause: string
  action: string
  tags: string[]
  source: string
  alert_id: string
}, role: string) {
  return request<KnowledgeCase>('/api/knowledge-cases', role, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}
