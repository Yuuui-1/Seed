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
  if (report.value) setTimeout(renderRadar, 200)
}

function renderRadar() {
  const el = document.getElementById('shared-radar')
  if (!el || !report.value) return
  const chart = echarts.init(el)
  const dims = report.value.dimensions
  chart.setOption({
    radar: {
      center: ['50%', '52%'], radius: '62%',
      indicator: Object.values(dims).map((d: any) => ({ name: d.label, max: 100 })),
      axisName: { color: '#7d5e30', fontSize: 11, fontWeight: 500 },
      splitArea: { areaStyle: { color: ['#fff', '#f8f6f0'] } },
      splitLine: { lineStyle: { color: '#e2d8c0' } },
      axisLine: { lineStyle: { color: '#d4c8a8' } },
    },
    series: [{
      type: 'radar',
      data: [{ value: Object.values(dims).map((d: any) => d.score), name: '能力画像', areaStyle: { color: 'rgba(184,148,90,0.18)' } }],
      lineStyle: { color: '#b8945a', width: 2 },
      itemStyle: { color: '#b8945a' },
    }],
  })
}

onMounted(loadReport)
</script>

<template>
  <div class="min-h-screen pb-20" style="background: #f8f6f0">
    <div class="text-center px-4 py-4 border-b" style="background: rgba(248,246,240,0.92); border-color: #e2d8c0">
      <h1 class="display-font text-lg font-semibold" style="color: #5a4220">{{ report?.share_from || '...' }} 的能力画像</h1>
    </div>

    <div v-if="loading" class="flex justify-center py-24">
      <div class="w-10 h-10 border-2 rounded-full animate-spin" style="border-color: #b8945a; border-top-color: transparent"/>
    </div>

    <template v-if="report">
      <div class="mx-4 mt-4 rounded-2xl p-3" style="background: #fff">
        <div id="shared-radar" style="width:100%;height:300px" />
      </div>
      <div class="mx-4 mt-4 rounded-2xl p-5" style="background: #fff">
        <p class="text-sm leading-relaxed" style="color: #5a4220">{{ report.summary }}</p>
      </div>
      <div class="text-center mt-10">
        <p class="text-sm mb-5" style="color: #9b8a70">想了解你的优势吗？</p>
        <button @click="router.push('/')"
          class="px-10 py-4 rounded-2xl text-white font-semibold text-lg transition-all active:scale-95"
          style="background: linear-gradient(135deg, #8ba888, #7a9876); box-shadow: 0 4px 20px rgba(139,168,136,0.3)"
        >我也要测评</button>
      </div>
    </template>
  </div>
</template>
