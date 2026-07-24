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
  } finally { loading.value = false }
}
</script>

<template>
  <div class="min-h-screen flex flex-col px-6 pt-20" style="background: #f8f6f0">
    <h1 class="display-font text-3xl font-semibold mb-1" style="color: #5a4220">欢迎回来</h1>
    <p class="text-sm mb-10" style="color: #9b8a70">登录查看你的优势报告</p>

    <form @submit.prevent="handleLogin" class="space-y-4">
      <input v-model="email" type="email" placeholder="your@email.com" required
        class="w-full px-4 py-3.5 rounded-xl text-base outline-none transition-all"
        style="background: #fff; border: 2px solid #e2d8c0; color: #5a4220"
        :style="error ? 'border-color: #d88' : ''"
        @focus="$event.target.style.borderColor = '#b8945a'"
        @blur="$event.target.style.borderColor = '#e2d8c0'"
      />
      <input v-model="password" type="password" placeholder="密码" required
        class="w-full px-4 py-3.5 rounded-xl text-base outline-none transition-all"
        style="background: #fff; border: 2px solid #e2d8c0; color: #5a4220"
        @focus="$event.target.style.borderColor = '#b8945a'"
        @blur="$event.target.style.borderColor = '#e2d8c0'"
      />
      <p v-if="error" class="text-sm" style="color: #d88">{{ error }}</p>
      <button type="submit" :disabled="loading"
        class="w-full py-3.5 rounded-xl text-white font-semibold text-lg transition-all active:scale-95"
        style="background: linear-gradient(135deg, #b8945a, #a07a40)"
        :style="loading ? 'opacity: 0.7' : ''"
      >{{ loading ? '登录中...' : '登录' }}</button>
    </form>
    <p class="text-center text-sm mt-6" style="color: #9b8a70">
      还没有账号？<router-link to="/register" style="color: #8ba888" class="font-medium">立即注册</router-link>
    </p>
  </div>
</template>
