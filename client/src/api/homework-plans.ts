import { request } from './request'

export type PlanRangeType = 'week' | 'month' | 'custom'
export type HomeworkPlanStatus = 'upcoming' | 'active'

export interface PlanDictationItem { content: string }

export interface HomeworkPlanCreateParams {
  type: 'school' | 'home'
  title: string
  desc?: string
  duration?: number
  subject?: string
  range_type: PlanRangeType
  start_date?: string
  end_date?: string
  dictation_items: PlanDictationItem[]
}

export interface HomeworkPlanUpdateParams {
  type: 'school' | 'home'
  title: string
  desc?: string | null
  duration?: number | null
  subject?: string | null
  start_date: string
  end_date: string
  updated_at: string
  dictation_items: PlanDictationItem[]
}

export interface HomeworkPlanSummary {
  id: string
  type: 'school' | 'home'
  title: string
  desc: string | null
  duration: number | null
  subject: string | null
  start_date: string
  end_date: string
  status: HomeworkPlanStatus
  has_dictation: boolean
  dictation_count: number
  total_days: number
  generated_count: number
  remaining_days: number | null
  days_until_start: number | null
  today_generated: boolean
  updated_at: string
}

export interface HomeworkPlanDetail extends HomeworkPlanSummary {
  dictation_items: PlanDictationItem[]
}

export interface PlanMaterializeResult {
  plan_id: string
  created_dates: string[]
  status: 'success' | 'failed'
  error: 'materialization_failed' | 'plan_changed' | 'plan_unavailable' | null
}

export interface MaterializeResult {
  created_count: number
  success_count: number
  failed_count: number
  plans: PlanMaterializeResult[]
}

export const createHomeworkPlan = (payload: HomeworkPlanCreateParams) =>
  request<HomeworkPlanDetail>('/homework-plans/', 'POST', payload)

export const listActiveHomeworkPlans = () =>
  request<HomeworkPlanSummary[]>('/homework-plans/', 'GET')

export const getHomeworkPlan = (id: string) =>
  request<HomeworkPlanDetail>(`/homework-plans/${encodeURIComponent(id)}`, 'GET')

export const updateHomeworkPlan = (id: string, payload: HomeworkPlanUpdateParams) =>
  request<HomeworkPlanDetail>(`/homework-plans/${encodeURIComponent(id)}`, 'PATCH', payload)

export const deleteHomeworkPlan = (id: string) =>
  request<{ ok: boolean }>(`/homework-plans/${encodeURIComponent(id)}`, 'DELETE')

export const materializeHomeworkPlans = () =>
  request<MaterializeResult>('/homework-plans/materialize', 'POST')
