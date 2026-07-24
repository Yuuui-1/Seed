<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

onMounted(async () => {
  if (auth.accessToken && !auth.user) {
    try { await auth.fetchMe() } catch {}
  }
})
</script>

<template>
  <router-view />
</template>
