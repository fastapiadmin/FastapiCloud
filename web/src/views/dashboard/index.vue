<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, Edit, RefreshRight, User, Monitor, Clock } from '@element-plus/icons-vue'
import type { UserTable } from '@/api/user'

const router = useRouter()

// 响应式数据
const userList = ref<UserTable[]>([])
const loading = ref(false)
const currentUser = ref<UserTable | null>(null)
const totalUsers = ref(0)
const activeUsers = ref(0)

// 模拟统计数据
const dashboardStats = ref({
  totalUsers: 156,
  activeUsers: 128,
  newUsers: 5,
  pendingTasks: 2
})

// 模拟用户列表数据
const mockUserList: UserTable[] = [
  { id: 1, username: 'zhangsan', name: '张三', status: true, description: '普通用户', is_superuser: false, created_time: '2026-01-01 10:00:00', updated_time: '2026-01-01 10:00:00' },
  { id: 2, username: 'lisi', name: '李四', status: true, description: '普通用户', is_superuser: false, created_time: '2026-01-02 11:00:00', updated_time: '2026-01-02 11:00:00' },
  { id: 3, username: 'wangwu', name: '王五', status: false, description: '已禁用用户', is_superuser: false, created_time: '2026-01-03 12:00:00', updated_time: '2026-01-03 12:00:00' },
  { id: 4, username: 'zhaoliu', name: '赵六', status: true, description: '普通用户', is_superuser: false, created_time: '2026-01-04 13:00:00', updated_time: '2026-01-04 13:00:00' },
  { id: 5, username: 'qianqi', name: '钱七', status: true, description: '普通用户', is_superuser: false, created_time: '2026-01-05 14:00:00', updated_time: '2026-01-05 14:00:00' }
]

// 模拟当前用户
const mockCurrentUser: UserTable = {
  id: 1, username: 'admin', name: '管理员', status: true, description: '系统管理员', is_superuser: true, created_time: '2026-01-01 10:00:00', updated_time: '2026-01-01 10:00:00'
}

// 模拟用户活动
const userActivity = ref([
  { id: 1, user: '张三', action: '创建了新用户', time: '2026-01-11 10:30:25' },
  { id: 2, user: '李四', action: '更新了用户信息', time: '2026-01-11 09:15:42' },
  { id: 3, user: '管理员', action: '删除了无效用户', time: '2026-01-11 08:45:18' },
  { id: 4, user: '王五', action: '激活了新用户', time: '2026-01-11 07:30:55' },
  { id: 5, user: '赵六', action: '查看了用户详情', time: '2026-01-10 18:20:33' }
])

// 加载用户数据 (使用模拟数据)
const loadUserList = () => {
  loading.value = true
  // 使用 setTimeout 模拟异步请求
  setTimeout(() => {
    try {
      userList.value = mockUserList
      totalUsers.value = dashboardStats.value.totalUsers
      activeUsers.value = dashboardStats.value.activeUsers
    } catch (error) {
      console.error('获取用户列表错误:', error)
      ElMessage.error('获取用户列表失败')
    } finally {
      loading.value = false
    }
  }, 500)
}

// 获取当前用户信息 (使用模拟数据)
const loadCurrentUser = () => {
  // 直接使用模拟数据
  currentUser.value = mockCurrentUser
}

// 页面挂载时加载数据
onMounted(() => {
  loadUserList()
  loadCurrentUser()
})

// 快捷操作
const handleQuickAction = (action: string) => {
  switch (action) {
    case 'addUser':
      router.push('/users/create')
      break
    case 'userList':
      router.push('/users')
      break
    case 'refresh':
      loadUserList()
      ElMessage.success('数据已刷新')
      break
    case 'settings':
      ElMessage.info('设置功能开发中')
      break
  }
}
</script>

