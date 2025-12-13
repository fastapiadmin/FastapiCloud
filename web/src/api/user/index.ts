import request from '@/axios'
import type { UserForm, UserTable, UserQuery } from './types'

// 获取用户列表
export const getUserList = async (
  params?: UserQuery
): Promise<IResponse<PageResponse<UserTable>>> => {
  return await request.get({
    url: '/api/users',
    params
  })
}

// 获取用户详情
export const getUserDetail = async (userId: number): Promise<IResponse<UserTable>> => {
  return await request.get({
    url: `/api/user/${userId}`
  })
}

// 创建用户
export const createUser = async (userData: UserForm): Promise<IResponse<UserTable>> => {
  return await request.post({
    url: '/api/user',
    data: userData
  })
}

// 更新用户
export const updateUser = async (
  userId: number,
  userData: UserForm
): Promise<IResponse<UserTable>> => {
  return await request.put({
    url: `/api/user/${userId}`,
    data: userData
  })
}

// 删除用户
export const deleteUser = async (userId: number): Promise<IResponse> => {
  return await request.delete({
    url: `/api/user/${userId}`
  })
}
