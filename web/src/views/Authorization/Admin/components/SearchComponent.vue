<script setup lang="ts">
import { ref, watch } from 'vue'
import type { UserQuery } from '@/api/user/types'

// 定义组件属性
const props = defineProps<{
  modelValue: UserQuery
}>()

// 定义事件
const emit = defineEmits<{
  'update:modelValue': [value: UserQuery]
  search: []
  reset: []
}>()

// 本地查询参数
const query = ref<UserQuery>({ ...props.modelValue })

// 监听props变化，更新本地数据
watch(
  () => props.modelValue,
  (newValue) => {
    query.value = { ...newValue }
  },
  { deep: true }
)

// 搜索按钮点击
const handleSearch = () => {
  emit('search')
}

// 重置按钮点击
const handleReset = () => {
  query.value = {
    page: 1,
    size: 10
  }
  emit('update:modelValue', query.value)
  emit('reset')
}
</script>

<template>
  <div class="search-bar">
    <div class="search-form">
      <el-input
        v-model="query.username"
        placeholder="用户名"
        style="width: 200px; margin-right: 10px"
        @change="emit('update:modelValue', query)"
      />
      <el-input
        v-model="query.name"
        placeholder="姓名"
        style="width: 200px; margin-right: 10px"
        @change="emit('update:modelValue', query)"
      />
      <el-button type="primary" @click="handleSearch">搜索</el-button>
      <el-button @click="handleReset">重置</el-button>
    </div>
  </div>
</template>

<style scoped>
.search-bar {
  margin-bottom: 20px;
}

.search-form {
  display: flex;
  align-items: center;
}
</style>