<template>
  <div class="dashboard-container">
    <!-- 页面头部 -->
    <div class="dashboard-header">
      <div class="header-left">
        <p class="welcome-message">
          <span>欢迎回来，</span>
          <span class="username">{{ currentUser?.name || '管理员' }}</span>
        </p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="handleQuickAction('refresh')" :icon="RefreshRight" circle>
        </el-button>
      </div>
    </div>

    <!-- 统计卡片区域 -->
    <div class="stats-cards">
      <el-card shadow="hover" class="stat-card">
        <template #header>
          <div class="card-header">
            <span>用户总数</span>
            <el-icon
              :size="23"
              color="#409eff"
            >
              <User />
            </el-icon>
          </div>
        </template>
        <div class="card-content">
          <el-statistic
            :value="dashboardStats.totalUsers"
            :precision="0"
            value-style="color: #409eff; font-size: 2.5rem; font-weight: 700"
          />
          <div class="stat-description">系统中注册的用户总数</div>
        </div>
      </el-card>

      <el-card shadow="hover" class="stat-card">
        <template #header>
          <div class="card-header">
            <span>活跃用户</span>
            <el-icon
              :size="23"
              color="#67c23a"
            >
              <Monitor />
            </el-icon>
          </div>
        </template>
        <div class="card-content">
          <el-statistic
            :value="dashboardStats.activeUsers"
            :precision="0"
            value-style="color: #67c23a; font-size: 2.5rem; font-weight: 700"
          />
          <div class="stat-description">当前处于激活状态的用户</div>
        </div>
      </el-card>

      <el-card shadow="hover" class="stat-card">
        <template #header>
          <div class="card-header">
            <span>新增用户</span>
            <el-icon
              :size="23"
              color="#e6a23c"
            >
              <Plus />
            </el-icon>
          </div>
        </template>
        <div class="card-content">
          <el-statistic
            :value="dashboardStats.newUsers"
            :precision="0"
            value-style="color: #e6a23c; font-size: 2.5rem; font-weight: 700"
          />
          <div class="stat-description">最近7天新增的用户</div>
        </div>
      </el-card>

      <el-card shadow="hover" class="stat-card">
        <template #header>
          <div class="card-header">
            <span>待处理任务</span>
            <el-icon
              :size="23"
              color="#f56c6c"
            >
              <Clock />
            </el-icon>
          </div>
        </template>
        <div class="card-content">
          <el-statistic
            :value="dashboardStats.pendingTasks"
            :precision="0"
            value-style="color: #f56c6c; font-size: 2.5rem; font-weight: 700"
          />
          <div class="stat-description">需要处理的任务数量</div>
        </div>
      </el-card>
    </div>

    <!-- 内容区域 -->
    <div class="dashboard-content">
      <!-- 用户活动区域 -->
      <el-card shadow="hover" class="content-card">
        <template #header>
          <div class="card-header">
            <span>用户活动</span>
            <el-button size="small" link @click="router.push('/users')">查看更多</el-button>
          </div>
        </template>
        <el-timeline>
          <el-timeline-item
            v-for="activity in userActivity"
            :key="activity.id"
            :timestamp="activity.time"
          >
            <div class="timeline-content">
              <span class="activity-user">{{ activity.user }}</span>
              <span class="activity-action">{{ activity.action }}</span>
            </div>
          </el-timeline-item>
        </el-timeline>
      </el-card>

      <!-- 快捷入口区域 -->
      <el-card shadow="hover" class="content-card">
        <template #header>
          <div class="card-header">
            <span>快捷入口</span>
            <span>常用功能快速访问</span>
          </div>
        </template>
        <div class="quick-actions">
          <el-button 
            type="primary" 
            size="large" 
            :icon="Plus" 
            @click="handleQuickAction('addUser')"
            class="quick-action-button"
          >
            添加用户
          </el-button>
          <el-button 
            type="success" 
            size="large" 
            :icon="User" 
            @click="handleQuickAction('userList')"
            class="quick-action-button"
          >
            用户管理
          </el-button>
          <el-button 
            type="warning" 
            size="large" 
            :icon="Edit" 
            @click="handleQuickAction('settings')"
            class="quick-action-button"
          >
            系统设置
          </el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.dashboard-container {
  width: 100%;
}

/* 页面头部 */
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e4e7ed;
}

.header-left .dashboard-title {
  font-size: 2rem;
  margin: 0 0 8px 0;
  color: #303133;
}

.header-left .welcome-message {
  margin: 0;
  color: #606266;
  font-size: 1rem;
}

.header-left .username {
  font-weight: 600;
  color: #409eff;
}

/* 统计卡片区域 */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header span {
  font-weight: 600;
  font-size: 1rem;
  color: #303133;
}

.card-icon {
  color: #c0c4cc;
}

.stat-description {
  margin-top: 8px;
  color: #909399;
  font-size: 0.9rem;
}

/* 内容区域 */
.dashboard-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
}
</style>