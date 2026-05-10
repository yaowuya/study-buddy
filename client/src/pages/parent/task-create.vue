<template>
  <view class="create-page">
    <view class="form-section">
      <view class="role-selector">
        <view :class="['role-btn', form.type === 'school' ? 'role-active-school' : '']" @tap="form.type = 'school'">
          <text>学校任务</text>
        </view>
        <view :class="['role-btn', form.type === 'home' ? 'role-active-home' : '']" @tap="form.type = 'home'">
          <text>家庭任务</text>
        </view>
      </view>

      <input v-model="form.title" placeholder="任务标题" class="input" />
      <textarea v-model="form.desc" placeholder="任务描述（选填）" class="textarea" />
      <input v-model.number="form.duration" type="number" placeholder="预计耗时（分钟，选填）" class="input" />

      <view class="subject-row">
        <text class="label">学科</text>
        <view class="chips">
          <view v-for="s in subjects" :key="s" :class="['chip', form.subject === s ? 'chip-active' : '']" @tap="form.subject = s">
            <text>{{ s }}</text>
          </view>
        </view>
      </view>

      <button class="btn-primary" @tap="handleSubmit">发布</button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { createTask } from '@/api/tasks'

const subjects = ['语文', '数学', '英语']

const form = reactive({
  type: 'school' as 'school' | 'home',
  title: '',
  desc: '',
  duration: null as number | null,
  date: new Date().toISOString().slice(0, 10),
  subject: '' as string,
})

async function handleSubmit() {
  if (!form.title.trim()) {
    uni.showToast({ title: '请输入任务标题', icon: 'none' })
    return
  }
  try {
    await createTask({
      type: form.type,
      title: form.title,
      desc: form.desc || undefined,
      duration: form.duration || undefined,
      date: form.date,
      subject: form.subject || undefined,
    })
    uni.showToast({ title: '发布成功', icon: 'success' })
    setTimeout(() => uni.navigateBack(), 500)
  } catch (e: any) {
    uni.showToast({ title: e.message, icon: 'none' })
  }
}
</script>

<style lang="scss" scoped>
@import '@/static/styles/variables.scss';

.create-page { padding: $spacing-md; }
.form-section { display: flex; flex-direction: column; gap: $spacing-sm; }

.role-selector { display: flex; gap: $spacing-sm; }
.role-btn {
  flex: 1; height: $touch-min; display: flex; align-items: center; justify-content: center;
  border: 2px solid $color-outline-variant; border-radius: $radius-md; font-weight: 500;
}
.role-active-school { border-color: $color-primary; background: rgba($color-primary, 0.08); color: $color-primary; }
.role-active-home { border-color: #8B5CF6; background: rgba(#8B5CF6, 0.08); color: #8B5CF6; }

.input, .textarea {
  padding: 0 $spacing-sm; height: $touch-min; border: 1px solid $color-outline-variant;
  border-radius: $radius-md; font-size: $font-body-md; background: #fff;
}
.textarea { height: 80px; padding-top: 12px; }

.subject-row { display: flex; align-items: center; gap: $spacing-sm; }
.label { font-size: $font-body-md; color: $color-on-surface-variant; min-width: 40px; }
.chips { display: flex; gap: 8px; }
.chip {
  padding: 4px 12px; border-radius: $radius-full; font-size: $font-label;
  background: rgba($color-primary, 0.06); color: $color-on-surface-variant;
}
.chip-active { background: $color-primary; color: #fff; }

.btn-primary {
  height: $touch-min; background: $color-primary; color: #fff;
  border-radius: $radius-md; font-size: $font-body-md; font-weight: 600; border: none; margin-top: $spacing-md;
}
</style>
