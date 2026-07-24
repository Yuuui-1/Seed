<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { getReport, shareReport } from '@/api/report'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const report = ref<any>(null)
const loading = ref(true)
const error = ref('')
const sharing = ref(false)
const shareMessage = ref('')
let chart: echarts.ECharts | null = null

const dimensions = computed(() => {
  if (!report.value?.dimensions) return []
  const dims = report.value.dimensions
  return typeof dims === 'object' ? Object.values(dims) as any[] : []
})
const topDimensions = computed(() => [...dimensions.value].sort((a, b) => b.score - a.score).slice(0, 2))

function renderRadar() {
  const el = document.getElementById('radar-chart')
  if (!el || !report.value) return
  if (!dimensions.value.length) return
  chart?.dispose()
  el.style.width = el.clientWidth + 'px'
  el.style.height = '350px'
  chart = echarts.init(el)
  chart.setOption({
    radar: {
      center: ['50%', '52%'],
      radius: '64%',
      splitNumber: 4,
      indicator: dimensions.value.map((item) => ({ name: item.label, max: 100 })),
      axisName: { color: '#59645c', fontSize: 12, fontWeight: 600 },
      axisLine: { lineStyle: { color: 'rgba(23,33,27,.10)' } },
      splitLine: { lineStyle: { color: 'rgba(23,33,27,.10)' } },
      splitArea: { areaStyle: { color: ['rgba(255,255,255,.34)', 'rgba(223,236,228,.18)'] } },
    },
    series: [{
      type: 'radar',
      symbol: 'circle',
      symbolSize: 7,
      lineStyle: { color: '#2f6f4e', width: 2.5 },
      itemStyle: { color: '#2f6f4e', borderColor: '#fff', borderWidth: 2 },
      areaStyle: { color: 'rgba(47,111,78,.18)' },
      data: [{ value: dimensions.value.map((item) => item.score) }],
    }],
  })
}

async function loadReport() {
  loading.value = true
  error.value = ''
  try {
    const response = await getReport(Number(route.params.id))
    report.value = response.data
    await nextTick()
    setTimeout(renderRadar, 300)
  } catch {
    report.value = null
    error.value = '这份报告暂时无法加载，可能已失效或不属于当前账户。'
  } finally {
    loading.value = false
  }
}

async function createShareLink() {
  if (!report.value || sharing.value) return
  sharing.value = true
  shareMessage.value = ''
  try {
    const response = await shareReport(report.value.id)
    const url = response.data.share_url
    await navigator.clipboard.writeText(url)
    shareMessage.value = '分享链接已复制'
  } catch {
    shareMessage.value = '暂时无法创建分享链接'
  } finally {
    sharing.value = false
  }
}

