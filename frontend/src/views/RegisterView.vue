<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { bindAssessment } from '@/api/assessment'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const email = ref('')
const password = ref('')
const nickname = ref('')
const error = ref('')
const loading = ref(false)

async function handleRegister() {
  error.value = ''
  if (password.value.length < 8) { error.value = '密码至少8位'; return }
  loading.value = true
  try {
    await auth.register(email.value, password.value, nickname.value)
    const redirect = route.query.redirect as string
    if (redirect) {
      const match = redirect.match(/\/assessment\/(\d+)/)
      if (match) {
        try { await bindAssessment(Number(match[1])) } catch {}
        router.push(redirect)
        return
      }
    }
    router.push('/')
  } catch (e: any) {
    error.value = e.response?.data?.msg || '注册失败'
  } finally { loading.value = false }
}
</script>

<template>
  <div class="min-h-screen flex flex-col px-6 pt-16" style="background: #f8f6f0">
    <h1 class="display-font text-3xl font-semibold mb-1" style="color: #5a4220">创建账号</h1>
    <p class="text-sm mb-8" style="color: #9b8a70">开启你的优势探索之旅</p>

    <form @submit.prevent="handleRegister" class="space-y-4">
      <input v-model="nickname" type="text" placeholder="你的昵称" required minlength="2" maxlength="20"
        class="w-full px-4 py-3.5 rounded-xl text-base outline-none transition-all"
        style="background: #fff; border: 2px solid #e2d8c0; color: #5a4220"
        @focus="$event.target.style.borderColor = '#b8945a'"
        @blur="$event.target.style.borderColor = '#e2d8c0'"
      />
      <input v-model="email" type="email" placeholder="your@email.com" required
        class="w-full px-4 py-3.5 rounded-xl text-base outline-none transition-all"
        style="background: #fff; border: 2px solid #e2d8c0; color: #5a4220"
        @focus="$event.target.style.borderColor = '#b8945a'"
        @blur="$event.target.style.borderColor = '#e2d8c0'"
      />
      <input v-model="password" type="password" placeholder="至少8位密码" required minlength="8"
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
      >{{ loading ? '注册中...' : '注册' }}</button>
    </form>
    <p class="text-center text-sm mt-6" style="color: #9b8a70">
      已有账号？<router-link to="/login" style="color: #8ba888" class="font-medium">立即登录</router-link>
    </p>
  </div>
</template>
