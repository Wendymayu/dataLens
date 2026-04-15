<script setup lang="ts">
import { ref } from 'vue'
import { Icon } from '@iconify/vue'
import hljs from 'highlight.js'

const props = defineProps<{
  sql: string
}>()

const copied = ref(false)

const highlightedSql = hljs.highlight(props.sql, { language: 'sql' }).value

async function copySql() {
  try {
    await navigator.clipboard.writeText(props.sql)
    copied.value = true
    setTimeout(() => copied.value = false, 2000)
  } catch {}
}
</script>

<template>
  <div class="relative rounded-lg overflow-hidden border border-gray-200 bg-slate-900">
    <!-- Header -->
    <div class="flex items-center justify-between px-3 py-2 bg-slate-800">
      <span class="text-xs font-medium text-slate-400">SQL</span>
      <button
        @click="copySql"
        class="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1"
      >
        <Icon :icon="copied ? 'lucide:check' : 'lucide:copy'" class="w-3 h-3" />
        {{ copied ? '已复制' : '复制' }}
      </button>
    </div>

    <!-- Code -->
    <pre class="p-3 text-sm overflow-x-auto"><code class="language-sql" v-html="highlightedSql" /></pre>
  </div>
</template>