onMounted(() => {
  loadReport()
  window.addEventListener('resize', () => setTimeout(renderRadar, 200))
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
        <div class="flex items-center gap-2">
          <button class="seed-button seed-button-secondary !min-h-10 !px-4 text-sm" @click="router.push('/history')">历史报告</button>
          <button v-if="report" class="seed-button seed-button-primary !min-h-10 !px-4 text-sm" :disabled="sharing" @click="createShareLink">
            {{ sharing ? '生成中…' : '分享报告' }}
          </button>
        </div>
      </div>
    </header>

    <section v-if="loading" class="seed-shell flex min-h-[70vh] flex-col items-center justify-center">
      <div class="h-9 w-9 animate-spin rounded-full border-2 border-[var(--seed-green-soft)] border-t-[var(--seed-green)]" />
      <p class="mt-4 text-sm text-[var(--seed-muted)]">正在读取你的优势画像…</p>
    </section>

    <section v-else-if="error" class="seed-shell flex min-h-[70vh] items-center justify-center">
      <div class="seed-card max-w-lg p-8 text-center">
        <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-amber-50 text-amber-700">!</div>
        <h1 class="mt-5 text-2xl font-semibold">报告没有如期出现</h1>
        <p class="mt-3 text-sm leading-7 text-[var(--seed-muted)]">{{ error }}</p>
        <div class="mt-6 flex justify-center gap-3">
          <button class="seed-button seed-button-primary" @click="loadReport">重新加载</button>
          <button class="seed-button seed-button-secondary" @click="router.push('/history')">返回历史</button>
        </div>
      </div>
    </section>

    <template v-else-if="report">
      <section class="seed-shell pt-10 sm:pt-16">
        <div class="flex flex-col gap-7 border-b border-[var(--seed-border)] pb-10 md:flex-row md:items-end md:justify-between">
          <div class="max-w-3xl">
            <p class="text-xs font-semibold uppercase tracking-[.22em] text-[var(--seed-green)]">Your Seed Profile</p>
            <h1 class="mt-4 text-4xl font-semibold leading-tight tracking-[-.055em] sm:text-6xl">你的优势，正在形成<br>独特的生长方式。</h1>
            <p class="mt-5 max-w-2xl text-base leading-8 text-[var(--seed-muted)]">{{ report.summary }}</p>
          </div>
          <div class="shrink-0 rounded-2xl border border-[var(--seed-border)] bg-white/55 px-5 py-4">
            <p class="text-xs text-[var(--seed-muted)]">报告生成于</p>
            <p class="mt-1 font-semibold">{{ new Date(report.created_at).toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' }) }}</p>
          </div>
        </div>

        <div class="mt-8 grid gap-6 lg:grid-cols-[.92fr_1.08fr]">
          <article class="seed-card p-5 sm:p-7">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-xs font-semibold uppercase tracking-[.18em] text-[var(--seed-muted)]">六维能力图谱</p>
                <h2 class="mt-2 text-xl font-semibold">整体优势分布</h2>
              </div>
              <span class="rounded-full bg-[var(--seed-green-soft)] px-3 py-1 text-xs font-semibold text-[var(--seed-green)]">科学量表</span>
            </div>
            <div id="radar-chart" class="mt-3 h-[350px] w-full" />
          </article>

          <article class="seed-card p-6 sm:p-8">
            <p class="text-xs font-semibold uppercase tracking-[.18em] text-[var(--seed-gold)]">核心优势</p>
            <h2 class="mt-3 text-2xl font-semibold tracking-tight">你最自然的两种力量</h2>
            <div class="mt-7 space-y-7">
              <div v-for="(item, index) in topDimensions" :key="item.label">
                <div class="flex items-end justify-between gap-4">
                  <div class="flex items-center gap-3">
                    <span class="text-xs font-semibold text-[var(--seed-muted)]">0{{ index + 1 }}</span>
                    <h3 class="text-lg font-semibold">{{ item.label }}</h3>
                  </div>
                  <span class="text-3xl font-semibold tracking-[-.05em] text-[var(--seed-green)]">{{ item.score }}</span>
                </div>
                <p class="mt-3 text-sm leading-7 text-[var(--seed-muted)]">{{ item.strengths || item.description }}</p>
                <div class="mt-4 h-1.5 rounded-full bg-black/5">
                  <div class="h-full rounded-full bg-[var(--seed-green)]" :style="{ width: `${item.score}%` }" />
                </div>
              </div>
            </div>
          </article>
        </div>

        <section class="mt-14">
          <div class="max-w-xl">
            <p class="text-xs font-semibold uppercase tracking-[.18em] text-[var(--seed-green)]">Dimension insights</p>
            <h2 class="mt-3 text-3xl font-semibold tracking-[-.045em]">六个维度，六种成长线索</h2>
          </div>
          <div class="mt-7 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <article v-for="item in dimensions" :key="item.label" class="seed-card flex min-h-[250px] flex-col p-6">
              <div class="flex items-start justify-between gap-4">
                <h3 class="text-lg font-semibold">{{ item.label }}</h3>
                <span class="text-2xl font-semibold text-[var(--seed-green)]">{{ item.score }}</span>
              </div>
              <p class="mt-5 flex-1 text-sm leading-7 text-[var(--seed-muted)]">{{ item.description || item.strengths }}</p>
              <div v-if="item.evidence?.length" class="mt-5 rounded-xl bg-[var(--seed-green-soft)]/55 px-4 py-3 text-xs leading-5 text-[var(--seed-green-deep)]">
                {{ item.evidence[0] }}
              </div>
            </article>
          </div>
        </section>

        <section v-if="report.career_suggestions?.length" class="mt-14 seed-card overflow-hidden">
          <div class="border-b border-[var(--seed-border)] p-6 sm:p-8">
            <p class="text-xs font-semibold uppercase tracking-[.18em] text-[var(--seed-gold)]">Possible directions</p>
            <h2 class="mt-3 text-3xl font-semibold tracking-[-.045em]">适合你的探索方向</h2>
            <p class="mt-3 text-sm text-[var(--seed-muted)]">建议不是答案，而是值得优先尝试的方向。</p>
          </div>
          <div class="divide-y divide-[var(--seed-border)]">
            <div v-for="(suggestion, index) in report.career_suggestions" :key="index" class="grid gap-4 p-6 sm:grid-cols-[52px_1fr_auto] sm:items-center sm:p-8">
              <span class="flex h-11 w-11 items-center justify-center rounded-2xl bg-[var(--seed-green-soft)] text-sm font-semibold text-[var(--seed-green)]">0{{ Number(index) + 1 }}</span>
              <div>
                <h3 class="font-semibold">{{ suggestion.direction }}</h3>
                <p class="mt-1 text-sm leading-6 text-[var(--seed-muted)]">{{ suggestion.reason }}</p>
              </div>
              <span class="text-sm font-semibold text-[var(--seed-green)]">{{ suggestion.match }}% 匹配</span>
            </div>
          </div>
        </section>

        <section class="mt-14 flex flex-col items-start justify-between gap-6 rounded-[28px] bg-[var(--seed-ink)] p-7 text-white sm:flex-row sm:items-center sm:p-10">
          <div>
            <p class="text-xs font-semibold uppercase tracking-[.2em] text-white/50">Keep growing</p>
            <h2 class="mt-3 text-2xl font-semibold tracking-tight">把这份认识，带到下一次行动里。</h2>
            <p v-if="shareMessage" class="mt-2 text-sm text-white/65">{{ shareMessage }}</p>
          </div>
          <div class="flex flex-wrap gap-3">
            <button class="seed-button bg-white text-[var(--seed-ink)]" @click="createShareLink">复制分享链接</button>
            <button class="seed-button border border-white/20 bg-white/8 text-white" @click="router.push('/assessment')">再次测评</button>
          </div>
        </section>
      </section>
    </template>
  </main>
</template>
