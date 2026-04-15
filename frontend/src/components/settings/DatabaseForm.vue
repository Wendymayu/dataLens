<script setup lang="ts">
import { ref } from 'vue'
import { Icon } from '@iconify/vue'
import type { DatabaseCreateRequest } from '@/types/database'

const emit = defineEmits<{
  submit: [data: DatabaseCreateRequest]
  cancel: []
}>()

const form = ref<DatabaseCreateRequest>({
  name: '',
  host: 'localhost',
  port: 3306,
  user: '',
  password: '',
  database: ''
})

const loading = ref(false)

async function handleSubmit() {
  if (!form.value.name || !form.value.user || !form.value.database) {
    return
  }

  loading.value = true
  emit('submit', { ...form.value })
  loading.value = false
}
</script>

<template>
  <div class="bg-gray-50 rounded-lg p-4 mb-4">
    <h3 class="font-medium text-gray-800 mb-3">添加新数据库</h3>

    <div class="space-y-3">
      <div>
        <label class="text-xs text-gray-500 mb-1 block">连接名称 *</label>
        <input
          v-model="form.name"
          type="text"
          placeholder="例如: ecommerce"
          class="w-full text-sm border rounded px-2 py-1"
        />
      </div>

      <div class="grid grid-cols-2 gap-2">
        <div>
          <label class="text-xs text-gray-500 mb-1 block">主机</label>
          <input
            v-model="form.host"
            type="text"
            class="w-full text-sm border rounded px-2 py-1"
          />
        </div>
        <div>
          <label class="text-xs text-gray-500 mb-1 block">端口</label>
          <input
            v-model="form.port"
            type="number"
            class="w-full text-sm border rounded px-2 py-1"
          />
        </div>
      </div>

      <div>
        <label class="text-xs text-gray-500 mb-1 block">用户名 *</label>
        <input
          v-model="form.user"
          type="text"
          placeholder="root"
          class="w-full text-sm border rounded px-2 py-1"
        />
      </div>

      <div>
        <label class="text-xs text-gray-500 mb-1 block">密码</label>
        <input
          v-model="form.password"
          type="password"
          class="w-full text-sm border rounded px-2 py-1"
        />
      </div>

      <div>
        <label class="text-xs text-gray-500 mb-1 block">数据库名 *</label>
        <input
          v-model="form.database"
          type="text"
          placeholder="ecommerce"
          class="w-full text-sm border rounded px-2 py-1"
        />
      </div>

      <div class="flex gap-2 pt-2">
        <button
          @click="handleSubmit"
          :disabled="loading"
          class="flex-1 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
        >
          添加
        </button>
        <button
          @click="emit('cancel')"
          class="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
        >
          取消
        </button>
      </div>
    </div>
  </div>
</template>