<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()
const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(email.value, password.value)
    router.push('/')
  } catch (e: any) {
    error.value = e.response?.data?.msg || '登录失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex flex-col px-6 pt-20">
    <div class="mb-10">
      <h1 class="text-2xl font-bold text-slate-800">欢迎回来</h1>
      <p class="text-slate-400 mt-1">登录查看你的优势报告</p>
    </div>

    <form @submit.prevent="handleLogin" class="space-y-4">
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
          class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-indigo-400 focus:outline-none text-slate-800"
          placeholder="8-32位密码"
        />
      </div>

      <p v-if="error" class="text-red-400 text-sm">{{ error }}</p>

      <button
        type="submit"
        :disabled="loading"
        class="w-full py-3 rounded-xl bg-indigo-500 text-white font-medium text-lg disabled:opacity-50"
      >
        {{ loading ? '登录中...' : '登录' }}
      </button>
    </form>

    <p class="text-center text-slate-400 mt-6">
      还没有账号？
      <router-link to="/register" class="text-indigo-500 font-medium">立即注册</router-link>
    </p>
  </div>
</template>
