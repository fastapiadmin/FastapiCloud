<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { createUser } from '@/api/user'
import type { UserForm } from '@/api/user/types'

const router = useRouter()

const form = reactive<UserForm>({
  username: '',
  password: '',
  name: '',
  status: true,
  description: ''
})

const loading = ref(false)
const visible = ref(true)

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
  if (!form.password) {
    ElMessage.warning('请输入密码')
    return false
  }
  return true
}

// 处理表单提交
const handleSubmit = async () => {
  if (!validateForm()) return
  loading.value = true
  try {
    await createUser(form)
    ElMessage.success('用户创建成功')
    router.push('/users')
  } catch (error) {
    ElMessage.error('创建用户失败')
    console.error('Create user error:', error)
  } finally {
    loading.value = false
  }
}

// 取消操作
const handleCancel = () => {
  router.push('/users')
}
</script>

<template>
  <el-dialog title="创建用户" v-model:visible="visible" width="600px">
    <el-form v-loading="loading" :model="form" label-width="100px" class="user-form">
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
