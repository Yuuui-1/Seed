<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { safeRedirect } from '@/router/guards'

const router = useRouter()
const route = useRoute()
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
    router.push(safeRedirect(route.query.redirect, '/'))
  } catch (e: any) {
    error.value = e.response?.data?.msg || '登录失败，请检查邮箱和密码。'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="seed-shell grid min-h-screen items-center gap-10 py-8 lg:grid-cols-2">
    <section class="hidden max-w-xl lg:block">
      <button class="seed-brand border-0 bg-transparent p-0" @click="router.push('/')">
        <span class="seed-mark" aria-hidden="true" />
        <span>Seed</span>
      </button>
      <p class="mt-16 text-xs font-semibold uppercase tracking-[.22em] text-[var(--seed-gold)]">Welcome back</p>
      <h1 class="mt-5 text-6xl font-semibold leading-[1.02] tracking-[-.06em]">继续认识<br>真实的自己。</h1>
      <p class="mt-7 max-w-md text-lg leading-8 text-[var(--seed-muted)]">你的每次测评都会被安静保存，随时回来查看成长轨迹。</p>
    </section>

    <section class="seed-card mx-auto w-full max-w-[480px] p-6 sm:p-9">
      <button class="seed-brand mb-10 border-0 bg-transparent p-0 lg:hidden" @click="router.push('/')">
        <span class="seed-mark" aria-hidden="true" />
        <span>Seed</span>
      </button>
      <p class="text-xs font-semibold uppercase tracking-[.2em] text-[var(--seed-green)]">登录账户</p>
      <h1 class="mt-3 text-3xl font-semibold tracking-[-.04em]">欢迎回来</h1>
      <p class="mt-2 text-sm leading-6 text-[var(--seed-muted)]">登录后继续测评，或查看你的历史优势报告。</p>

      <form class="mt-8 space-y-5" @submit.prevent="handleLogin">
        <label class="block">
          <span class="mb-2 block text-sm font-medium">邮箱</span>
          <input v-model="email" class="seed-input" type="email" autocomplete="email" required placeholder="name@example.com">
        </label>
        <label class="block">
          <span class="mb-2 block text-sm font-medium">密码</span>
          <input v-model="password" class="seed-input" type="password" autocomplete="current-password" required placeholder="输入你的密码">
        </label>
        <p v-if="error" role="alert" class="rounded-xl border border-red-100 bg-red-50 px-4 py-3 text-sm text-red-700">{{ error }}</p>
        <button class="seed-button seed-button-primary w-full" type="submit" :disabled="loading">
          {{ loading ? '正在登录…' : '登录并继续' }}
        </button>
      </form>

      <p class="mt-7 text-center text-sm text-[var(--seed-muted)]">
        还没有账户？
        <router-link :to="{ name: 'register', query: route.query }" class="font-semibold text-[var(--seed-green)]">免费创建</router-link>
      </p>
    </section>
  </main>
</template>
