<template>
  <view class="page">
    <view class="appbar" :style="{ paddingTop: Math.max(statusBarHeight, 12) + 'px' }"><view class="back" @tap="handleBack">‹</view><text>编辑作业计划</text></view>
    <view v-if="conflictMessage" class="conflict-panel">
      <text>{{ conflictMessage }}</text>
      <button :disabled="operationLocked" @tap="reloadPlan">重新加载计划</button>
    </view>
    <view v-if="plansStore.detailLoading || !form" class="loading">加载中…</view>
    <scroll-view v-else scroll-y class="content" :style="{ paddingTop: (Math.max(statusBarHeight, 12) + 76) + 'px' }">
      <view class="notice">修改仅影响之后尚未生成的作业；已经生成的作业不会改变。</view>
      <view class="card"><text class="heading">作业时间计划</text><view class="dates"><picker mode="date" :value="form.start_date" :disabled="started || operationLocked" @change="updateStartDate"><view class="field">开始：{{ form.start_date }}</view></picker><picker mode="date" :value="form.end_date" :disabled="operationLocked" @change="updateEndDate"><view class="field">结束：{{ form.end_date }}</view></picker></view><text v-if="errors.dates" class="field-error">{{ errors.dates }}</text></view>
      <view class="card"><text class="heading">选择科目</text><view class="subjects"><button v-for="subject in ['语文','数学','英语']" :key="subject" :disabled="operationLocked" :class="{active:form.subject===subject}" @tap="form.subject=subject">{{ subject }}</button></view></view>
      <view class="card"><text class="heading">为作业起个好名字</text><input v-model="form.title" :disabled="operationLocked" class="field" @input="errors.title=''" /><text v-if="errors.title" class="field-error">{{ errors.title }}</text></view>
      <DictationConfig v-model:enabled="dictationEnabled" v-model:words="words" :disabled="operationLocked" :error="errors.dictation" @clear-error="errors.dictation=''" />
      <view class="card"><text class="heading">留下你的温馨提示</text><textarea v-model="form.desc" :disabled="operationLocked" class="field textarea" /></view>
      <view class="card"><text class="heading">预计需要多长时间？</text><input v-model.number="form.duration" :disabled="operationLocked" class="field" type="number" @input="errors.duration=''" /><text v-if="errors.duration" class="field-error">{{ errors.duration }}</text></view>
      <text class="save-note">保存后，新内容从下一份尚未生成的作业开始生效。</text>
      <button class="save" :disabled="operationLocked" @tap="save">{{ plansStore.saving?'保存中…':'保存修改' }}</button>
      <button class="delete" :disabled="operationLocked" @tap="showDelete=true">{{ plansStore.deleting ? '删除中…' : '删除这个计划' }}</button>
      <view class="spacer" />
    </scroll-view>
    <ConfirmModal v-model:visible="showDiscard" type="warning" icon="warning" title="放弃修改？" desc="尚未保存的修改将会丢失。" cancel-text="继续编辑" confirm-text="放弃修改" @confirm="leave" />
    <ConfirmModal v-model:visible="showDelete" type="warning" icon="delete" title="删除这个计划？" desc="删除后将停止生成后续作业，已经生成的作业仍会保留。" cancel-text="取消" confirm-text="确认删除" @confirm="remove" />
  </view>
</template>
<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { onBackPress, onLoad, onUnload } from '@dcloudio/uni-app'
import { useAuthStore } from '@/stores/auth'
import { useHomeworkPlansStore } from '@/stores/homework-plans'
import { localToday } from '@/utils/local-date'
import DictationConfig from '@/components/DictationConfig.vue'
import ConfirmModal from '@/components/ConfirmModal.vue'
import type { HomeworkPlanUpdateParams } from '@/api/homework-plans'
const auth = useAuthStore()
const plansStore = useHomeworkPlansStore()
const statusBarHeight = ref(0)
const id = ref('')
const form = ref<HomeworkPlanUpdateParams | null>(null)
const initial = ref('')
const words = ref<string[]>([])
const dictationEnabled = ref(false)
const showDiscard = ref(false)
const showDelete = ref(false)
const conflictMessage = ref('')
const errors = ref({ title: '', dates: '', duration: '', dictation: '' })
const operationLocked = computed(() => plansStore.saving || plansStore.deleting)
const started = computed(() => !!form.value && form.value.start_date <= localToday())

function normalized() {
  if (!form.value) return ''
  return JSON.stringify({
    ...form.value,
    title: form.value.title.trim(),
    desc: form.value.desc?.trim() || null,
    duration: form.value.duration || null,
    subject: form.value.subject || null,
    dictation_items: dictationEnabled.value ? words.value.map(content => ({ content: content.trim() })) : [],
  })
}
const dirty = computed(() => !!form.value && normalized() !== initial.value)

function applyPlan(plan: Awaited<ReturnType<typeof plansStore.fetchPlan>>) {
  form.value = { type: plan.type, title: plan.title, desc: plan.desc, duration: plan.duration,
    subject: plan.subject, start_date: plan.start_date, end_date: plan.end_date, updated_at: plan.updated_at,
    dictation_items: [] }
  words.value = plan.dictation_items.map(item => item.content)
  dictationEnabled.value = words.value.length > 0
  conflictMessage.value = ''
  errors.value = { title: '', dates: '', duration: '', dictation: '' }
  initial.value = normalized()
}

