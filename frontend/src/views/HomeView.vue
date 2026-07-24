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
  <div class="min-h-screen flex flex-col items-center justify-center px-8 text-center relative overflow-hidden"
    style="background: linear-gradient(160deg, #f8f6f0 0%, #f0ece0 40%, #e8e0cc 100%)"
  >
    <!-- Subtle organic shape -->
    <div class="absolute top-0 right-0 w-64 h-64 rounded-full opacity-10"
      style="background: radial-gradient(circle, #c4a97a 0%, transparent 70%); transform: translate(30%, -30%)"
    />

    <div class="relative z-10 flex flex-col items-center">
      <!-- Logo -->
      <div class="w-24 h-24 rounded-full flex items-center justify-center mb-8"
        style="background: linear-gradient(135deg, #b8945a, #8ba888); box-shadow: 0 8px 32px rgba(139,168,136,0.25)"
      >
        <span class="text-4xl">🌱</span>
      </div>

      <h1 class="display-font text-5xl font-semibold mb-2" style="color: #5a4220">Seed</h1>
      <p class="text-lg mb-2" style="color: #7d5e30">发现你的天赋优势</p>
      <p class="text-sm max-w-xs leading-relaxed" style="color: #9b8a70">
        基于大五人格·RIASEC·Grit 科学量表<br/>AI 自适应选题，10 道题发现六维能力画像
      </p>

      <!-- CTA -->
      <button
        @click="router.push('/assessment')"
        class="mt-10 px-10 py-4 rounded-2xl text-white font-semibold text-lg pulse-glow transition-all active:scale-95"
        style="background: linear-gradient(135deg, #b8945a, #a07a40); box-shadow: 0 4px 20px rgba(184,148,90,0.3)"
      >
        开始测评
      </button>

      <div v-if="auth.isAuthenticated" class="mt-6 flex gap-6">
        <button @click="router.push('/history')" class="text-sm" style="color: #8ba888">历史报告</button>
        <button @click="auth.logout" class="text-sm" style="color: #9b8a70">退出</button>
      </div>
      <div v-else class="mt-6">
        <button @click="router.push('/login')" class="text-sm" style="color: #9b8a70">已有账号，登录</button>
      </div>
    </div>
  </div>
</template>
