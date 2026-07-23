<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { viewSharedReport } from '@/api/report'

const route = useRoute()
const router = useRouter()
const report = ref<any>(null)
const loading = ref(true)

async function loadReport() {
  try {
    const res = await viewSharedReport(route.params.token as string)
    report.value = res.data
  } catch {}
  loading.value = false
  if (report.value) {
    setTimeout(renderRadar, 100)
  }
}

function renderRadar() {
  const el = document.getElementById('shared-radar')
  if (!el || !report.value) return
  const chart = echarts.init(el)
  const dims = report.value.dimensions
  const labels = Object.values(dims).map((d: any) => d.label)
  const scores = Object.values(dims).map((d: any) => d.score)

  chart.setOption({
    radar: {
      center: ['50%', '50%'],
      radius: '60%',
      indicator: labels.map((label: string) => ({ name: label, max: 100 })),
      axisName: { color: '#64748b', fontSize: 11 },
    },
    series: [{
      type: 'radar',
      data: [{ value: scores, name: '能力画像', areaStyle: { color: 'rgba(99,102,241,0.12)' } }],
      lineStyle: { color: '#6366f1', width: 2 },
      itemStyle: { color: '#6366f1' },
    }],
  })
}

onMounted(loadReport)
</script>

<template>
  <div class="min-h-screen bg-slate-50 pb-20">
    <div class="bg-white px-4 py-3 border-b border-slate-100">
      <h1 class="text-lg font-semibold text-slate-800 text-center">
        {{ report?.share_from || '...' }} 的能力画像
      </h1>
    </div>

    <div v-if="loading" class="flex justify-center py-20">
      <div class="animate-spin w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full" />
    </div>

    <template v-if="report">
      <div class="bg-white mx-4 mt-4 rounded-2xl p-4 shadow-sm">
        <div id="shared-radar" class="w-full" style="height:280px" />
      </div>

      <div class="mx-4 mt-4 bg-white rounded-2xl p-4 shadow-sm">
        <p class="text-sm text-slate-600 leading-relaxed">{{ report.summary }}</p>
      </div>

      <div class="text-center mt-8">
        <p class="text-slate-400 text-sm mb-4">想了解你的优势吗？</p>
        <button
          @click="router.push('/')"
          class="px-8 py-3 rounded-xl bg-indigo-500 text-white font-medium text-lg"
        >
          我也要测评
        </button>
      </div>
    </template>
  </div>
</template>
