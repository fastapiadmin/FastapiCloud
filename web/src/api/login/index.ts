import request from '@/axios'
import type { UserType, UserLoginType } from './types'
import { useUserStoreWithOut } from '@/store/modules/user'

interface RoleParams {
  roleName: string
}

export const loginApi = (data: UserType): Promise<IResponse<UserType>> => {
  return request.post({ url: '/mock/user/login', data })
}

export const loginOutApi = (): Promise<IResponse> => {
  return request.get({ url: '/mock/user/loginOut' })
}

export const getUserListApi = ({ params }: AxiosConfig) => {
  return request.get<{
    code: string
    data: {
      list: UserType[]
      total: number
    }
  }>({ url: '/mock/user/list', params })
}

export const getAdminRoleApi = (
  params: RoleParams
): Promise<IResponse<AppCustomRouteRecordRaw[]>> => {
  return request.get({ url: '/mock/role/list', params })
}

export const getTestRoleApi = (params: RoleParams): Promise<IResponse<string[]>> => {
  return request.get({ url: '/mock/role/list2', params })
}

// 用户登录
export const login = async (data: UserLoginType): Promise<IResponse<LoginResponse>> => {
  try {
    const response = await request.post({
      url: '/api/login',
      data: data,
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
    // 保存token到user store
    const userStore = useUserStoreWithOut()
    if (response.data && response.data.access_token) {
      userStore.setToken(response.data.access_token)
    }
    return response
  } catch (error) {
    console.error('Login failed:', error)
    throw error
  }
}

// 用户注销
export const logout = async (): Promise<IResponse> => {
  try {
    const response = await request.post({ url: '/api/logout' })
    // 清除user store中的token
    const userStore = useUserStoreWithOut()
    userStore.logout()
    return response
  } catch (error) {
    console.error('Logout failed:', error)
    // 即使API调用失败，也清除本地token
    const userStore = useUserStoreWithOut()
    userStore.logout()
    throw error
  }
}
