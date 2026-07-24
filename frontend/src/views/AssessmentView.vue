<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

interface Message {
  role: 'agent' | 'user' | 'question' | 'preview'
  content: string
  options?: { value: number; label: string }[]
  questionId?: string
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
const error = ref('')
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
  error.value = ''
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (auth.accessToken) headers['Authorization'] = `Bearer ${auth.accessToken}`

  // If URL has an assessment ID, start fresh anyway
  const urlId = route.params.id as string
  if (urlId) {
    assessmentId.value = Number(urlId)
  }

  messages.value = []
  try {
    const res = await fetch('/api/v1/assessment/start', { method: 'POST', headers })
    if (!res.ok) throw new Error('HTTP ' + res.status)
    const reader = res.body?.getReader()
    if (!reader) { error.value = '无法连接服务器'; return }
    await readSSEStream(reader)
  } catch (e: any) {
    error.value = e.message || '连接失败'; status.value = 'idle'
  }
}

function handleSSEEvent(eventType: string, data: any) {
  if (eventType === 'start') {
    assessmentId.value = data.assessment_id
    totalRounds.value = data.total_rounds || 10
    scrollToBottom()
    return
  }
  if (eventType === 'question') {
    currentRound.value = data.round
    messages.value.push({ role: 'question', content: data.question_text, options: data.options, questionId: data.question_id })
    selectedOption.value = null
    scrollToBottom()
    return
  }
  if (eventType === 'preview') {
    messages.value.push({ role: 'preview', content: data.message, score: data.score, showRegisterPrompt: data.show_register_prompt })
    scrollToBottom()
    return
  }
  if (eventType === 'complete') {
    status.value = 'completed'
    messages.value.push({ role: 'agent', content: '测评完成！正在生成报告...' })
    scrollToBottom()
    // Backend auto-generates report on completion, just navigate
    setTimeout(() => router.push(`/report/${assessmentId.value}`), 2000)
    return
  }
}

async function readSSEStream(reader: ReadableStreamDefaultReader<Uint8Array>) {
  const decoder = new TextDecoder()
  let buffer = ''
  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() || ''
    let eventType = ''
    for (const line of lines) {
      if (line.startsWith('event: ')) { eventType = line.slice(7).trim(); continue }
      if (line.startsWith('data: ')) {
        try { handleSSEEvent(eventType, JSON.parse(line.slice(6))) } catch {}
      }
    }
  }
}

async function selectOption(value: number) {
  selectedOption.value = value
  const label = ['', '非常不符合', '不太符合', '一般', '比较符合', '非常符合'][value] || ''
  messages.value.push({ role: 'user', content: label })
  scrollToBottom()

  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (auth.accessToken) headers['Authorization'] = `Bearer ${auth.accessToken}`
  const body: any = { question_id: messages.value[messages.value.length - 2].questionId, answer_value: value }
  if (sessionId.value) body.session_id = sessionId.value

  try {
    const res = await fetch(`/api/v1/assessment/${assessmentId.value}/answer`, {
      method: 'POST', headers, body: JSON.stringify(body),
    })
    if (!res.ok) throw new Error('HTTP ' + res.status)
    const reader = res.body?.getReader()
    if (!reader) return
    await readSSEStream(reader)
  } catch (e: any) {
    error.value = e.message || '提交失败'
  }
}

onMounted(startAssessment)
</script>

