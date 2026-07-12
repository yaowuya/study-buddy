<template>
  <view class="page">
    <view class="appbar" :style="{ paddingTop: Math.max(statusBarHeight, 12) + 'px' }"><view class="back" @tap="handleBack">‹</view><text>编辑作业计划</text></view>
    <view v-if="plansStore.detailLoading || !form" class="loading">加载中…</view>
    <scroll-view v-else scroll-y class="content" :style="{ paddingTop: (Math.max(statusBarHeight, 12) + 76) + 'px' }">
      <view class="notice">修改仅影响之后尚未生成的作业；已经生成的作业不会改变。</view>
      <view class="card"><text class="heading">作业时间计划</text><view class="dates"><picker mode="date" :value="form.start_date" :disabled="started" @change="form.start_date=$event.detail.value"><view class="field">开始：{{ form.start_date }}</view></picker><picker mode="date" :value="form.end_date" @change="form.end_date=$event.detail.value"><view class="field">结束：{{ form.end_date }}</view></picker></view></view>
      <view class="card"><text class="heading">选择科目</text><view class="subjects"><button v-for="subject in ['语文','数学','英语']" :key="subject" :class="{active:form.subject===subject}" @tap="form.subject=subject">{{ subject }}</button></view></view>
      <view class="card"><text class="heading">为作业起个好名字</text><input v-model="form.title" class="field" /></view>
      <DictationConfig v-model:enabled="dictationEnabled" v-model:words="words" />
      <view class="card"><text class="heading">留下你的温馨提示</text><textarea v-model="form.desc" class="field textarea" /></view>
      <view class="card"><text class="heading">预计需要多长时间？</text><input v-model.number="form.duration" class="field" type="number" /></view>
      <text class="save-note">保存后，新内容从下一份尚未生成的作业开始生效。</text>
      <button class="save" :disabled="plansStore.saving" @tap="save">{{ plansStore.saving?'保存中…':'保存修改' }}</button>
      <button class="delete" @tap="showDelete=true">删除这个计划</button>
      <view class="spacer" />
    </scroll-view>
    <ConfirmModal v-model:visible="showDiscard" type="warning" icon="warning" title="放弃修改？" desc="尚未保存的修改将会丢失。" cancel-text="继续编辑" confirm-text="放弃修改" @confirm="leave" />
    <ConfirmModal v-model:visible="showDelete" type="warning" icon="delete" title="删除这个计划？" desc="删除后将停止生成后续作业，已经生成的作业仍会保留。" cancel-text="取消" confirm-text="确认删除" @confirm="remove" />
  </view>
</template>
<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { onLoad, onUnload } from '@dcloudio/uni-app'
import { useAuthStore } from '@/stores/auth'
import { useHomeworkPlansStore } from '@/stores/homework-plans'
import { localToday } from '@/utils/local-date'
import DictationConfig from '@/components/DictationConfig.vue'
import ConfirmModal from '@/components/ConfirmModal.vue'
import type { HomeworkPlanUpdateParams } from '@/api/homework-plans'
const auth=useAuthStore(), plansStore=useHomeworkPlansStore(); const statusBarHeight=ref(0), id=ref(''), form=ref<any>(null), initial=ref(''), words=ref<string[]>([]), dictationEnabled=ref(false), showDiscard=ref(false), showDelete=ref(false)
const started=computed(()=>!!form.value&&form.value.start_date<=localToday()); const normalized=()=>JSON.stringify({...form.value,dictation_items:dictationEnabled.value?words.value.map(content=>({content})):[]}); const dirty=computed(()=>!!form.value&&normalized()!==initial.value)
onLoad(async(query:any)=>{if(!query.id||!auth.isParent()){uni.redirectTo({url:'/pages/parent/dashboard'});return}id.value=query.id;try{const plan=await plansStore.fetchPlan(id.value);form.value={type:plan.type,title:plan.title,desc:plan.desc,duration:plan.duration,subject:plan.subject,start_date:plan.start_date,end_date:plan.end_date,updated_at:plan.updated_at};words.value=plan.dictation_items.map(i=>i.content);dictationEnabled.value=words.value.length>0;initial.value=normalized()}catch(e:any){uni.showToast({title:e.message||'加载失败',icon:'none'});uni.redirectTo({url:'/pages/parent/dashboard'})}})
onMounted(()=>{statusBarHeight.value=uni.getSystemInfoSync().statusBarHeight||0});onUnload(()=>plansStore.clearCurrentPlan())
function handleBack(){dirty.value?showDiscard.value=true:leave()} function leave(){uni.redirectTo({url:'/pages/parent/dashboard'})}
async function save(){if(!form.value.title.trim()||(dictationEnabled.value&&!words.value.length)){uni.showToast({title:'请完善作业信息',icon:'none'});return}try{await plansStore.updatePlan(id.value,{...form.value,dictation_items:dictationEnabled.value?words.value.map(content=>({content})):[]} as HomeworkPlanUpdateParams);uni.showToast({title:'计划修改已保存',icon:'success'});leave()}catch(e:any){uni.showToast({title:e.message||'保存失败',icon:'none'})}}
async function remove(){try{await plansStore.deletePlan(id.value);uni.showToast({title:'计划已删除，已有作业不受影响',icon:'none'});leave()}catch(e:any){uni.showToast({title:e.message||'删除失败',icon:'none'})}}
</script>
<style lang="scss" scoped>
@use '@/static/styles/variables.scss' as *;.page{min-height:100vh;background:$color-organic-bg}.appbar{position:fixed;z-index:10;top:0;left:0;right:0;height:64px;background:#fff;display:flex;align-items:center;justify-content:center;font-size:22px;font-weight:600}.back{position:absolute;left:16px;font-size:36px}.loading{padding-top:140px;text-align:center}.content{padding:0 24px 60px;box-sizing:border-box}.notice{padding:13px;border-radius:14px;background:#fff4dc;color:#765b12;margin-bottom:16px;font-size:13px}.card{background:#fff;border-radius:24px;padding:20px;margin-bottom:16px}.heading{display:block;font-size:18px;font-weight:600;margin-bottom:12px}.field{min-height:48px;background:#f1f5f9;border-radius:12px;padding:12px;box-sizing:border-box}.dates,.subjects{display:flex;gap:10px}.dates picker,.subjects button{flex:1}.subjects button{border:0;border-radius:12px}.subjects .active{background:#4caf50;color:#fff}.textarea{height:110px}.save-note{display:block;color:#64748b;font-size:12px;margin:8px}.save{border:0;border-radius:999px;background:#4caf50;color:#fff}.delete{border:0;background:transparent;color:#b3261e;margin-top:10px}.spacer{height:50px}
</style>
