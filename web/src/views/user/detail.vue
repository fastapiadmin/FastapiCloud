<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElNotification } from 'element-plus'
import { DocumentCopy } from '@element-plus/icons-vue'
import { getUserDetail, type UserTable } from '@/api/user'

const route = useRoute()
const router = useRouter()

// 响应式数据
const userId = ref<number>(Number(route.params.id) || 0)
const userDetail = ref<UserTable | null>(null)
const loading = ref<boolean>(false)

// 方法
// 复制用户ID
const copyUserId = async () => {
    if (!userDetail.value?.id) return

    try {
        await navigator.clipboard.writeText(userDetail.value.id.toString())
        ElNotification.success({
            title: '成功',
            message: `用户ID ${userDetail.value.id} 已复制到剪贴板`,
            duration: 2000
        })
    } catch (error) {
        console.error('复制失败:', error)
        ElMessage.error('复制失败，请手动复制')
    }
}

// 加载用户详情
const loadUserDetail = async () => {
    if (!userId.value) {
        ElMessage.error('用户ID无效')
        return
    }

    loading.value = true
    try {
        const response = await getUserDetail(userId.value)
        userDetail.value = response.data
    } catch (error) {
        ElMessage.error('加载用户详情失败')
        console.error('Load user detail error:', error)
    } finally {
        loading.value = false
    }
}

// 返回用户列表
const handleBack = () => {
    router.push('/users')
}

// 监听路由变化
watch(
    () => route.params.id,
    (newId) => {
        userId.value = Number(newId) || 0
        loadUserDetail()
    },
    { immediate: true }
)
</script>

<template>
    <div class="user-detail-container">
        <el-card v-loading="loading">
            <!-- 页面头部 -->
            <el-page-header title="返回" @back="handleBack" content="用户详情" class="page-header">
                <!-- 详细信息描述列表 -->
                <el-descriptions v-if="userDetail" v-loading="loading" :column="2" border
                    :label-width="120" class="user-detail-descriptions">
                    <el-descriptions-item label="用户ID">
                        {{ userDetail.id }}
                        <el-button type="primary" link @click="copyUserId">
                            <el-icon>
                                <DocumentCopy />
                            </el-icon>
                            复制ID
                        </el-button>
                    </el-descriptions-item>
                    <el-descriptions-item label="用户名">
                        {{ userDetail.username }}
                    </el-descriptions-item>
                    <el-descriptions-item label="姓名">
                        {{ userDetail.name }}
                    </el-descriptions-item>
                    <el-descriptions-item label="超级管理员">
                        <el-switch v-model="userDetail.is_superuser" disabled active-text="是" inactive-text="否" />
                    </el-descriptions-item>
                    <el-descriptions-item label="状态">
                        <el-switch v-model="userDetail.status" disabled active-text="已激活" inactive-text="未激活" />
                    </el-descriptions-item>
                    <el-descriptions-item label="备注" :span="2">
                        <el-empty v-if="!userDetail.description" description="无备注信息" :image-size="40" />
                        <span v-else>{{ userDetail.description }}</span>
                    </el-descriptions-item>
                    <el-descriptions-item label="创建时间">
                        {{ userDetail.created_time }}
                    </el-descriptions-item>
                    <el-descriptions-item label="更新时间">
                        {{ userDetail.updated_time }}
                    </el-descriptions-item>
                </el-descriptions>
            </el-page-header>
        </el-card>
    </div>
</template>

<style scoped>
/* 基本布局 */
.user-detail-container {
    width: 100%;
}
</style>