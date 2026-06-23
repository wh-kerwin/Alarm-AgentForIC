export type Severity = 'critical' | 'high' | 'medium' | 'low'
export type Confidence = 'high' | 'medium' | 'low'

export interface Alert {
  alert_id: string
  source: string
  severity: Severity
  status: string
  equipment_id: string
  chamber_id: string
  alarm_code: string
  alarm_message: string
  timestamp: string
  lot_id: string
  wafer_id: string
  recipe_id: string
  product_id: string
  current_state: string
  owner_role: string
  summary: string
}

export interface EventItem {
  time: string
  event_type: string
  title: string
  description: string
  source: string
  severity: Severity
}

export interface Evidence {
  label: string
  detail: string
  source: string
  strength: Confidence
}

export interface RootCauseCandidate {
  rank: number
  cause: string
  confidence: Confidence
  category: string
  evidence: Evidence[]
  counter_evidence: string[]
  verification_steps: string[]
  recommended_actions: string[]
}

export interface CollectionPolicy {
  policy_id: string
  alarm_code: string
  equipment_family: string
  time_window_minutes: number
  required_sources: string[]
  optional_sources: string[]
  fallback_note: string
}

export interface CollectionStatus {
  policy: CollectionPolicy
  collected_sources: string[]
  missing_required_sources: string[]
  missing_optional_sources: string[]
  fallback_notes: string[]
}

export interface AnalysisResult {
  alert_id: string
  alert_summary: string
  generated_at: string
  impact_scope: Record<string, string>
  timeline: EventItem[]
  root_cause_candidates: RootCauseCandidate[]
  handling_recommendations: string[]
  escalation: {
    required: boolean
    target_role: string
    reason: string
  }
  agent_limitations: string[]
  data_sources: string[]
  collection_status: CollectionStatus
}

export interface FeedbackRecord {
  feedback_id: string
  alert_id: string
  selected_cause_rank: number | null
  final_root_cause: string
  action_taken: string
  recurrence_risk: Confidence
  notes: string
  created_at: string
}

export interface KnowledgeCase {
  case_id: string
  alarm_code: string
  equipment_family: string
  root_cause: string
  action: string
  tags: string[]
  source: string
  created_at: string
}
