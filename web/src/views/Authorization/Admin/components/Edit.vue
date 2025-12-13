<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { updateUser, getUserDetail } from '@/api/user'
import type { UserForm } from '@/api/user/types'

const router = useRouter()
const route = useRoute()
const userId = computed(() => route.params.id as string)

const form = reactive<UserForm>({
  username: '',
  name: '',
  status: true,
  description: '',
  password: ''
})

const loading = ref(false)
const loadingUser = ref(false)
const visible = ref(true)

// 加载用户数据
const loadUser = async () => {
  loadingUser.value = true
  try {
    const response = await getUserDetail(Number(userId.value))
    const user = response.data
    // 填充表单数据
    form.username = user.username
    form.name = user.name
    form.status = user.status
    form.description = user.description || ''
  } catch (error) {
    ElMessage.error('加载用户数据失败')
    console.error('Load user error:', error)
    router.push('/users')
  } finally {
    loadingUser.value = false
  }
}

// 验证表单
const validateForm = (): boolean => {
  if (!form.username) {
    ElMessage.warning('请输入用户名')
    return false
  }
  if (!form.name) {
    ElMessage.warning('请输入昵称')
    return false
  }
  return true
}

// 处理表单提交
const handleSubmit = async () => {
  if (!validateForm()) return
  loading.value = true
  try {
    await updateUser(Number(userId.value), form)
    ElMessage.success('用户更新成功')
    router.push('/users')
  } catch (error) {
    ElMessage.error('更新用户失败')
    console.error('Update user error:', error)
  } finally {
    loading.value = false
  }
}

// 取消操作
const handleCancel = () => {
  router.push('/users')
}

// 组件挂载时加载用户数据
onMounted(() => {
  loadUser()
})
</script>

<template>
  <el-dialog title="编辑用户" v-model:visible="visible" width="500px">
    <el-form v-loading="loadingUser" :model="form" label-width="100px" class="user-form">
      <el-form-item label="用户名">
        <el-input v-model="form.username" placeholder="请输入用户名" />
      </el-form-item>
      <el-form-item label="昵称">
        <el-input v-model="form.name" placeholder="请输入昵称" />
      </el-form-item>
      <el-form-item label="密码">
        <el-input v-model="form.password" type="password" placeholder="请输入密码" />
      </el-form-item>
      <el-form-item label="是否激活">
        <el-switch v-model="form.status" />
      </el-form-item>
      <el-form-item label="备注">
        <el-input v-model="form.description" type="textarea" placeholder="请输入备注" :rows="3" />
      </el-form-item>
      <el-form-item>
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="loading">确定</el-button>
      </el-form-item>
    </el-form>
  </el-dialog>
</template>

<style scoped></style>
