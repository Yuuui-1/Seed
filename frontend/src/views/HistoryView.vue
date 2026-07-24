<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { listReports } from '@/api/report'

const router = useRouter()
const reports = ref<any[]>([])
const loading = ref(true)
const error = ref('')

function topDimensions(dimensions: Record<string, any>) {
  return Object.values(dimensions).sort((a: any, b: any) => b.score - a.score).slice(0, 3)
}

async function loadReports() {
  loading.value = true
  error.value = ''
  try {
    const response = await listReports()
    reports.value = response.data.items || []
  } catch {
    error.value = '历史报告加载失败，请稍后重试。'
  } finally {
    loading.value = false
  }
}

onMounted(loadReports)
</script>

<template>
  <main class="min-h-screen pb-16">
    <header class="border-b border-[var(--seed-border)] bg-[var(--seed-canvas)]/80 backdrop-blur-xl">
      <div class="seed-shell seed-nav">
        <button class="seed-brand border-0 bg-transparent p-0" @click="router.push('/')">
          <span class="seed-mark" aria-hidden="true" />
          <span>Seed</span>
        </button>
        <button class="seed-button seed-button-primary !min-h-10 !px-4 text-sm" @click="router.push('/assessment')">开始新测评</button>
      </div>
    </header>

    <section class="seed-shell pt-10 sm:pt-16">
      <div class="max-w-2xl">
        <p class="text-xs font-semibold uppercase tracking-[.22em] text-[var(--seed-green)]">Your growth archive</p>
        <h1 class="mt-4 text-4xl font-semibold tracking-[-.055em] sm:text-6xl">每一次回答，<br>都是成长的切片。</h1>
        <p class="mt-5 text-base leading-8 text-[var(--seed-muted)]">回看不同阶段的优势画像，观察什么始终稳定，什么正在发生变化。</p>
      </div>

      <div v-if="loading" class="mt-14 grid gap-4 md:grid-cols-2">
        <div v-for="i in 4" :key="i" class="seed-card h-[230px] animate-pulse bg-white/45" />
      </div>

      <div v-else-if="error" class="seed-card mt-14 max-w-xl p-7">
        <p class="text-sm text-red-700">{{ error }}</p>
        <button class="seed-button seed-button-secondary mt-5" @click="loadReports">重新加载</button>
      </div>

      <div v-else-if="reports.length === 0" class="seed-card mt-14 flex min-h-[360px] flex-col items-center justify-center p-8 text-center">
        <span class="seed-mark !h-14 !w-14 !rounded-2xl" />
        <h2 class="mt-6 text-2xl font-semibold">还没有第一份报告</h2>
        <p class="mt-3 max-w-sm text-sm leading-7 text-[var(--seed-muted)]">完成 10 道自适应问题，建立你的六维优势画像。</p>
        <button class="seed-button seed-button-primary mt-7" @click="router.push('/assessment')">开始测评</button>
      </div>

      <div v-else class="mt-14 grid gap-5 md:grid-cols-2">
        <article
          v-for="(item, index) in reports"
          :key="item.id"
          class="seed-card group cursor-pointer overflow-hidden p-6 transition hover:-translate-y-1 hover:shadow-[var(--seed-shadow)] sm:p-7"
          tabindex="0"
          @click="router.push(`/report/${item.id}`)"
          @keydown.enter="router.push(`/report/${item.id}`)"
        >
          <div class="flex items-start justify-between gap-5">
            <div>
              <p class="text-xs font-semibold uppercase tracking-[.18em] text-[var(--seed-gold)]">Profile {{ String(reports.length - index).padStart(2, '0') }}</p>
              <h2 class="mt-3 text-xl font-semibold">优势画像报告</h2>
              <p class="mt-1 text-sm text-[var(--seed-muted)]">{{ new Date(item.created_at).toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' }) }}</p>
            </div>
            <span class="flex h-10 w-10 items-center justify-center rounded-full border border-[var(--seed-border)] bg-white/55 transition group-hover:bg-[var(--seed-green)] group-hover:text-white">
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m9 18 6-6-6-6" /></svg>
            </span>
          </div>
          <div class="mt-8 border-t border-[var(--seed-border)] pt-5">
            <p class="text-xs font-medium text-[var(--seed-muted)]">当期突出优势</p>
            <div class="mt-3 flex flex-wrap gap-2">
              <span v-for="dim in topDimensions(item.dimensions)" :key="dim.label" class="rounded-full bg-[var(--seed-green-soft)] px-3 py-1.5 text-xs font-semibold text-[var(--seed-green-deep)]">
                {{ dim.label }} · {{ dim.score }}
              </span>
            </div>
          </div>
        </article>
      </div>
    </section>
  </main>
</template>
