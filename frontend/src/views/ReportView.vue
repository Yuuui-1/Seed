<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { generateReport, getReport, getReportByAssessment, shareReport } from '@/api/report'
import { bindAssessment } from '@/api/assessment'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const report = ref<any>(null)
const loading = ref(true)
const sharing = ref(false)
const shareUrl = ref('')
const needLogin = ref(false)
const aid = Number(route.params.id)

async function loadReport() {
  try {
    // Try by assessment ID first (new auto-generate flow)
    const res = await getReportByAssessment(aid)
    report.value = res.data
  } catch {
    // Fallback: try as report ID, or generate
    try { report.value = (await getReport(aid)).data } catch {
      if (auth.isAuthenticated) {
        try {
          await bindAssessment(aid)
          report.value = (await generateReport(aid)).data || (await getReportByAssessment(aid)).data
        } catch { report.value = null }
      } else {
        needLogin.value = true
      }
    }
  }
  loading.value = false
  if (report.value) setTimeout(renderRadar, 200)
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
      center: ['50%', '52%'],
      radius: '68%',
      indicator: labels.map((label: string) => ({ name: label, max: 100 })),
      axisName: { color: '#7d5e30', fontSize: 11, fontWeight: 500 },
      splitArea: { areaStyle: { color: ['#fff', '#f8f6f0'] } },
      splitLine: { lineStyle: { color: '#e2d8c0' } },
      axisLine: { lineStyle: { color: '#d4c8a8' } },
    },
    series: [{
      type: 'radar',
      data: [{ value: scores, name: '能力画像', areaStyle: { color: 'rgba(184,148,90,0.18)' } }],
      lineStyle: { color: '#b8945a', width: 2 },
      itemStyle: { color: '#b8945a' },
      symbol: 'circle', symbolSize: 5,
    }],
  })
}

async function handleShare() {
  if (!report.value) return
  sharing.value = true
  try {
    const res = await shareReport(report.value.id)
    shareUrl.value = res.data.share_url
  } catch { } finally { sharing.value = false }
}
</script>

<template>
  <div class="min-h-screen pb-20" style="background: #f8f6f0">
    <div class="sticky top-0 z-10 px-4 py-3 border-b flex items-center gap-2"
      style="background: rgba(248,246,240,0.92); backdrop-filter: blur(8px); border-color: #e2d8c0">
      <button @click="router.push('/')" style="color: #9b8a70">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
      </button>
      <h1 class="text-lg font-semibold" style="color: #5a4220">你的能力画像</h1>
    </div>

    <div v-if="loading" class="flex justify-center py-24">
      <div class="w-10 h-10 border-2 rounded-full animate-spin" style="border-color: #b8945a; border-top-color: transparent"/>
    </div>

    <div v-else-if="needLogin" class="text-center py-24 px-6">
      <p class="text-sm mb-2" style="color: #7d5e30">请先登录以查看完整报告</p>
      <p class="text-xs mb-6" style="color: #9b8a70">你的测评数据已保存</p>
      <button @click="router.push('/login')" class="px-10 py-3 rounded-xl text-white font-semibold"
        style="background: #b8945a">去登录</button>
    </div>

    <div v-else-if="!report" class="text-center py-24">
      <p style="color: #9b8a70">报告生成失败，请重试</p>
      <button @click="router.push('/')" class="mt-4 px-6 py-2.5 rounded-xl text-white text-sm" style="background: #b8945a">返回首页</button>
    </div>

    <template v-if="report">
      <!-- Radar -->
      <div class="mx-4 mt-4 rounded-2xl p-3" style="background: #fff; box-shadow: 0 2px 12px rgba(0,0,0,0.04)">
        <div id="radar-chart" style="width:100%;height:340px" />
      </div>

      <!-- Summary -->
      <div class="mx-4 mt-4 rounded-2xl p-5" style="background: #fff; box-shadow: 0 2px 12px rgba(0,0,0,0.04)">
        <h3 class="display-font text-lg font-semibold mb-2" style="color: #5a4220">总体评价</h3>
        <p class="text-sm leading-relaxed" style="color: #7d5e30">{{ report.summary }}</p>
      </div>

      <!-- Dimensions -->
      <div class="mx-4 mt-4 space-y-3">
        <div v-for="(dim, key) in report.dimensions" :key="key" class="rounded-2xl p-5 animate-fade-up"
          style="background: #fff; box-shadow: 0 2px 12px rgba(0,0,0,0.04)">
          <div class="flex items-center justify-between mb-3">
            <h3 class="display-font text-lg font-semibold" style="color: #5a4220">{{ dim.label }}</h3>
            <span class="display-font text-3xl font-bold" :style="dim.score >= 75 ? 'color:#8ba888' : dim.score >= 50 ? 'color:#b8945a' : 'color:#c1785a'">{{ dim.score }}</span>
          </div>
          <div class="h-2 rounded-full overflow-hidden mb-4" style="background: #e2d8c0">
            <div class="h-full rounded-full transition-all duration-1000"
              :style="{ width: `${dim.score}%`, background: dim.score >= 75 ? 'linear-gradient(90deg,#8ba888,#6d9a6d)' : dim.score >= 50 ? 'linear-gradient(90deg,#b8945a,#a07a40)' : 'linear-gradient(90deg,#c1785a,#b06040)' }"
            />
          </div>
          <p class="text-sm leading-relaxed" style="color: #5a4220">{{ dim.strengths || dim.description }}</p>
        </div>
      </div>

      <!-- Career -->
      <div v-if="report.career_suggestions?.length" class="mx-4 mt-4 rounded-2xl p-5" style="background: #fff; box-shadow: 0 2px 12px rgba(0,0,0,0.04)">
        <h3 class="display-font text-lg font-semibold mb-4" style="color: #5a4220">职业方向推荐</h3>
        <div class="space-y-3">
          <div v-for="(s, i) in report.career_suggestions" :key="i" class="flex items-center justify-between py-2.5 border-b last:border-0" style="border-color: #e2d8c0">
            <div>
              <span class="text-sm font-semibold" style="color: #3d2d14">{{ s.direction }}</span>
              <p class="text-xs mt-0.5" style="color: #9b8a70">{{ s.reason }}</p>
            </div>
            <span class="display-font text-lg font-bold" style="color: #8ba888">{{ s.match }}%</span>
          </div>
        </div>
      </div>

      <!-- Share -->
      <div class="mx-4 mt-6 text-center">
        <button @click="handleShare" :disabled="sharing"
          class="w-full py-3.5 rounded-xl text-white font-semibold text-lg transition-all active:scale-95"
          style="background: linear-gradient(135deg, #8ba888, #7a9876)"
        >{{ sharing ? '生成中...' : shareUrl ? '已生成分享链接' : '分享报告' }}</button>
        <input v-if="shareUrl" :value="shareUrl" readonly
          class="w-full mt-3 px-4 py-2.5 rounded-xl text-sm text-center outline-none"
          style="background: #fff; border: 2px solid #8ba888; color: #5a4220"
          @focus="$event.target.select()"
        />
      </div>
    </template>
  </div>
</template>
