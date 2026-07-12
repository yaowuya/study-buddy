<template>
  <view class="dictation-card">
    <view class="dictation-header">
      <view class="dictation-title-row">
        <text class="material-symbols-outlined dictation-icon">record_voice_over</text>
        <text class="dictation-title">开启听写</text>
      </view>
      <switch :checked="enabled" color="#4CAF50" :disabled="disabled" @change="toggle" />
    </view>
    <view v-if="enabled" class="dictation-body">
      <view class="word-input-row">
        <input v-model="wordInput" class="word-input" :disabled="disabled" placeholder="输入需要听写的生字或单词..." @confirm="addWord" />
        <button class="add-word-btn" :disabled="disabled" @tap="addWord">添加</button>
      </view>
      <view v-if="words.length" class="word-tags">
        <view v-for="(word, index) in words" :key="word" class="word-tag">
          <text>{{ word }}</text>
          <text class="material-symbols-outlined tag-close" @tap="removeWord(index)">close</text>
        </view>
      </view>
      <text class="dictation-hint">输入需要听写的生字或单词，我们将为每天的作业生成听写卡片。</text>
      <text v-if="error" class="field-error">{{ error }}</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const props = withDefaults(defineProps<{ enabled: boolean; words: string[]; disabled?: boolean; error?: string }>(), {
  disabled: false,
  error: '',
})
const emit = defineEmits<{ 'update:enabled': [value: boolean]; 'update:words': [value: string[]]; 'clear-error': [] }>()
const wordInput = ref('')

function toggle(event: any) { emit('update:enabled', !!event.detail.value); emit('clear-error') }
function addWord() {
  const word = wordInput.value.trim()
  if (word && !props.words.some(item => item.toLocaleLowerCase() === word.toLocaleLowerCase())) {
    emit('update:words', [...props.words, word]); emit('clear-error')
  }
  wordInput.value = ''
}
function removeWord(index: number) {
  if (!props.disabled) emit('update:words', props.words.filter((_, itemIndex) => itemIndex !== index))
}
</script>

<style lang="scss" scoped>
.dictation-card { background: linear-gradient(145deg,#eefbee,#fff 70%); border: 1px solid #b7e6b9; border-radius: 24px; padding: 20px; margin-bottom: 20px; }
.dictation-header,.dictation-title-row,.word-input-row,.word-tags,.word-tag { display:flex; align-items:center; }
.dictation-header { justify-content:space-between; }
.dictation-title-row { gap:8px; }.dictation-icon { color:#3a692e; font-size:24px; }.dictation-title { font-size:18px; font-weight:600; color:#1e293b; }
.dictation-body { margin-top:16px; }.word-input-row { gap:8px; }.word-input { flex:1; min-height:44px; background:#f1f5f9; border-radius:12px; padding:0 16px; font-size:14px; }
.add-word-btn { min-height:44px; margin:0; padding:0 18px; border:0; border-radius:12px; background:#4caf50; color:#fff; font-size:14px; line-height:44px; }
.word-tags { gap:7px; flex-wrap:wrap; margin-top:12px; }.word-tag { gap:4px; padding:6px 10px; border-radius:999px; background:#d9f3d5; color:#285f2d; font-size:13px; }.tag-close { font-size:17px; }
.dictation-hint,.field-error { display:block; margin-top:10px; font-size:12px; line-height:18px; }.dictation-hint { color:#64748b; }.field-error { color:#c62828; }
</style>
