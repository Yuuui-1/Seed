<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

interface Message {
  role: 'agent' | 'user' | 'preview'
  content: string
  options?: { value: number; label: string }[]
  questionId?: string
  round?: number
  score?: number
  showRegisterPrompt?: boolean
}

const messages = ref<Message[]>([])
const assessmentId = ref(0)
const currentRound = ref(0)
const totalRounds = ref(10)
const status = ref<'idle' | 'active' | 'completed'>('idle')
const selectedOption = ref<number | null>(null)
const chatContainer = ref<HTMLElement | null>(null)
const sessionId = ref(localStorage.getItem('session_id') || '')

function scrollToBottom() {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

async function startAssessment() {
  status.value = 'active'
  messages.value = []
  const token = auth.accessToken
  const headers: Record<string, string> = {}
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch('/api/v1/assessment/start', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...headers },
  })

  const reader = res.body?.getReader()
  if (!reader) return

  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })

    const lines = buffer.split('\n')
    buffer = lines.pop() || ''

    for (const line of lines) {
      if (line.startsWith('event: ')) continue
      if (line.startsWith('data: ')) {
        const data = JSON.parse(line.slice(6))
        handleSSEEvent(data)
      }
    }
  }
}

function handleSSEEvent(data: any) {
  if (data.assessment_id) {
    assessmentId.value = data.assessment_id
    totalRounds.value = data.total_rounds || 10
  }
  if (data.question_id) {
    currentRound.value = data.round
    messages.value.push({
      role: 'agent',
      content: data.agent_message || questionMessages[data.target_dimension] || '...',
    })
    messages.value.push({
      role: 'agent',
      content: data.question_text,
      options: [
        { value: 1, label: '非常不符合' },
        { value: 2, label: '不太符合' },
        { value: 3, label: '一般' },
        { value: 4, label: '比较符合' },
        { value: 5, label: '非常符合' },
      ],
      questionId: data.question_id,
      round: data.round,
    })
    selectedOption.value = null
    scrollToBottom()
  }
  if (data.score !== undefined && data.show_register_prompt) {
    messages.value.push({
      role: 'preview',
      content: data.message || '初步评估完成，想看完整报告吗？',
      score: data.score,
      showRegisterPrompt: true,
    })
    scrollToBottom()
  }
  if (data.message === '测评已完成') {
    status.value = 'completed'
    messages.value.push({
      role: 'agent',
      content: '测评完成！正在生成你的报告...',
    })
    // Navigate to generate report
    router.push(`/report/${assessmentId.value}`)
  }
}

async function selectOption(value: number) {
  selectedOption.value = value
  const lastMsg = messages.value[messages.value.length - 1]
  messages.value.push({ role: 'user', content: getOptionLabel(value) })
  scrollToBottom()

  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (auth.accessToken) headers['Authorization'] = `Bearer ${auth.accessToken}`

  const body: any = { question_id: lastMsg.questionId, answer_value: value }
  if (sessionId.value) body.session_id = sessionId.value

  const res = await fetch(`/api/v1/assessment/${assessmentId.value}/answer`, {
    method: 'POST',
    headers,
    body: JSON.stringify(body),
  })

  const reader = res.body?.getReader()
  if (!reader) return
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() || ''
    for (const line of lines) {
      if (line.startsWith('event: ')) {
        const eventType = line.slice(7)
        if (eventType === 'complete') {
          status.value = 'completed'
          messages.value.push({ role: 'agent', content: '测评完成！正在生成报告...' })
          router.push(`/report/${assessmentId.value}`)
        }
        continue
      }
      if (line.startsWith('data: ')) {
        const d = JSON.parse(line.slice(6))
        if (d.question_id) handleSSEEvent(d)
        if (d.score !== undefined && d.show_register_prompt) {
          messages.value.push({
            role: 'preview',
            content: d.message,
            score: d.score,
            showRegisterPrompt: true,
          })
          scrollToBottom()
        }
      }
    }
  }
}

function getOptionLabel(v: number) {
  const map: Record<number, string> = { 1: '非常不符合', 2: '不太符合', 3: '一般', 4: '比较符合', 5: '非常符合' }
  return map[v] || ''
}

