<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { generateReport, getGeneratedReportId } from '@/api/report'

interface Question {
  questionId: string
  text: string
  agentMessage: string
  dimension: string
  round: number
}

const labels: Record<number, string> = {
  1: '非常不符合',
  2: '不太符合',
  3: '一般',
  4: '比较符合',
  5: '非常符合',
}

const dimensionNames: Record<string, string> = {
  thinking: '思维方式',
  creativity: '创造倾向',
  execution: '行动模式',
  social: '协作方式',
  emotional: '情绪韧性',
  drive: '内在驱动',
}

const router = useRouter()
const auth = useAuthStore()
const assessmentId = ref(0)
const currentRound = ref(0)
const totalRounds = ref(10)
const question = ref<Question | null>(null)
const selected = ref<number | null>(null)
const loading = ref(true)
const submitting = ref(false)
const generating = ref(false)
const error = ref('')

const progress = computed(() => Math.max(4, (currentRound.value / totalRounds.value) * 100))
const dimensionLabel = computed(() => dimensionNames[question.value?.dimension || ''] || '优势探索')

function authHeaders() {
  return {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${auth.accessToken}`,
  }
}

async function readSSE(response: Response, onEvent: (event: string, data: any) => Promise<void> | void) {
  if (!response.ok) throw new Error(`请求失败（${response.status}）`)
  const reader = response.body?.getReader()
  if (!reader) throw new Error('浏览器无法读取测评流')

  const decoder = new TextDecoder()
  let buffer = ''

  async function processBlock(block: string) {
    let event = 'message'
    let data: any = null
    for (const line of block.split(/\r?\n/)) {
      if (line.startsWith('event:')) event = line.slice(6).trim()
      if (line.startsWith('data:')) data = JSON.parse(line.slice(5).trim())
    }
    if (data !== null) await onEvent(event, data)
  }

  while (true) {
    const { done, value } = await reader.read()
    buffer += decoder.decode(value || new Uint8Array(), { stream: !done })
    const blocks = buffer.split(/\r?\n\r?\n/)
    buffer = blocks.pop() || ''
    for (const block of blocks) await processBlock(block)
    if (done) break
  }
  if (buffer.trim()) await processBlock(buffer)
}

function acceptQuestion(data: any) {
  question.value = {
    questionId: data.question_id,
    text: data.question_text,
    agentMessage: data.agent_message || '慢慢来，选择最接近你真实状态的答案。',
    dimension: data.target_dimension,
    round: data.round,
  }
  currentRound.value = data.round
  selected.value = null
}

async function startAssessment() {
  loading.value = true
  error.value = ''
  try {
    const response = await fetch('/api/v1/assessment/start', {
      method: 'POST',
      headers: authHeaders(),
    })
    await readSSE(response, async (event, data) => {
      if (event === 'start') {
        assessmentId.value = data.assessment_id
        totalRounds.value = data.total_rounds || 10
      }
      if (event === 'question' || data.question_id) acceptQuestion(data)
    })
  } catch (e: any) {
    error.value = e.message || '测评启动失败，请稍后重试。'
  } finally {
    loading.value = false
  }
}

async function finishAssessment() {
  if (generating.value) return
  generating.value = true
  error.value = ''
  try {
    const generated = await generateReport(assessmentId.value)
    await router.push(`/report/${getGeneratedReportId(generated)}`)
  } catch {
    error.value = '报告生成失败，请检查网络后重试。'
    generating.value = false
  }
}

async function submitAnswer(value: number) {
  if (!question.value || submitting.value) return
  selected.value = value
  submitting.value = true
  error.value = ''
  try {
    const response = await fetch(`/api/v1/assessment/${assessmentId.value}/answer`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({
        question_id: question.value.questionId,
        answer_value: value,
      }),
    })
    await readSSE(response, async (event, data) => {
      if (event === 'complete') {
        await finishAssessment()
        return
      }
      if (event === 'error') throw new Error(data.msg || '答案提交失败')
      if (event === 'question' || data.question_id) acceptQuestion(data)
    })
  } catch (e: any) {
    error.value = e.message || '答案提交失败，请稍后再试。'
    selected.value = null
  } finally {
    submitting.value = false
  }
}

onMounted(startAssessment)
</script>

<template>
  <main class="min-h-screen pb-10">
    <header class="border-b border-[var(--seed-border)] bg-[var(--seed-canvas)]/80 backdrop-blur-xl">
      <div class="seed-shell seed-nav">
        <button class="seed-brand border-0 bg-transparent p-0" @click="router.push('/')">
          <span class="seed-mark" aria-hidden="true" />
          <span>Seed</span>
        </button>
        <button class="min-h-11 rounded-xl px-3 text-sm font-medium text-[var(--seed-muted)]" @click="router.push('/')">暂时退出</button>
      </div>
    </header>

    <section class="seed-shell mx-auto max-w-[900px] pt-8 sm:pt-14">
      <div class="mb-8 flex items-end justify-between gap-4">
        <div>
          <p class="text-xs font-semibold uppercase tracking-[.2em] text-[var(--seed-green)]">优势测评</p>
          <h1 class="mt-2 text-2xl font-semibold tracking-[-.035em] sm:text-3xl">跟随第一直觉，不必过度思考。</h1>
        </div>
        <span class="shrink-0 text-sm font-semibold tabular-nums text-[var(--seed-muted)]">{{ currentRound }}/{{ totalRounds }}</span>
      </div>

      <div class="mb-7 h-1.5 overflow-hidden rounded-full bg-black/6">
        <div class="h-full rounded-full bg-[var(--seed-green)] transition-[width] duration-500" :style="{ width: `${progress}%` }" />
      </div>

      <div v-if="error" role="alert" class="mb-5 flex items-center justify-between gap-4 rounded-2xl border border-red-100 bg-red-50 px-4 py-3 text-sm text-red-700">
        <span>{{ error }}</span>
        <button v-if="!assessmentId" class="shrink-0 font-semibold underline" @click="startAssessment">重试</button>
        <button v-else-if="generating === false && currentRound >= totalRounds" class="shrink-0 font-semibold underline" @click="finishAssessment">重新生成</button>
      </div>

      <div v-if="loading || generating" class="seed-card flex min-h-[470px] flex-col items-center justify-center p-8 text-center">
        <div class="relative h-14 w-14">
          <div class="absolute inset-0 animate-ping rounded-full bg-[var(--seed-green-soft)]" />
          <div class="relative flex h-14 w-14 items-center justify-center rounded-full bg-[var(--seed-green)] text-white">
            <span class="seed-mark !border-0 !bg-transparent brightness-0 invert" />
          </div>
        </div>
        <h2 class="mt-7 text-xl font-semibold">{{ generating ? '正在生成你的优势报告' : '正在准备第一道问题' }}</h2>
        <p class="mt-2 text-sm text-[var(--seed-muted)]">{{ generating ? '我们正在整理六个维度的证据与建议…' : 'AI 正在从科学题库中选择起点…' }}</p>
      </div>

      <article v-else-if="question" class="seed-card overflow-hidden">
        <div class="border-b border-[var(--seed-border)] px-5 py-4 sm:px-8">
          <div class="flex items-center gap-3">
            <span class="flex h-9 w-9 items-center justify-center rounded-xl bg-[var(--seed-green-soft)] text-xs font-bold text-[var(--seed-green)]">AI</span>
            <div>
              <p class="text-xs font-semibold uppercase tracking-[.16em] text-[var(--seed-muted)]">{{ dimensionLabel }}</p>
              <p class="mt-0.5 text-sm text-[var(--seed-muted)]">{{ question.agentMessage }}</p>
            </div>
          </div>
        </div>

        <div class="px-5 py-7 sm:px-10 sm:py-10">
          <p class="text-xs font-semibold text-[var(--seed-gold)]">问题 {{ question.round }}</p>
          <h2 class="mt-3 max-w-3xl text-2xl font-semibold leading-[1.42] tracking-[-.035em] sm:text-3xl">{{ question.text }}</h2>

          <div class="mt-8 grid gap-3 sm:grid-cols-5">
            <button
              v-for="value in 5"
              :key="value"
              class="group min-h-[88px] rounded-2xl border p-3 text-center transition disabled:cursor-wait disabled:opacity-60"
              :class="selected === value
                ? 'border-[var(--seed-green)] bg-[var(--seed-green)] text-white shadow-lg shadow-green-900/10'
                : 'border-[var(--seed-border)] bg-white/55 hover:-translate-y-0.5 hover:border-[var(--seed-green)] hover:bg-white'"
              :disabled="submitting"
              @click="submitAnswer(value)"
            >
              <span class="block text-lg font-semibold">{{ value }}</span>
              <span class="mt-2 block text-xs" :class="selected === value ? 'text-white/80' : 'text-[var(--seed-muted)]'">{{ labels[value] }}</span>
            </button>
          </div>

          <div class="mt-7 flex items-center justify-between gap-4 text-xs text-[var(--seed-muted)]">
            <span>没有正确答案，真实比完美更重要。</span>
            <span v-if="submitting" class="font-semibold text-[var(--seed-green)]">正在记录…</span>
          </div>
        </div>
      </article>
    </section>
  </main>
</template>
