<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ElIcon } from 'element-plus'
import { HomeFilled, UserFilled } from '@element-plus/icons-vue'

interface SidebarProps {
  collapsed: boolean
  activeMenu: string
  onCollapseChange: (collapsed: boolean) => void
}

const props = defineProps<SidebarProps>()
const router = useRouter()

// 菜单数据
const menuItems = [
  {
    path: '/dashboard',
    name: 'dashboard',
    label: '首页',
    icon: HomeFilled
  },
  {
    path: '/users',
    name: 'users',
    label: '用户管理',
    icon: UserFilled
  }
]

// 处理菜单点击
const handleMenuClick = (path: string) => {
  router.push(path)
}
</script>

<template>
  <el-aside :width="collapsed ? '64px' : '220px'" class="sidebar-container" :class="{ 'sidebar-collapsed': collapsed }">
    <div class="sidebar-header">
      <img src="@/assets/imgs/logo-dark.svg" alt="Logo" class="sidebar-logo"
        :class="{ 'sidebar-logo-collapsed': collapsed }">
      <h2 class="sidebar-title" v-if="!collapsed">管理系统</h2>
    </div>

    <!-- 侧边菜单 -->
    <div class="menu-container">
      <el-menu :default-active="activeMenu" class="el-menu-vertical" background-color="#001529" text-color="#fff"
        active-text-color="#409eff" unique-opened :collapse-transition="false">
        <el-menu-item v-for="item in menuItems" :key="item.path" :index="item.path" @click="handleMenuClick(item.path)">
          <el-icon :size="18">
            <component :is="item.icon" />
          </el-icon>
          <template #title>
            <span>{{ item.label }}</span>
          </template>
        </el-menu-item>
      </el-menu>
    </div>
  </el-aside>
</template>

<style scoped>
.sidebar-container {
  background-color: #001529;
  color: #fff;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15);
  z-index: 100;
  overflow: hidden;
  transition: width 0.3s ease;
  height: 100%;
}

.sidebar-header {
  display: flex;
  align-items: center;
  padding: 0 20px;
  height: 60px;
  border-bottom: 1px solid #002140;
}

.sidebar-logo {
  width: 90px;
  height: 40px;
  transition: all 0.3s ease;
}

.sidebar-logo-collapsed {
  margin-left: 12px;
}

.sidebar-title {
  font-size: 16px;
  font-weight: 600;
  margin-left: 12px;
  white-space: nowrap;
  transition: all 0.3s ease;
}

.sidebar-collapse-btn {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  background-color: #002140;
  color: #fff;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  z-index: 101;
}

.sidebar-collapse-btn:hover {
  background-color: #1890ff;
}

.menu-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px 0;
}

.el-menu-vertical {
  border-right: none;
  height: 100%;
}

.el-menu-item {
  margin: 0 12px;
  border-radius: 6px;
  margin-bottom: 8px;
  height: 40px;
  line-height: 40px;
}

.el-menu-item:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.el-menu-item.is-active {
  background-color: rgba(64, 158, 255, 0.2);
}

.el-menu-item__icon {
  margin-right: 8px;
  font-size: 18px;
}
</style>