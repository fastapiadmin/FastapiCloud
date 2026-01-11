import apiClient from '@/utils/request';
import type { BaseResponse, LoginRequest, LoginResponse, PageResponse } from '@/utils/types';

// 用户类型定义
export interface UserTable {
  id: number;
  username: string;
  name: string;
  status: boolean;
  description?: string | null;
  is_superuser: boolean;
  created_time: string;
  updated_time: string;
}

// 用户创建/更新请求类型定义
export interface UserForm {
  username: string;
  password?: string;
  name: string;
  status: boolean;
  description?: string | null;
}

// 用户查询参数类型定义
export interface UserQuery {
  page?: number;
  size?: number;
  name?: string;
}

// 重新导出类型
export type { LoginRequest, LoginResponse };

// 用户登录
export const login = async (params: LoginRequest): Promise<BaseResponse<LoginResponse>> => {
  const data = await apiClient.post('/login', new URLSearchParams({
    username: params.username,
    password: params.password,
  }), {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  });
  
  // 保存token到localStorage
  if (data.data && data.data.access_token) {
    localStorage.setItem('token', data.data.access_token);
  }
  
  return data;
};

// 用户注销
export const logout = async (): Promise<BaseResponse> => {
  try {
    const data = await apiClient.post('/logout');
    return data;
  } finally {
    // 无论API调用成功与否，都清除本地token
    localStorage.removeItem('token');
  }
};

// 获取用户列表
export const getUserList = async (params?: UserQuery): Promise<BaseResponse<PageResponse<UserTable>>> => {
  return apiClient.get('/users', { params });
};

// 创建用户
export const createUser = async (userData: UserForm): Promise<BaseResponse<UserTable>> => {
  return apiClient.post('/user', userData);
};

// 获取用户详情
export const getUserDetail = async (userId: number): Promise<BaseResponse<UserTable>> => {
  return apiClient.get(`/user/${userId}`);
};

// 更新用户
export const updateUser = async (userId: number, userData: UserForm): Promise<BaseResponse<UserTable>> => {
  return apiClient.put(`/user/${userId}`, userData);
};

// 删除用户
export const deleteUser = async (userId: number): Promise<BaseResponse> => {
  return apiClient.delete(`/user/${userId}`);
};

// 检查用户是否已登录
export const isAuthenticated = (): boolean => {
  return localStorage.getItem('token') !== null;
};

// 安全的JWT解析函数
const parseJWT = <T = any>(token: string): T | null => {
  try {
    const tokenParts = token.split('.');
    if (tokenParts.length !== 3 || !tokenParts[1]) {
      throw new Error('Invalid token format');
    }
    
    // 解码base64Url
    const decodeBase64Url = (str: string): string => {
      const base64 = str.replace(/-/g, '+').replace(/_/g, '/');
      const padding = '='.repeat((4 - (base64.length % 4)) % 4);
      return atob(base64 + padding);
    };
    
    const payload = decodeBase64Url(tokenParts[1] as string);
    return JSON.parse(payload) as T;
  } catch (error) {
    console.error('Failed to parse JWT:', error);
    return null;
  }
};

// 获取当前用户信息
export const getCurrentUser = async (): Promise<BaseResponse<UserTable | null>> => {
  const token = localStorage.getItem('token');
  
  if (token) {
    // 从token解析用户信息
    const userData = parseJWT<UserTable>(token);
    if (userData) {
      return { code: 0, msg: 'Success', data: userData };
    }
    
    // 如果解析失败，尝试从API获取
    try {
      return await apiClient.get('/user/profile');
    } catch (error) {
      console.error('Failed to get user profile:', error);
      return { code: 1, msg: 'Failed to get user profile', data: null };
    }
  }
  
  return { code: 1, msg: 'No token found', data: null };
};
