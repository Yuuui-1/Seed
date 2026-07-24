<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { viewSharedReport } from '@/api/report'

const route = useRoute()
const router = useRouter()
const report = ref<any>(null)
const loading = ref(true)
const error = ref('')
let chart: echarts.ECharts | null = null

const dimensions = computed(() => report.value ? Object.values(report.value.dimensions) as any[] : [])

function renderRadar() {
  const el = document.getElementById('shared-radar')
  if (!el || !report.value) return
  chart?.dispose()
  chart = echarts.init(el)
  chart.setOption({
    radar: {
      radius: '62%',
      splitNumber: 4,
      indicator: dimensions.value.map((item) => ({ name: item.label, max: 100 })),
      axisName: { color: '#59645c', fontSize: 12, fontWeight: 600 },
      axisLine: { lineStyle: { color: 'rgba(23,33,27,.10)' } },
      splitLine: { lineStyle: { color: 'rgba(23,33,27,.10)' } },
      splitArea: { areaStyle: { color: ['rgba(255,255,255,.36)', 'rgba(223,236,228,.18)'] } },
    },
    series: [{
      type: 'radar',
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: { color: '#2f6f4e', width: 2.5 },
      itemStyle: { color: '#2f6f4e' },
      areaStyle: { color: 'rgba(47,111,78,.18)' },
      data: [{ value: dimensions.value.map((item) => item.score) }],
    }],
  })
}

async function loadReport() {
  try {
    const response = await viewSharedReport(route.params.token as string)
    report.value = response.data
    await nextTick()
    renderRadar()
  } catch {
    error.value = '分享链接不存在或已经过期。'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadReport()
  window.addEventListener('resize', renderRadar)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', renderRadar)
  chart?.dispose()
})
</script>

<template>
  <main class="min-h-screen pb-16">
    <header class="border-b border-[var(--seed-border)] bg-[var(--seed-canvas)]/80 backdrop-blur-xl">
      <div class="seed-shell seed-nav">
        <button class="seed-brand border-0 bg-transparent p-0" @click="router.push('/')">
          <span class="seed-mark" aria-hidden="true" />
          <span>Seed</span>
        </button>
        <span class="rounded-full border border-[var(--seed-border)] bg-white/50 px-3 py-1.5 text-xs font-semibold text-[var(--seed-muted)]">公开分享</span>
      </div>
    </header>

    <section v-if="loading" class="seed-shell flex min-h-[70vh] flex-col items-center justify-center">
      <div class="h-9 w-9 animate-spin rounded-full border-2 border-[var(--seed-green-soft)] border-t-[var(--seed-green)]" />
      <p class="mt-4 text-sm text-[var(--seed-muted)]">正在打开分享报告…</p>
    </section>

    <section v-else-if="error" class="seed-shell flex min-h-[70vh] items-center justify-center">
      <div class="seed-card max-w-md p-8 text-center">
        <h1 class="text-2xl font-semibold">链接无法打开</h1>
        <p class="mt-3 text-sm text-[var(--seed-muted)]">{{ error }}</p>
        <button class="seed-button seed-button-primary mt-6" @click="router.push('/')">回到 Seed</button>
      </div>
    </section>

    <section v-else-if="report" class="seed-shell pt-10 sm:pt-16">
      <div class="max-w-3xl">
        <p class="text-xs font-semibold uppercase tracking-[.22em] text-[var(--seed-green)]">Shared Seed Profile</p>
        <h1 class="mt-4 text-4xl font-semibold tracking-[-.055em] sm:text-6xl">{{ report.share_from }} 的<br>六维优势画像。</h1>
        <p class="mt-6 text-base leading-8 text-[var(--seed-muted)]">{{ report.summary }}</p>
      </div>

      <div class="mt-10 grid gap-6 lg:grid-cols-[.9fr_1.1fr]">
        <article class="seed-card p-5 sm:p-7">
          <p class="text-xs font-semibold uppercase tracking-[.18em] text-[var(--seed-muted)]">能力分布</p>
          <div id="shared-radar" class="h-[340px] w-full" />
        </article>
        <div class="grid gap-4 sm:grid-cols-2">
          <article v-for="item in dimensions" :key="item.label" class="seed-card p-5">
            <div class="flex items-start justify-between gap-4">
              <h2 class="font-semibold">{{ item.label }}</h2>
              <span class="text-2xl font-semibold text-[var(--seed-green)]">{{ item.score }}</span>
            </div>
            <p class="mt-4 text-sm leading-6 text-[var(--seed-muted)]">{{ item.strengths || item.description }}</p>
          </article>
        </div>
      </div>

      <div class="mt-12 flex flex-col items-start justify-between gap-6 rounded-[28px] bg-[var(--seed-ink)] p-7 text-white sm:flex-row sm:items-center sm:p-10">
        <div>
          <p class="text-xs font-semibold uppercase tracking-[.2em] text-white/45">Discover yours</p>
          <h2 class="mt-3 text-2xl font-semibold">也想看见自己的优势吗？</h2>
          <p class="mt-2 text-sm text-white/60">10 道自适应问题，约 5 分钟完成。</p>
        </div>
        <button class="seed-button bg-white text-[var(--seed-ink)]" @click="router.push('/assessment')">开始我的测评</button>
      </div>
    </section>
  </main>
</template>
