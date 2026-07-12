import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as api from '@/api/homework-plans'
import type { HomeworkPlanCreateParams, HomeworkPlanDetail, HomeworkPlanSummary, HomeworkPlanUpdateParams } from '@/api/homework-plans'

export const useHomeworkPlansStore = defineStore('homework-plans', () => {
  const activePlans = ref<HomeworkPlanSummary[]>([])
  const currentPlan = ref<HomeworkPlanDetail | null>(null)
  const listLoading = ref(false)
  const detailLoading = ref(false)
  const saving = ref(false)
  const deleting = ref(false)
  const syncing = ref(false)
  const syncWarning = ref<string | null>(null)
  let syncPromise: Promise<api.MaterializeResult> | null = null

  async function fetchActivePlans() {
    listLoading.value = true
    try { activePlans.value = await api.listActiveHomeworkPlans() }
    finally { listLoading.value = false }
  }

  async function fetchPlan(id: string) {
    detailLoading.value = true
    try { currentPlan.value = await api.getHomeworkPlan(id); return currentPlan.value }
    finally { detailLoading.value = false }
  }

  async function createPlan(payload: HomeworkPlanCreateParams) {
    saving.value = true
    try { return await api.createHomeworkPlan(payload) }
    finally { saving.value = false }
  }

  async function updatePlan(id: string, payload: HomeworkPlanUpdateParams) {
    saving.value = true
    try {
      const updated = await api.updateHomeworkPlan(id, payload)
      currentPlan.value = updated
      const index = activePlans.value.findIndex(plan => plan.id === id)
      if (index >= 0) activePlans.value.splice(index, 1, updated)
      return updated
    } finally { saving.value = false }
  }

  async function deletePlan(id: string) {
    deleting.value = true
    try {
      await api.deleteHomeworkPlan(id)
      activePlans.value = activePlans.value.filter(plan => plan.id !== id)
      if (currentPlan.value?.id === id) currentPlan.value = null
    } finally { deleting.value = false }
  }

  function materialize() {
    if (syncPromise) return syncPromise
    syncing.value = true
    syncWarning.value = null
    syncPromise = api.materializeHomeworkPlans().then(result => {
      if (result.failed_count) syncWarning.value = '部分计划作业生成失败，请稍后重试'
      return result
    }).finally(() => {
      syncing.value = false
      syncPromise = null
    })
    return syncPromise
  }

  function clearSyncWarning() { syncWarning.value = null }
  function clearCurrentPlan() { currentPlan.value = null }
  function reset() {
    activePlans.value = []
    currentPlan.value = null
    syncWarning.value = null
    listLoading.value = detailLoading.value = saving.value = deleting.value = syncing.value = false
    syncPromise = null
  }

  return { activePlans, currentPlan, listLoading, detailLoading, saving, deleting, syncing, syncWarning,
    fetchActivePlans, fetchPlan, createPlan, updatePlan, deletePlan, materialize,
    clearSyncWarning, clearCurrentPlan, reset }
})
