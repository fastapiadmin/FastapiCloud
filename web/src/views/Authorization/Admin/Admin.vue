<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getUserList, deleteUser } from '@/api/user'
import type { UserTable, UserQuery } from '@/api/user/types'
import { ContentWrap } from '@/components/ContentWrap'
import SearchComponent from './components/SearchComponent.vue'
import AddComponent from './components/Add.vue'
import EditComponent from './components/Edit.vue'
import DetailComponent from './components/Detail.vue'

const router = useRouter()
const users = ref<UserTable[]>([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)

// 查询参数
const query = ref<UserQuery>({
  page: currentPage.value,
  size: pageSize.value
})

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
  // Element Plus pagination updates v-model bindings directly
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
  loadUsers()
}

// 跳转到创建用户页面
const handleCreate = () => {
  router.push('/users/create')
}

// 跳转到编辑用户页面
const handleEdit = (user: UserTable) => {
  router.push(`/users/${user.id}/edit`)
}

// 跳转到用户详情页面
const handleDetail = (user: UserTable) => {
  router.push(`/users/${user.id}`)
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
  <ContentWrap>
    <!-- 搜索和操作栏 -->
    <el-card>
      <SearchComponent v-model="query" @search="handleSearch" @reset="handleReset" />
      <div class="action-bar">
        <el-button type="primary" @click="handleCreate">创建用户</el-button>
      </div>
    </el-card>

    <el-card class="user-list-card" shadow="never" border="false" title="用户列表">
      <!-- 用户列表 -->
      <el-table v-loading="loading" :data="users" stripe border style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="name" label="昵称" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="scope">
            <el-tag type="success" v-if="scope.row.status"> ✅ 激活 </el-tag>
            <el-tag type="danger" v-else> ❌ 未激活 </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_time" label="创建时间" width="180" />
        <el-table-column prop="updated_time" label="更新时间" width="180" />
        <el-table-column label="操作" width="240">
          <template #default="scope">
            <el-button size="small" @click="handleDetail(scope.row)">详情</el-button>
            <el-button type="primary" size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button type="danger" size="small" @click="handleDelete(scope.row)">删除</el-button>
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

    <AddComponent />
    <EditComponent />
    <DetailComponent />
  </ContentWrap>
</template>

<style scoped></style>
