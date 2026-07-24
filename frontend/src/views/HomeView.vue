<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

onMounted(async () => {
  if (auth.accessToken && !auth.user) {
    try {
      await auth.fetchMe()
    } catch {
      auth.logout()
    }
  }
})

function startAssessment() {
  router.push('/assessment')
}

function logout() {
  auth.logout()
}
</script>

<template>
  <main class="min-h-screen overflow-hidden">
    <nav class="seed-shell seed-nav">
      <button class="seed-brand border-0 bg-transparent p-0" @click="router.push('/')" aria-label="Seed 首页">
        <span class="seed-mark" aria-hidden="true" />
        <span>Seed</span>
      </button>
      <div class="flex items-center gap-2">
        <template v-if="auth.isAuthenticated">
          <button class="seed-button seed-button-secondary !min-h-10 !px-4 text-sm" @click="router.push('/history')">
            历史报告
          </button>
          <button class="min-h-10 rounded-xl px-3 text-sm font-medium text-[var(--seed-muted)]" @click="logout">
            退出
          </button>
        </template>
        <template v-else>
          <button class="min-h-10 rounded-xl px-3 text-sm font-semibold text-[var(--seed-ink)]" @click="router.push('/login')">
            登录
          </button>
          <button class="seed-button seed-button-primary !min-h-10 !px-4 text-sm" @click="router.push('/register')">
            创建账户
          </button>
        </template>
      </div>
    </nav>

    <section class="seed-shell grid items-center gap-12 pb-20 pt-14 md:grid-cols-[1.04fr_.96fr] md:pb-28 md:pt-24">
      <div class="max-w-2xl">
        <div class="mb-6 inline-flex items-center gap-2 rounded-full border border-[var(--seed-border)] bg-white/55 px-3 py-1.5 text-xs font-semibold text-[var(--seed-green)]">
          <span class="h-1.5 w-1.5 rounded-full bg-[var(--seed-green)]" />
          科学量表 × 自适应选题
        </div>
        <h1 class="text-[clamp(3rem,8vw,6.7rem)] font-semibold leading-[.92] tracking-[-.075em] text-[var(--seed-ink)]">
          看见你的<br>
          <span class="text-[var(--seed-green)]">成长优势。</span>
        </h1>
        <p class="mt-7 max-w-xl text-lg leading-8 text-[var(--seed-muted)] md:text-xl">
          一次安静、清晰的 AI 优势测评。基于经典心理量表，自适应理解你的思维、创造、执行与内在驱动力。
        </p>
        <div class="mt-9 flex flex-col gap-3 sm:flex-row">
          <button class="seed-button seed-button-primary px-7" @click="startAssessment">
            开始 10 题测评
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m9 18 6-6-6-6" />
            </svg>
          </button>
          <button class="seed-button seed-button-secondary px-7" @click="router.push(auth.isAuthenticated ? '/history' : '/login')">
            {{ auth.isAuthenticated ? '查看我的报告' : '已有账户，登录' }}
          </button>
        </div>
        <p class="mt-5 text-xs tracking-wide text-[var(--seed-muted)]">约 5 分钟 · 结果仅你可见 · 随时重新测评</p>
      </div>

      <div class="relative mx-auto w-full max-w-[520px]">
        <div class="absolute -inset-10 rounded-full bg-[var(--seed-green-soft)]/55 blur-3xl" />
        <div class="seed-card relative overflow-hidden p-5 sm:p-7">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-xs font-semibold uppercase tracking-[.18em] text-[var(--seed-muted)]">优势画像预览</p>
              <p class="mt-1 text-xl font-semibold tracking-tight">你的六维成长地图</p>
            </div>
            <span class="rounded-full bg-[var(--seed-green-soft)] px-3 py-1 text-xs font-semibold text-[var(--seed-green)]">AI 分析</span>
          </div>
          <div class="relative mx-auto mt-7 aspect-square max-w-[360px]">
            <div class="absolute inset-[7%] rounded-full border border-[var(--seed-border)]" />
            <div class="absolute inset-[20%] rounded-full border border-[var(--seed-border)]" />
            <div class="absolute inset-[33%] rounded-full border border-[var(--seed-border)]" />
            <svg class="absolute inset-0 h-full w-full" viewBox="0 0 100 100" aria-hidden="true">
              <polygon points="50,10 84,30 82,67 50,90 18,68 16,30" fill="rgba(47,111,78,.12)" stroke="#2f6f4e" stroke-width="1.2" />
              <circle v-for="(point, i) in [[50,10],[84,30],[82,67],[50,90],[18,68],[16,30]]" :key="i" :cx="point[0]" :cy="point[1]" r="1.8" fill="#2f6f4e" />
            </svg>
            <span class="absolute left-1/2 top-0 -translate-x-1/2 text-xs font-medium">思维</span>
            <span class="absolute right-0 top-[27%] text-xs font-medium">创造</span>
            <span class="absolute bottom-[22%] right-0 text-xs font-medium">执行</span>
            <span class="absolute bottom-0 left-1/2 -translate-x-1/2 text-xs font-medium">社交</span>
            <span class="absolute bottom-[22%] left-0 text-xs font-medium">情绪</span>
            <span class="absolute left-0 top-[27%] text-xs font-medium">驱动</span>
          </div>
          <div class="mt-4 grid grid-cols-3 gap-2">
            <div v-for="item in [['科学题库','36 题'],['自适应','10 轮'],['能力维度','6 项']]" :key="item[0]" class="rounded-2xl border border-[var(--seed-border)] bg-white/55 p-3">
              <p class="text-[11px] text-[var(--seed-muted)]">{{ item[0] }}</p>
              <p class="mt-1 text-base font-semibold">{{ item[1] }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="border-y border-[var(--seed-border)] bg-white/35">
      <div class="seed-shell grid gap-8 py-14 md:grid-cols-3 md:py-20">
        <article v-for="feature in [
          ['01','可信的起点','题目改编自 Big Five、RIASEC、Grit、SDT 与 NFC 等经典量表。'],
          ['02','更懂你的路径','AI 不随意出题，只从验证题库中选择当下最有区分度的问题。'],
          ['03','有依据的结果','每个维度都回到你的真实回答，形成清晰、可理解的证据链。']
        ]" :key="feature[0]" class="max-w-sm">
          <span class="text-xs font-semibold tracking-[.2em] text-[var(--seed-gold)]">{{ feature[0] }}</span>
          <h2 class="mt-4 text-xl font-semibold tracking-tight">{{ feature[1] }}</h2>
          <p class="mt-3 text-sm leading-7 text-[var(--seed-muted)]">{{ feature[2] }}</p>
        </article>
      </div>
    </section>

    <footer class="seed-shell flex flex-col gap-3 py-8 text-xs text-[var(--seed-muted)] sm:flex-row sm:items-center sm:justify-between">
      <span>Seed · 发现适合你的生长方向</span>
      <span>科学测评不是标签，而是一次更清晰的自我观察。</span>
    </footer>
  </main>
</template>
