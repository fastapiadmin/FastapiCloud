<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getUserDetail } from '@/api/user'
import type { UserTable } from '@/api/user/types'

const router = useRouter()
const route = useRoute()
const userId = computed(() => route.params.id as string)

const user = ref<UserTable | null>(null)
const loading = ref(false)
const visible = ref(true)

// 加载用户详情
const loadUserDetail = async () => {
  loading.value = true
  try {
    const response = await getUserDetail(Number(userId.value))
    user.value = response.data
  } catch (error) {
    ElMessage.error('加载用户详情失败')
    console.error('Load user detail error:', error)
    router.push('/users')
  } finally {
    loading.value = false
  }
}

// 返回用户列表
const handleBack = () => {
  router.push('/users')
}

// 跳转到编辑页面
const handleEdit = () => {
  router.push(`/users/${userId.value}/edit`)
}

// 组件挂载时加载用户详情
onMounted(() => {
  loadUserDetail()
})
</script>

<template>
  <el-dialog title="用户详情" v-model:visible="visible" width="600px">
    <el-descriptions :column="2" :data="user" :label-width="120">
      <el-descriptions-item label="ID" :span="2">
        {{ user?.id }}
      </el-descriptions-item>
      <el-descriptions-item label="名称" :span="2">
        {{ user?.name }}
      </el-descriptions-item>
      <el-descriptions-item label="用户名" :span="2">
        {{ user?.username }}
      </el-descriptions-item>
      <el-descriptions-item label="状态" :span="2">
        {{ user?.status ? '✅ 激活' : '❌ 未激活' }}
      </el-descriptions-item>
      <el-descriptions-item label="超级管理员" :span="2">
        {{ user?.is_superuser ? '✅ 是' : '❌ 否' }}
      </el-descriptions-item>
      <el-descriptions-item label="备注" :span="2">
        {{ user?.description || '无' }}
      </el-descriptions-item>
      <el-descriptions-item label="创建时间" :span="2">
        {{ user?.created_time }}
      </el-descriptions-item>
      <el-descriptions-item label="更新时间" :span="2">
        {{ user?.updated_time }}
      </el-descriptions-item>
    </el-descriptions>
    <template #footer>
      <el-button size="small" @click="handleBack">取消</el-button>
      <el-button type="primary" size="small" @click="handleEdit">确定</el-button>
    </template>
  </el-dialog>
</template>

<style scoped></style>
