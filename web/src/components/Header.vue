<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Expand, Fold, Remove, User } from '@element-plus/icons-vue'
import { logout } from '@/api/user'

interface HeaderProps {
  collapsed: boolean
  onCollapseChange: (collapsed: boolean) => void
}

const props = defineProps<HeaderProps>()
const router = useRouter()
const route = useRoute()

// 面包屑导航项
const breadcrumbItems = computed(() => {
  const items = []
  const matched = route.matched

  // 过滤掉根路径
  for (const record of matched) {
    if (record.path === '/') continue

    let title = ''
    // 根据路由名称设置标题
    switch (record.path) {
      case '/dashboard':
        title = '仪表盘'
        break
      case '/users':
        title = '用户管理'
        break
      case '/users/:id':
        title = '用户详情'
        break
      default:
        title = record.meta?.title as string || (record.name as string) || '未知'
    }

    items.push({
      path: record.path,
      title
    })
  }

  return items
})

// 处理退出登录
const handleLogout = async () => {
  try {
    await logout()
    ElMessage.success('退出登录成功')
    router.push('/login')
  } catch (error) {
    ElMessage.error('退出登录失败')
    console.error('Logout error:', error)
  }
}
</script>

<template>
  <el-header class="header-container">
    <div class="header-left">
      <el-button link @click="onCollapseChange(!collapsed)" class="header-collapse-btn">
        <el-icon>
          <Expand v-if="collapsed" />
          <Fold v-else />
        </el-icon>
      </el-button>

      <!-- 面包屑导航 -->
      <el-breadcrumb separator-class="el-icon-arrow-right" class="header-breadcrumb">
        <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item 
          v-for="(item, index) in breadcrumbItems" :key="index" :to="item.path">
          {{ item.title }}
        </el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <div class="header-right">
      <el-dropdown>
        <span class="user-info">
          <el-avatar :size="32" class="user-avatar">
            <User />
          </el-avatar>
          <span class="user-name" v-if="!collapsed">管理员</span>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item divided>
              <el-icon>
                <Remove />
              </el-icon>
              <span @click="handleLogout">退出登录</span>
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </el-header>
</template>

<style scoped>
.header-container {
  height: 60px !important;
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.09);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  z-index: 99;
  margin: 0 !important;
}

.header-left {
  display: flex;
  align-items: center;
  flex: 1;
}

.header-collapse-btn {
  font-size: 20px;
  color: #666;
}

.header-search-btn {
  margin-right: 20px;
  font-size: 20px;
  color: #666;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background-color 0.3s ease;
}

.user-info:hover {
  background-color: #f5f7fa;
}

.user-avatar {
  margin-right: 8px;
  background-color: #1890ff;
}

.user-name {
  font-size: 14px;
  color: #333;
  white-space: nowrap;
}

/* Header面包屑样式 */
.header-breadcrumb {
  margin-left: 20px;
  font-size: 14px;
}

.header-breadcrumb .el-breadcrumb__inner {
  color: #606266;
}

.header-breadcrumb .el-breadcrumb__inner.is-link {
  color: #409eff;
}

.header-breadcrumb .el-breadcrumb__inner.is-link:hover {
  color: #66b1ff;
}
</style>