async function loadPlan() {
  const plan = await plansStore.fetchPlan(id.value)
  applyPlan(plan)
}

onLoad(async (query: any) => {
  if (!query.id || !auth.isParent()) { uni.redirectTo({ url: '/pages/parent/dashboard' }); return }
  id.value = query.id
  try { await loadPlan() }
  catch (error: any) { uni.showToast({ title: error.message || '加载失败', icon: 'none' }); uni.redirectTo({ url: '/pages/parent/dashboard' }) }
})
onMounted(() => { statusBarHeight.value = uni.getSystemInfoSync().statusBarHeight || 0 })
onUnload(() => plansStore.clearCurrentPlan())
onBackPress(() => {
  if (operationLocked.value) return true
  if (dirty.value) { showDiscard.value = true; return true }
  return false
})

function updateStartDate(event: any) { if (form.value) form.value.start_date = event.detail.value; errors.value.dates = '' }
function updateEndDate(event: any) { if (form.value) form.value.end_date = event.detail.value; errors.value.dates = '' }
function handleBack() { if (operationLocked.value) return; dirty.value ? showDiscard.value = true : leave() }
function leave() { if (!operationLocked.value) uni.redirectTo({ url: '/pages/parent/dashboard' }) }
function validate() {
  if (!form.value) return false
  errors.value = { title: '', dates: '', duration: '', dictation: '' }
  if (!form.value.title.trim()) errors.value.title = '请输入作业标题'
  if (form.value.end_date < form.value.start_date || form.value.end_date < localToday()) errors.value.dates = '结束日期不能早于开始日期或今天'
  if (form.value.duration != null && form.value.duration <= 0) errors.value.duration = '预计时长必须大于 0'
  if (dictationEnabled.value && !words.value.length) errors.value.dictation = '开启听写后，请至少添加一个词条'
  return !Object.values(errors.value).some(Boolean)
}
async function save() {
  if (!form.value || !validate() || operationLocked.value) return
  conflictMessage.value = ''
  try {
    await plansStore.updatePlan(id.value, { ...form.value,
      title: form.value.title.trim(), desc: form.value.desc?.trim() || null,
      dictation_items: dictationEnabled.value ? words.value.map(content => ({ content: content.trim() })) : [] })
    initial.value = normalized()
    uni.showToast({ title: '计划修改已保存', icon: 'success' })
    leave()
  } catch (error: any) {
    if (error.statusCode === 409 || error.status === 409 || /409|changed|修改/.test(error.message || '')) {
      conflictMessage.value = '计划已被其他家长修改，请重新加载后再编辑。'
      return
    }
    uni.showToast({ title: error.message || '保存失败', icon: 'none' })
  }
}
async function reloadPlan() { if (!operationLocked.value) try { await loadPlan() } catch (error: any) { uni.showToast({ title: error.message || '重新加载失败', icon: 'none' }) } }
async function remove() {
  if (operationLocked.value) return
  try { await plansStore.deletePlan(id.value); uni.showToast({ title: '计划已删除，已有作业不受影响', icon: 'none' }); leave() }
  catch (error: any) { uni.showToast({ title: error.message || '删除失败', icon: 'none' }) }
}
</script>
<style lang="scss" scoped>
@use '@/static/styles/variables.scss' as *;.page{min-height:100vh;background:$color-organic-bg}.appbar{position:fixed;z-index:10;top:0;left:0;right:0;height:64px;background:#fff;display:flex;align-items:center;justify-content:center;font-size:22px;font-weight:600}.back{position:absolute;left:16px;font-size:36px}.loading{padding-top:140px;text-align:center}.content{padding:0 24px 60px;box-sizing:border-box}.notice{padding:13px;border-radius:14px;background:#fff4dc;color:#765b12;margin-bottom:16px;font-size:13px}.card{background:#fff;border-radius:24px;padding:20px;margin-bottom:16px}.heading{display:block;font-size:18px;font-weight:600;margin-bottom:12px}.field{min-height:48px;background:#f1f5f9;border-radius:12px;padding:12px;box-sizing:border-box}.dates,.subjects{display:flex;gap:10px}.dates picker,.subjects button{flex:1}.subjects button{border:0;border-radius:12px}.subjects .active{background:#4caf50;color:#fff}.textarea{height:110px}.save-note{display:block;color:#64748b;font-size:12px;margin:8px}.save{border:0;border-radius:999px;background:#4caf50;color:#fff}.delete{border:0;background:transparent;color:#b3261e;margin-top:10px}.conflict-panel{margin:92px 24px 0;padding:14px;border-radius:14px;background:#fff4dc;color:#765b12;display:flex;align-items:center;justify-content:space-between;gap:12px}.conflict-panel button{margin:0;min-height:40px;border:0;border-radius:999px;background:#765b12;color:#fff;font-size:12px}.conflict-panel + .loading{padding-top:32px}.field-error{display:block;margin-top:8px;color:#c62828;font-size:12px;line-height:18px}.save:disabled,.delete:disabled{opacity:.55}.spacer{height:50px}
</style>
