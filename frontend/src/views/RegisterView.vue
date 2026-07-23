<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()
const email = ref('')
const password = ref('')
const nickname = ref('')
const error = ref('')
const loading = ref(false)

async function handleRegister() {
  error.value = ''
  if (password.value.length < 8) {
    error.value = '密码至少8位'
    return
  }
  loading.value = true
  try {
    await auth.register(email.value, password.value, nickname.value)
    router.push('/')
  } catch (e: any) {
    error.value = e.response?.data?.msg || '注册失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex flex-col px-6 pt-16">
    <div class="mb-8">
      <h1 class="text-2xl font-bold text-slate-800">创建账号</h1>
      <p class="text-slate-400 mt-1">开启你的优势探索之旅</p>
    </div>

    <form @submit.prevent="handleRegister" class="space-y-4">
      <div>
        <label class="block text-sm text-slate-500 mb-1">昵称</label>
        <input
          v-model="nickname"
          type="text"
          required
          minlength="2"
          maxlength="20"
          class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-indigo-400 focus:outline-none text-slate-800"
          placeholder="你的昵称"
        />
      </div>
      <div>
        <label class="block text-sm text-slate-500 mb-1">邮箱</label>
        <input
          v-model="email"
          type="email"
          required
          class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-indigo-400 focus:outline-none text-slate-800"
          placeholder="your@email.com"
        />
      </div>
      <div>
        <label class="block text-sm text-slate-500 mb-1">密码</label>
        <input
          v-model="password"
          type="password"
          required
          minlength="8"
          class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-indigo-400 focus:outline-none text-slate-800"
          placeholder="至少8位"
        />
      </div>

      <p v-if="error" class="text-red-400 text-sm">{{ error }}</p>

      <button
        type="submit"
        :disabled="loading"
        class="w-full py-3 rounded-xl bg-indigo-500 text-white font-medium text-lg disabled:opacity-50"
      >
        {{ loading ? '注册中...' : '注册' }}
      </button>
    </form>

    <p class="text-center text-slate-400 mt-6">
      已有账号？
      <router-link to="/login" class="text-indigo-500 font-medium">立即登录</router-link>
    </p>
  </div>
</template>
