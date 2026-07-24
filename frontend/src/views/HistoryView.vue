<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { listReports } from '@/api/report'

const router = useRouter()
const reports = ref<any[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await listReports()
    reports.value = res.data.items || []
  } catch {}
  loading.value = false
})
</script>

<template>
  <div class="min-h-screen pb-12" style="background: #f8f6f0">
    <div class="sticky top-0 z-10 px-4 py-3 border-b flex items-center gap-2"
      style="background: rgba(248,246,240,0.92); backdrop-filter: blur(8px); border-color: #e2d8c0">
      <button @click="router.push('/')" style="color: #9b8a70">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
      </button>
      <h1 class="display-font text-lg font-semibold" style="color: #5a4220">历史报告</h1>
    </div>

    <div v-if="loading" class="flex justify-center py-24">
      <div class="w-10 h-10 border-2 rounded-full animate-spin" style="border-color: #b8945a; border-top-color: transparent"/>
    </div>

    <div v-else-if="reports.length === 0" class="text-center py-24">
      <p style="color: #9b8a70">还没有报告</p>
      <button @click="router.push('/assessment')" class="mt-4 px-8 py-3 rounded-xl text-white font-medium" style="background: #b8945a">开始测评</button>
    </div>

    <div v-else class="mx-4 mt-4 space-y-3">
      <div v-for="r in reports" :key="r.id" @click="router.push(`/report/${r.id}`)"
        class="rounded-2xl p-5 cursor-pointer transition-all active:scale-[0.98]" style="background: #fff; box-shadow: 0 2px 8px rgba(0,0,0,0.03)">
        <div class="flex justify-between items-center mb-3">
          <span class="text-xs" style="color: #9b8a70">{{ new Date(r.created_at).toLocaleDateString() }}</span>
          <svg class="w-4 h-4" style="color: #c4a97a" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
        </div>
        <div class="flex flex-wrap gap-2">
          <span v-for="(dim, key) in r.dimensions" :key="key"
            class="px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors"
            :style="dim.score >= 75
              ? 'background: #c5d8c3; color: #4a7a40'
              : dim.score >= 50
              ? 'background: #f0ece0; color: #7d5e30'
              : 'background: #f5e0d8; color: #a06040'"
          >{{ dim.label }} {{ dim.score }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
