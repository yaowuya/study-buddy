export interface PlanSyncDependencies {
  materialize: () => Promise<unknown>
  fetchTasks: () => Promise<unknown>
  fetchPlans?: () => Promise<unknown>
  onSyncError?: () => void
}

export async function synchronizeHomeworkPage({
  materialize,
  fetchTasks,
  fetchPlans,
  onSyncError,
}: PlanSyncDependencies): Promise<void> {
  try {
    await materialize()
  } catch {
    onSyncError?.()
  }

  const requests = [fetchTasks()]
  if (fetchPlans) requests.push(fetchPlans())
  await Promise.allSettled(requests)
}
