<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { generateReport, getReport } from '@/api/report'

const route = useRoute()
const router = useRouter()
const report = ref<any>(null)
const loading = ref(true)

async function loadReport() {
  const aid = Number(route.params.id)
  try {
    const res = await generateReport(aid)
    report.value = res.data
  } catch {
    // Try getting existing
    try {
      const res = await getReport(aid)
      report.value = res.data
    } catch {
      report.value = null
    }
  }
  loading.value = false
  if (report.value) {
    setTimeout(renderRadar, 100)
  }
}

function renderRadar() {
  const el = document.getElementById('radar-chart')
  if (!el || !report.value) return
  const chart = echarts.init(el)
  const dims = report.value.dimensions
  const labels = Object.values(dims).map((d: any) => d.label)
  const scores = Object.values(dims).map((d: any) => d.score)

  chart.setOption({
    radar: {
      center: ['50%', '50%'],
      radius: '65%',
      indicator: labels.map((label: string) => ({ name: label, max: 100 })),
      axisName: { color: '#64748b', fontSize: 12 },
      splitArea: { areaStyle: { color: ['#fff', '#f8fafc'] } },
    },
    series: [{
      type: 'radar',
      data: [{ value: scores, name: '能力画像', areaStyle: { color: 'rgba(99,102,241,0.15)' } }],
      lineStyle: { color: '#6366f1', width: 2 },
      itemStyle: { color: '#6366f1' },
      symbol: 'circle',
      symbolSize: 5,
    }],
  })
}

onMounted(loadReport)
</script>

<template>
  <div class="min-h-screen bg-slate-50 pb-12">
    <div class="bg-white px-4 py-3 border-b border-slate-100 flex items-center gap-2">
      <button @click="router.push('/')" class="text-slate-400">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
      </button>
      <h1 class="text-lg font-semibold text-slate-800">你的能力画像</h1>
    </div>

    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="animate-spin w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full" />
    </div>

    <template v-if="report">
      <!-- Radar Chart -->
      <div class="bg-white mx-4 mt-4 rounded-2xl p-4 shadow-sm">
        <div id="radar-chart" class="w-full" style="height:320px" />
      </div>

      <!-- Summary -->
      <div class="mx-4 mt-4 bg-white rounded-2xl p-4 shadow-sm">
        <h3 class="font-semibold text-slate-800 mb-2">总体评价</h3>
        <p class="text-sm text-slate-600 leading-relaxed">{{ report.summary }}</p>
      </div>

      <!-- Dimensions -->
      <div class="mx-4 mt-4 space-y-3">
        <div
          v-for="(dim, key) in report.dimensions"
          :key="key"
          class="bg-white rounded-2xl p-4 shadow-sm"
        >
          <div class="flex items-center justify-between mb-2">
            <h3 class="font-semibold text-slate-800">{{ dim.label }}</h3>
            <span class="text-2xl font-bold text-indigo-500">{{ dim.score }}</span>
          </div>
          <div class="h-1.5 bg-slate-100 rounded-full overflow-hidden mb-3">
            <div
              class="h-full bg-indigo-500 rounded-full"
              :style="{ width: `${dim.score}%` }"
            />
          </div>
          <p class="text-sm text-slate-600 leading-relaxed">{{ dim.strengths || dim.description }}</p>
        </div>
      </div>

      <!-- Career Suggestions -->
      <div v-if="report.career_suggestions?.length" class="mx-4 mt-4 bg-white rounded-2xl p-4 shadow-sm">
        <h3 class="font-semibold text-slate-800 mb-3">职业方向推荐</h3>
        <div class="space-y-2">
          <div
            v-for="(s, i) in report.career_suggestions"
            :key="i"
            class="flex items-center justify-between py-2 border-b border-slate-50 last:border-0"
          >
            <div>
              <span class="text-sm font-medium text-slate-700">{{ s.direction }}</span>
              <p class="text-xs text-slate-400 mt-0.5">{{ s.reason }}</p>
            </div>
            <span class="text-sm font-bold text-indigo-500">{{ s.match }}%</span>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
