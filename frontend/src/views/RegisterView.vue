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
const nickname = ref('')
const error = ref('')
const loading = ref(false)

async function handleRegister() {
  error.value = ''
  if (password.value.length < 8) {
    error.value = '密码至少需要 8 位。'
    return
  }
  loading.value = true
  try {
    await auth.register(email.value, password.value, nickname.value)
    router.push(safeRedirect(route.query.redirect, '/'))
  } catch (e: any) {
    error.value = e.response?.data?.msg || '注册失败，请稍后重试。'
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
      <p class="mt-16 text-xs font-semibold uppercase tracking-[.22em] text-[var(--seed-gold)]">Begin with curiosity</p>
      <h1 class="mt-5 text-6xl font-semibold leading-[1.02] tracking-[-.06em]">从一颗种子，<br>看见更多可能。</h1>
      <p class="mt-7 max-w-md text-lg leading-8 text-[var(--seed-muted)]">用五分钟建立你的第一份六维优势画像，结果只属于你。</p>
    </section>

    <section class="seed-card mx-auto w-full max-w-[480px] p-6 sm:p-9">
      <button class="seed-brand mb-8 border-0 bg-transparent p-0 lg:hidden" @click="router.push('/')">
        <span class="seed-mark" aria-hidden="true" />
        <span>Seed</span>
      </button>
      <p class="text-xs font-semibold uppercase tracking-[.2em] text-[var(--seed-green)]">创建账户</p>
      <h1 class="mt-3 text-3xl font-semibold tracking-[-.04em]">开始你的优势探索</h1>
      <p class="mt-2 text-sm leading-6 text-[var(--seed-muted)]">免费注册，测评和报告都会安全地保存在你的账户中。</p>

      <form class="mt-7 space-y-4" @submit.prevent="handleRegister">
        <label class="block">
          <span class="mb-2 block text-sm font-medium">怎么称呼你</span>
          <input v-model="nickname" class="seed-input" type="text" autocomplete="nickname" minlength="2" maxlength="20" required placeholder="你的昵称">
        </label>
        <label class="block">
          <span class="mb-2 block text-sm font-medium">邮箱</span>
          <input v-model="email" class="seed-input" type="email" autocomplete="email" required placeholder="name@example.com">
        </label>
        <label class="block">
          <span class="mb-2 block text-sm font-medium">密码</span>
          <input v-model="password" class="seed-input" type="password" autocomplete="new-password" minlength="8" required placeholder="至少 8 位">
        </label>
        <p v-if="error" role="alert" class="rounded-xl border border-red-100 bg-red-50 px-4 py-3 text-sm text-red-700">{{ error }}</p>
        <button class="seed-button seed-button-primary w-full" type="submit" :disabled="loading">
          {{ loading ? '正在创建…' : '创建账户并开始' }}
        </button>
      </form>

      <p class="mt-6 text-center text-sm text-[var(--seed-muted)]">
        已有账户？
        <router-link :to="{ name: 'login', query: route.query }" class="font-semibold text-[var(--seed-green)]">直接登录</router-link>
      </p>
    </section>
  </main>
</template>
