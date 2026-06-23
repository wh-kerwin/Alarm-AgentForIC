import type { Alert, AnalysisResult, FeedbackRecord } from './types'

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })

  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    throw new Error(body.error || `HTTP ${response.status}`)
  }

  return response.json() as Promise<T>
}

export function getHealth() {
  return request<{ status: string; version: string }>('/api/health')
}

export function getAlerts() {
  return request<Alert[]>('/api/alerts')
}

export function analyzeAlert(alertId: string) {
  return request<AnalysisResult>(`/api/alerts/${alertId}/analyze`, { method: 'POST' })
}

export function getFeedback(alertId: string) {
  return request<FeedbackRecord[]>(`/api/alerts/${alertId}/feedback`)
}

export function submitFeedback(alertId: string, payload: {
  selected_cause_rank: number | null
  final_root_cause: string
  action_taken: string
  recurrence_risk: 'high' | 'medium' | 'low'
  notes: string
}) {
  return request<FeedbackRecord>(`/api/alerts/${alertId}/feedback`, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

