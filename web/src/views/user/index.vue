<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'

import { ElMessage, ElMessageBox } from 'element-plus'
import { Edit, Delete, User, Plus, Search, RefreshRight } from '@element-plus/icons-vue'
import { deleteUser, getUserList, getUserDetail, createUser, updateUser, type UserQuery, type UserTable, type UserForm } from '@/api/user'


const users = ref<UserTable[]>([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)

// 日期格式化函数
const formatDate = (dateString?: string): string => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  if (isNaN(date.getTime())) return 'N/A'
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}:${String(date.getSeconds()).padStart(2, '0')}`
}

// 路由实例
const router = useRouter()

// 查询参数
const query = ref<UserQuery>({
  page: currentPage.value,
  size: pageSize.value,
  username: '',
  name: ''
})

// 创建用户表单
const createForm = reactive<UserForm>({
  username: '',
  password: '',
  name: '',
  status: true,
  description: ''
})

const createLoading = ref(false)
const createVisible = ref(false)

// 验证创建表单
const validateCreateForm = (): boolean => {
  if (!createForm.username) {
    ElMessage.warning('请输入用户名')
    return false
  }
  if (createForm.username.length < 3 || createForm.username.length > 20) {
    ElMessage.warning('用户名长度应在3-20个字符之间')
    return false
  }
  if (!createForm.name) {
    ElMessage.warning('请输入昵称')
    return false
  }
  if (createForm.name.length < 2 || createForm.name.length > 20) {
    ElMessage.warning('昵称长度应在2-20个字符之间')
    return false
  }
  if (!createForm.password) {
    ElMessage.warning('请输入密码')
    return false
  }
  if (createForm.password.length < 6) {
    ElMessage.warning('密码长度不能少于6个字符')
    return false
  }
  return true
}

// 重置创建用户表单
const resetCreateForm = () => {
  Object.assign(createForm, {
    username: '',
    password: '',
    name: '',
    status: true,
    description: ''
  })
}

// 处理创建用户表单提交
const handleCreateSubmit = async () => {
  if (!validateCreateForm()) return
  createLoading.value = true
  try {
    await createUser(createForm)
    ElMessage.success('用户创建成功')
    createVisible.value = false
    loadUsers()
    resetCreateForm()
  } catch (error) {
    ElMessage.error('创建用户失败')
    console.error('Create user error:', error)
  } finally {
    createLoading.value = false
  }
}

// 处理创建用户取消
const handleCreateCancel = () => {
  createVisible.value = false
  resetCreateForm()
}

// 编辑用户表单
const editForm = reactive<UserForm>({
  username: '',
  name: '',
  status: true,
  description: '',
  password: ''
})

const editLoading = ref(false)
const editLoadingUser = ref(false)
const editVisible = ref(false)
let currentEditUserId = ref<number>(0)

// 加载用户数据用于编辑
const loadUserForEdit = async (userId: number) => {
  editLoadingUser.value = true
  try {
    const response = await getUserDetail(userId)
    const user = response.data
    // 填充表单数据
    editForm.username = user.username
    editForm.name = user.name
    editForm.status = user.status
    editForm.description = user.description || ''
    editForm.password = ''
    currentEditUserId.value = userId
  } catch (error) {
    ElMessage.error('加载用户数据失败')
    console.error('Load user error:', error)
  } finally {
    editLoadingUser.value = false
  }
}

// 验证编辑表单
const validateEditForm = (): boolean => {
  if (!editForm.username) {
    ElMessage.warning('请输入用户名')
    return false
  }
  if (editForm.username.length < 3 || editForm.username.length > 20) {
    ElMessage.warning('用户名长度应在3-20个字符之间')
    return false
  }
  if (!editForm.name) {
    ElMessage.warning('请输入昵称')
    return false
  }
  if (editForm.name.length < 2 || editForm.name.length > 20) {
    ElMessage.warning('昵称长度应在2-20个字符之间')
    return false
  }
  // 密码可选，但如果提供了密码，则验证长度
  if (editForm.password && editForm.password.length < 6) {
    ElMessage.warning('密码长度不能少于6个字符')
    return false
  }
  return true
}

// 重置编辑用户表单
const resetEditForm = () => {
  Object.assign(editForm, {
    username: '',
    name: '',
    status: true,
    description: '',
    password: ''
  })
  currentEditUserId.value = 0
}

// 处理编辑用户表单提交
const handleEditSubmit = async () => {
  if (!validateEditForm()) return
  editLoading.value = true
  try {
    await updateUser(currentEditUserId.value, editForm)
    ElMessage.success('用户更新成功')
    editVisible.value = false
    loadUsers()
    resetEditForm()
  } catch (error) {
    ElMessage.error('更新用户失败')
    console.error('Update user error:', error)
  } finally {
    editLoading.value = false
  }
}

// 处理编辑用户取消
const handleEditCancel = () => {
  editVisible.value = false
  resetEditForm()
}

// 查看用户详情
const handleDetail = async (user: UserTable) => {
  router.push(`/users/${user.id}`)
}

// 加载用户列表
const loadUsers = async () => {
  loading.value = true
  try {
    query.value.page = currentPage.value
    query.value.size = pageSize.value
    const response = await getUserList(query.value)
    users.value = response.data.items
    total.value = response.data.total
  } catch (error) {
    ElMessage.error('加载用户列表失败')
    console.error('加载用户列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 分页变更
const handlePageChange = () => {
  loadUsers()
}

// 搜索用户
const handleSearch = () => {
  currentPage.value = 1
  loadUsers()
}

// 重置搜索
const handleReset = () => {
  currentPage.value = 1
  // 重置查询参数
  Object.assign(query.value, {
    username: '',
    name: ''
  })
  loadUsers()
}

// 显示创建用户对话框
const handleCreate = () => {
  createVisible.value = true
}

// 显示编辑用户对话框并加载用户数据
const handleEdit = async (user: UserTable) => {
  await loadUserForEdit(user.id)
  editVisible.value = true
}

// 删除用户
const handleDelete = async (user: UserTable) => {
  try {
    await ElMessageBox.confirm(`确定要删除用户 ${user.username} 吗？`, '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteUser(user.id)
    ElMessage.success('删除成功')
    loadUsers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
      console.error('Delete user error:', error)
    }
  }
}

// 组件挂载时加载用户列表
onMounted(() => {
  loadUsers()
})
</script>

<template>
  <div class="user-container">
    <el-card class="user-list-card" shadow="hover" border="true" title="用户列表">
      <template #header>
        <div class="card-header">
          <!-- 搜索栏 -->
          <el-form class="search-bar" :model="query" inline>
            <el-input
              v-model="query.username"
              placeholder="用户名"
              style="width: 200px; margin-right: 10px"
            />
            <el-input
              v-model="query.name"
              placeholder="姓名"
              style="width: 200px; margin-right: 10px"
            />
            <el-button type="primary" @click="handleSearch">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
            <el-button @click="handleReset">
              <el-icon><RefreshRight /></el-icon>
              重置
            </el-button>
          </el-form>

          <!-- 操作栏 -->
          <div class="action-bar">
            <el-button type="primary" @click="handleCreate">
              <el-icon><Plus /></el-icon>
              创建用户
            </el-button>
          </div>
        </div>
      </template>
      
      <!-- 用户列表 -->
      <el-table v-loading="loading" :data="users" stripe border style="width: 100%" :row-style="{transition: 'background-color 0.2s'}">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="name" label="昵称" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="scope">
            <el-tag type="success" v-if="scope.row.status"> 激活 </el-tag>
            <el-tag type="danger" v-else> 未激活 </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_time" label="创建时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.created_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="updated_time" label="更新时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.updated_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280">
          <template #default="scope">
            <el-button size="small" @click="handleDetail(scope.row)" type="info">
              <el-icon><User /></el-icon>
              详情
            </el-button>
            <el-button type="primary" size="small" @click="handleEdit(scope.row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(scope.row)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <template #footer>
        <!-- 分页 -->
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[5, 10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handlePageChange"
          @current-change="handlePageChange"
        />
      </template>
    </el-card>

    <!-- 创建用户对话框 -->
    <el-dialog title="创建用户" v-model="createVisible">
      <el-form v-loading="createLoading" :model="createForm" label-width="100px" class="user-form">
        <el-form-item label="用户名">
          <el-input v-model="createForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="昵称">
          <el-input v-model="createForm.name" placeholder="请输入昵称" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="createForm.password" type="password" placeholder="请输入密码" />
        </el-form-item>
        <el-form-item label="是否激活">
          <el-switch v-model="createForm.status" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="createForm.description" type="textarea" placeholder="请输入备注" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="handleCreateCancel">取消</el-button>
          <el-button type="primary" @click="handleCreateSubmit" :loading="createLoading">确定</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 编辑用户对话框 -->
    <el-dialog title="编辑用户" v-model="editVisible">
      <el-form v-loading="editLoadingUser" :model="editForm" label-width="100px" class="user-form">
        <el-form-item label="用户名">
          <el-input v-model="editForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="昵称">
          <el-input v-model="editForm.name" placeholder="请输入昵称" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="editForm.password" type="password" placeholder="请输入密码" />
        </el-form-item>
        <el-form-item label="是否激活">
          <el-switch v-model="editForm.status" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="editForm.description" type="textarea" placeholder="请输入备注" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="handleEditCancel">取消</el-button>
          <el-button type="primary" @click="handleEditSubmit" :loading="editLoading">确定</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.user-container {
  background-color: #f5f7fa;
}

.user-list-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.user-list-card:hover {
  box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
}

.search-bar {
  margin-bottom: 0;
  display: flex;
  align-items: center;
}

.action-bar {
  margin-top: 0;
}

.user-form {
  max-height: 60vh;
  overflow-y: auto;
}

/* 美化表格样式 */
:deep(.el-table__row) {
  transition: background-color 0.2s ease;
}

:deep(.el-table__row:hover) {
  background-color: #f0f5ff !important;
}

:deep(.el-table-column--selection) {
  width: 60px;
}

:deep(.el-pagination) {
  margin-top: 20px;
  text-align: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-bar {
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .action-bar {
    text-align: center;
  }
}
</style>
