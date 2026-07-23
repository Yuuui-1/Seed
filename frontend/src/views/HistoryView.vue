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

const dimNames: Record<string, string> = {
  thinking: '思维力', creativity: '创造力', execution: '执行力',
  social: '社交力', emotional: '情绪力', drive: '驱动力',
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 pb-12">
    <div class="bg-white px-4 py-3 border-b border-slate-100 flex items-center gap-2">
      <button @click="router.push('/')" class="text-slate-400">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
      </button>
      <h1 class="text-lg font-semibold text-slate-800">历史报告</h1>
    </div>

    <div v-if="loading" class="flex justify-center py-20">
      <div class="animate-spin w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full" />
    </div>

    <div v-else-if="reports.length === 0" class="text-center py-20 text-slate-400">
      <p>还没有报告</p>
      <button @click="router.push('/assessment')" class="mt-4 text-indigo-500 font-medium">去测评</button>
    </div>

    <div v-else class="mx-4 mt-4 space-y-3">
      <div
        v-for="r in reports"
        :key="r.id"
        @click="router.push(`/report/${r.id}`)"
        class="bg-white rounded-2xl p-4 shadow-sm cursor-pointer"
      >
        <div class="flex items-center justify-between mb-3">
          <span class="text-sm text-slate-400">{{ new Date(r.created_at).toLocaleDateString() }}</span>
          <svg class="w-5 h-5 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
        </div>
        <div class="flex flex-wrap gap-2">
          <span
            v-for="(dim, key) in r.dimensions"
            :key="key"
            class="px-2.5 py-1 rounded-lg text-xs font-medium"
            :class="dim.score >= 75 ? 'bg-indigo-50 text-indigo-600' : dim.score >= 50 ? 'bg-slate-100 text-slate-600' : 'bg-orange-50 text-orange-600'"
          >
            {{ dim.label }} {{ dim.score }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>
