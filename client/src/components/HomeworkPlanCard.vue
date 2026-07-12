<template>
  <view :class="['plan-card', `plan-${plan.subject || 'default'}`]">
    <view class="plan-header">
      <view class="plan-icon"><text class="material-symbols-outlined">{{ subjectIcon }}</text></view>
      <text class="plan-title">{{ plan.title }}</text>
      <view class="status-badge">{{ plan.status === 'active' ? '进行中' : '即将开始' }}</view>
      <view v-if="plan.has_dictation" class="dictation-badge">听写</view>
    </view>
    <view class="plan-content">
      <text class="frequency">每天 1 份</text>
      <text class="range">{{ plan.start_date }}—{{ plan.end_date }} · {{ contextLabel }}</text>
      <view class="progress-track"><view class="progress-fill" :style="{ width: progress + '%' }" /></view>
      <text class="generated">已生成 {{ plan.generated_count }} / {{ plan.total_days }} 份 · {{ plan.today_generated ? '今天已生成' : '今天待生成' }}</text>
      <view class="metadata">
        <text v-if="plan.subject" class="chip">{{ plan.subject }}</text>
        <text v-if="plan.has_dictation" class="chip">听写 · {{ plan.dictation_count }} 个词</text>
        <text v-if="plan.duration" class="chip">约 {{ plan.duration }} 分钟</text>
      </view>
      <text v-if="plan.desc" class="description">{{ plan.desc }}</text>
    </view>
    <view class="actions">
      <button class="edit-btn" :disabled="busy" @tap="emit('edit', plan.id)">编辑计划</button>
      <button class="delete-btn" :disabled="busy" @tap="emit('delete', plan.id)">删除</button>
    </view>
  </view>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import type { HomeworkPlanSummary } from '@/api/homework-plans'
const props = withDefaults(defineProps<{ plan: HomeworkPlanSummary; busy?: boolean }>(), { busy: false })
const emit = defineEmits<{ edit: [id: string]; delete: [id: string] }>()
const progress = computed(() => Math.min(100, Math.max(0, props.plan.total_days ? props.plan.generated_count / props.plan.total_days * 100 : 0)))
const contextLabel = computed(() => props.plan.status === 'active' ? `还剩 ${props.plan.remaining_days} 天` : `${props.plan.days_until_start} 天后开始`)
const subjectIcon = computed(() => ({ 语文:'menu_book', 数学:'calculate', 英语:'language', 科学:'science' }[props.plan.subject || ''] || 'assignment'))
</script>
<style lang="scss" scoped>
.plan-card{background:#fff;border-radius:24px;padding:24px;box-shadow:0 12px 32px rgba(0,0,0,.06);margin-bottom:16px;display:flex;flex-direction:column;gap:16px}.plan-header{display:flex;align-items:center;gap:8px}.plan-icon{width:30px;height:30px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:#f1eded}.plan-icon text{font-size:15px}.plan-title{flex:1;min-width:0;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;font-size:16px;font-weight:700;color:#1d3b16}.status-badge,.dictation-badge,.chip{border-radius:999px;padding:4px 9px;font-size:12px}.status-badge{background:#e7eee8;color:#52645a;font-weight:700}.dictation-badge{background:#1d3b16;color:#fff}.plan-content{padding:20px;border-radius:16px;background:#f1eded;display:flex;flex-direction:column;gap:8px}.plan-语文 .plan-icon,.plan-语文 .edit-btn{background:#e5d9f2}.plan-语文 .plan-content{background:rgba(229,217,242,.3)}.plan-数学 .plan-icon,.plan-数学 .edit-btn{background:#ffe4d6}.plan-数学 .plan-content{background:rgba(255,228,214,.3)}.plan-英语 .plan-icon,.plan-英语 .edit-btn{background:#b9f0a6}.plan-英语 .plan-content{background:#e8f8e2}.frequency,.range{color:#1d3b16;font-weight:700}.range{font-size:14px}.progress-track{height:8px;background:rgba(29,59,22,.1);border-radius:99px;overflow:hidden}.progress-fill{height:100%;background:#4caf50;border-radius:99px}.generated,.description{font-size:13px;color:#52645a}.metadata{display:flex;gap:7px;flex-wrap:wrap}.chip{background:rgba(255,255,255,.8)}.description{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;line-height:20px}.actions{display:flex;align-items:center;gap:10px}.edit-btn{flex:1;min-height:44px;border:0;border-radius:999px;font-size:14px;font-weight:700}.delete-btn{min-height:44px;border:0;background:transparent;color:#b3261e;font-size:14px}
</style>
