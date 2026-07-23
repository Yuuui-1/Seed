<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

onMounted(async () => {
  if (auth.accessToken && !auth.user) {
    try { await auth.fetchMe() } catch {}
  }
})
</script>

<template>
  <div class="min-h-screen bg-white flex flex-col">
    <!-- Hero -->
    <div class="flex-1 flex flex-col items-center justify-center px-6 pt-16 pb-8">
      <div class="w-20 h-20 bg-indigo-500 rounded-2xl flex items-center justify-center mb-6 shadow-lg shadow-indigo-200">
        <span class="text-4xl">🌱</span>
      </div>
      <h1 class="text-3xl font-bold text-slate-800 mb-2">Seed</h1>
      <p class="text-slate-400 text-center max-w-xs">
        基于科学量表的 AI 自适应优势测评，发现你的六维能力画像
      </p>

      <button
        @click="router.push('/assessment')"
        class="mt-8 w-full max-w-xs py-3.5 rounded-xl bg-indigo-500 text-white font-semibold text-lg shadow-lg shadow-indigo-200 active:scale-95 transition-transform"
      >
        开始测评
      </button>

      <div v-if="auth.isAuthenticated" class="mt-4 flex gap-4">
        <button @click="router.push('/history')" class="text-slate-400 text-sm">历史报告</button>
        <button @click="auth.logout" class="text-slate-400 text-sm">退出登录</button>
      </div>
      <div v-else class="mt-4">
        <button @click="router.push('/login')" class="text-slate-400">已有账号，登录</button>
      </div>
    </div>

    <!-- Features -->
    <div class="px-6 pb-12 space-y-4">
      <div class="bg-slate-50 rounded-2xl p-4 flex gap-3">
        <span class="text-2xl">📊</span>
        <div>
          <h3 class="font-medium text-slate-800">科学量表题库</h3>
          <p class="text-sm text-slate-400 mt-0.5">基于大五人格、RIASEC、Grit 等经典量表改编</p>
        </div>
      </div>
      <div class="bg-slate-50 rounded-2xl p-4 flex gap-3">
        <span class="text-2xl">🧠</span>
        <div>
          <h3 class="font-medium text-slate-800">AI 自适应选题</h3>
          <p class="text-sm text-slate-400 mt-0.5">Claude Agent SDK 智能选择最有区分度的题目</p>
        </div>
      </div>
      <div class="bg-slate-50 rounded-2xl p-4 flex gap-3">
        <span class="text-2xl">🔒</span>
        <div>
          <h3 class="font-medium text-slate-800">隐私安全</h3>
          <p class="text-sm text-slate-400 mt-0.5">你的测评数据加密存储，可随时删除</p>
        </div>
      </div>
    </div>
  </div>
</template>
