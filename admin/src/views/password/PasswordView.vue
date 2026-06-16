<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { changePassword } from '@/api/auth'
import { useAuthStore } from '@/stores/auth'
import { message } from 'ant-design-vue'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)
const form = reactive({ old_password: '', new_password: '', confirm_password: '' })

async function handleSubmit() {
  if (form.new_password !== form.confirm_password) {
    message.error('两次输入的新密码不一致')
    return
  }
  loading.value = true
  try {
    await changePassword({ old_password: form.old_password, new_password: form.new_password })
    message.success('密码修改成功，请重新登录')
    authStore.logout()
    router.push('/login')
  } catch (err: any) {
    message.error(err.response?.data?.detail || '修改失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div>
    <h2 style="margin-bottom:24px">修改密码</h2>
    <a-card style="max-width:480px">
      <a-form layout="vertical">
        <a-form-item label="旧密码">
          <a-input-password v-model:value="form.old_password" placeholder="请输入旧密码" />
        </a-form-item>
        <a-form-item label="新密码（至少8位）">
          <a-input-password v-model:value="form.new_password" placeholder="请输入新密码" />
        </a-form-item>
        <a-form-item label="确认新密码">
          <a-input-password v-model:value="form.confirm_password" placeholder="请再次输入新密码" />
        </a-form-item>
        <a-form-item>
          <a-button type="primary" :loading="loading" @click="handleSubmit">确认修改</a-button>
        </a-form-item>
      </a-form>
    </a-card>
  </div>
</template>
