<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import Sidebar from '@/components/Sider.vue'
import Header from '@/components/Header.vue'
import Footer from '@/components/Footer.vue'

const route = useRoute()
const collapsed = ref(false)

// 当前激活的菜单项
const activeMenu = computed(() => route.path)

// 处理侧边栏折叠状态变化
const handleCollapseChange = (value: boolean) => {
    collapsed.value = value
}
</script>

<template>
    <el-container class="layout-container">
        <!-- 侧边栏 -->
        <Sidebar :collapsed="collapsed" :active-menu="activeMenu" :on-collapse-change="handleCollapseChange" />

        <!-- 主内容区 -->
        <el-container class="main-container" direction="vertical">
            <!-- 顶部导航 -->
            <Header :collapsed="collapsed" :on-collapse-change="handleCollapseChange" />

            <!-- 内容区域 -->
            <el-main class="content-container">
                <router-view v-slot="{ Component }">
                    <transition name="fade-transform" mode="out-in">
                        <component :is="Component" />
                    </transition>
                </router-view>
            </el-main>

            <!-- 底栏 -->
            <Footer />
        </el-container>
    </el-container>
</template>

<style scoped>
.layout-container {
    height: 100vh;
    overflow: hidden;
}

/* 主内容区样式 */
.main-container {
    overflow: hidden;
    display: flex;
    flex-direction: column;
}

/* 内容区域样式 */
.content-container {
    padding: 20px;
    overflow-y: auto;
    background-color: #f5f7fa;
    margin: 0 !important;
    flex: 1;
}

/* 过渡动画 */
.fade-transform-enter-active,
.fade-transform-leave-active {
    transition: all 0.3s ease;
}

.fade-transform-enter-from,
.fade-transform-leave-to {
    opacity: 0;
    transform: translateX(30px);
}
</style>