<template>
  <div class="min-h-screen flex flex-col" style="background: #f8f6f0">
    <!-- Header -->
    <div class="sticky top-0 z-10 px-4 py-3 border-b" style="background: rgba(248,246,240,0.92); backdrop-filter: blur(8px); border-color: #e2d8c0">
      <div class="flex items-center gap-2 mb-2">
        <button @click="router.push('/')" style="color: #9b8a70">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
        </button>
        <h1 class="text-lg font-semibold" style="color: #5a4220">优势测评</h1>
      </div>
      <div class="flex items-center gap-2">
        <div class="flex-1 h-2 rounded-full overflow-hidden" style="background: #e2d8c0">
          <div class="h-full rounded-full transition-all duration-700 ease-out" style="background: linear-gradient(90deg, #b8945a, #8ba888)"
            :style="{ width: `${(currentRound / totalRounds) * 100}%` }"
          />
        </div>
        <span class="text-xs font-medium" style="color: #9b8a70">{{ currentRound }}/{{ totalRounds }}</span>
      </div>
    </div>

    <!-- Chat -->
    <div ref="chatContainer" class="flex-1 overflow-y-auto px-5 py-5 space-y-4">
      <!-- Error -->
      <div v-if="error" class="text-center py-12">
        <p class="text-sm mb-4" style="color: #c1785a">{{ error }}</p>
        <button @click="startAssessment()" class="px-6 py-2.5 rounded-xl text-white text-sm font-medium"
          style="background: #b8945a">重试</button>
      </div>

      <!-- Agent greeting -->
      <div v-if="messages.length === 0 && !error" class="flex justify-center py-12">
        <div class="w-10 h-10 border-2 rounded-full animate-spin" style="border-color: #b8945a; border-top-color: transparent"/>
      </div>

      <template v-for="(msg, i) in messages" :key="i">
        <!-- Agent text -->
        <div v-if="msg.role === 'agent'" class="flex gap-2.5 animate-fade-up">
          <div class="w-9 h-9 rounded-full flex items-center justify-center shrink-0 text-sm"
            style="background: linear-gradient(135deg, #8ba888, #7a9876); color: #fff">AI</div>
          <div class="px-4 py-3 rounded-2xl rounded-tl-sm text-sm leading-relaxed max-w-[82%]" style="background: #fff; color: #5a4220; box-shadow: 0 1px 3px rgba(0,0,0,0.04)">
            {{ msg.content }}
          </div>
        </div>

        <!-- Question card -->
        <div v-if="msg.role === 'question'" class="flex gap-2.5 animate-fade-up">
          <div class="w-9 h-9 rounded-full flex items-center justify-center shrink-0 text-sm"
            style="background: linear-gradient(135deg, #8ba888, #7a9876); color: #fff">AI</div>
          <div class="px-4 py-3 rounded-2xl rounded-tl-sm max-w-[88%]" style="background: #fff; color: #5a4220; box-shadow: 0 1px 3px rgba(0,0,0,0.04)">
            <p class="text-sm font-medium mb-3 leading-relaxed" style="color: #3d2d14">{{ msg.content }}</p>
            <div class="space-y-2">
              <button
                v-for="opt in msg.options"
                :key="opt.value"
                @click="selectOption(opt.value)"
                :disabled="selectedOption !== null"
                class="w-full text-left px-4 py-3 rounded-xl text-sm font-medium option-btn border-2"
                :style="selectedOption === opt.value
                  ? 'background: #f0ece0; border-color: #b8945a; color: #7d5e30'
                  : 'background: #faf8f4; border-color: transparent; color: #7d5e30'"
              >
                {{ opt.label }}
              </button>
            </div>
          </div>
        </div>

        <!-- User answer -->
        <div v-if="msg.role === 'user'" class="flex justify-end animate-fade-up">
          <div class="px-4 py-2.5 rounded-2xl rounded-tr-sm text-sm max-w-[75%]" style="background: linear-gradient(135deg, #b8945a, #a07a40); color: #fff">
            {{ msg.content }}
          </div>
        </div>

        <!-- Preview -->
        <div v-if="msg.role === 'preview'" class="flex gap-2.5 animate-fade-up">
          <div class="w-9 h-9 rounded-full flex items-center justify-center shrink-0 text-sm"
            style="background: linear-gradient(135deg, #8ba888, #7a9876); color: #fff">AI</div>
          <div class="px-4 py-4 rounded-2xl rounded-tl-sm max-w-[88%]" style="background: #fff; box-shadow: 0 1px 3px rgba(0,0,0,0.04)">
            <p class="text-sm font-medium mb-3" style="color: #3d2d14">{{ msg.content }}</p>
            <div v-if="msg.score" class="flex items-end gap-2 mb-3">
              <span class="display-font text-4xl font-bold" style="color: #b8945a">{{ msg.score }}</span>
              <span class="text-xs pb-1" style="color: #9b8a70">思维力初步分数</span>
            </div>
            <div v-if="msg.showRegisterPrompt && !auth.isAuthenticated" class="flex gap-2">
              <button @click="router.push(`/register?redirect=/assessment/${assessmentId}`)" class="flex-1 py-2.5 rounded-xl text-white text-sm font-semibold"
                style="background: linear-gradient(135deg, #b8945a, #a07a40)">注册查看完整报告</button>
              <button class="flex-1 py-2.5 rounded-xl text-sm font-medium" style="background: #f0ece0; color: #7d5e30">继续测评</button>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>