const questionMessages: Record<string, string> = {
  thinking: '接下来想了解你的思维方式...',
  creativity: '很好，来看看你的创造力...',
  execution: '现在来了解你的执行力...',
  social: '来看看你在团队中的角色...',
  emotional: '接下来关注你的情绪调节能力...',
  drive: '最后来探索你的内在驱动力...',
}

onMounted(() => {
  startAssessment()
})
</script>

<template>
  <div class="min-h-screen flex flex-col bg-slate-50">
    <!-- Header -->
    <div class="sticky top-0 bg-white/90 backdrop-blur px-4 py-3 border-b border-slate-100 z-10">
      <div class="flex items-center gap-2">
        <button @click="router.push('/')" class="text-slate-400">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
        </button>
        <h1 class="text-lg font-semibold text-slate-800">优势测评</h1>
      </div>
      <!-- Progress -->
      <div class="mt-2 flex items-center gap-2">
        <div class="flex-1 h-1.5 bg-slate-100 rounded-full overflow-hidden">
          <div
            class="h-full bg-indigo-500 rounded-full transition-all duration-500"
            :style="{ width: `${(currentRound / totalRounds) * 100}%` }"
          />
        </div>
        <span class="text-xs text-slate-400">{{ currentRound }}/{{ totalRounds }}</span>
      </div>
    </div>

    <!-- Chat -->
    <div ref="chatContainer" class="flex-1 overflow-y-auto px-4 py-4 space-y-3">
      <template v-for="(msg, i) in messages" :key="i">
        <!-- Agent message -->
        <div v-if="msg.role === 'agent' && !msg.options" class="flex gap-2">
          <div class="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center shrink-0">
            <span class="text-indigo-500 text-sm">AI</span>
          </div>
          <div class="bg-white rounded-2xl rounded-tl-sm px-3.5 py-2.5 text-slate-700 text-sm max-w-[80%] shadow-sm">
            {{ msg.content }}
          </div>
        </div>

        <!-- Question card -->
        <div v-if="msg.options" class="flex gap-2">
          <div class="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center shrink-0">
            <span class="text-indigo-500 text-sm">AI</span>
          </div>
          <div class="bg-white rounded-2xl rounded-tl-sm px-4 py-3 max-w-[85%] shadow-sm">
            <p class="text-slate-700 text-sm mb-3">{{ msg.content }}</p>
            <div class="space-y-2">
              <button
                v-for="opt in msg.options"
                :key="opt.value"
                @click="selectOption(opt.value)"
                :disabled="selectedOption !== null"
                class="w-full text-left px-3.5 py-2.5 rounded-xl border text-sm transition-all"
                :class="selectedOption === opt.value
                  ? 'border-indigo-400 bg-indigo-50 text-indigo-600'
                  : 'border-slate-200 text-slate-600 hover:border-indigo-200'"
              >
                {{ opt.label }}
              </button>
            </div>
          </div>
        </div>

        <!-- User answer -->
        <div v-if="msg.role === 'user'" class="flex justify-end">
          <div class="bg-indigo-500 text-white rounded-2xl rounded-tr-sm px-3.5 py-2.5 text-sm max-w-[75%]">
            {{ msg.content }}
          </div>
        </div>

        <!-- Preview -->
        <div v-if="msg.role === 'preview'" class="flex gap-2">
          <div class="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center shrink-0">
            <span class="text-indigo-500 text-sm">AI</span>
          </div>
          <div class="bg-white rounded-2xl rounded-tl-sm px-4 py-3 max-w-[85%] shadow-sm">
            <p class="text-slate-700 text-sm mb-2">{{ msg.content }}</p>
            <div v-if="msg.score" class="flex items-center gap-2 mb-2">
              <span class="text-2xl font-bold text-indigo-500">{{ msg.score }}</span>
              <span class="text-xs text-slate-400">思维力初步分数</span>
            </div>
            <div v-if="msg.showRegisterPrompt && !auth.isAuthenticated" class="flex gap-2 mt-2">
              <button @click="router.push('/register')" class="flex-1 py-2 rounded-lg bg-indigo-500 text-white text-sm font-medium">
                注册查看完整报告
              </button>
              <button @click="selectOption(0)" class="flex-1 py-2 rounded-lg border border-slate-200 text-slate-500 text-sm">
                继续测评
              </button>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>
