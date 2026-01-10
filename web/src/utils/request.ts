import axios from 'axios';
import type { AxiosRequestConfig, AxiosResponse } from 'axios';
import type { BaseResponse } from './types';

// 创建Axios实例
const axiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_PATH || 'http://localhost:8000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 创建自定义ApiClient接口
export interface ApiClient {
  get<T = any>(url: string, config?: AxiosRequestConfig): Promise<BaseResponse<T>>;
  post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<BaseResponse<T>>;
  put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<BaseResponse<T>>;
  delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<BaseResponse<T>>;
}

// 请求拦截器
axiosInstance.interceptors.request.use(
  (config) => {
    // 从localStorage获取token
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
axiosInstance.interceptors.response.use(
  (response: AxiosResponse<BaseResponse<any>>) => {
    return response;
  },
  (error) => {
    // 统一错误处理
    let errorMessage = '请求失败，请稍后重试';
    
    if (error.response) {
      // 服务器返回错误状态码
      const { status, data } = error.response;
      
      switch (status) {
        case 400:
          errorMessage = data.msg || '请求参数错误';
          break;
        case 401:
          errorMessage = data.msg || '未授权，请重新登录';
          // 清除token并跳转到登录页
          localStorage.removeItem('token');
          window.location.href = '/login';
          break;
        case 403:
          errorMessage = data.msg || '没有权限访问该资源';
          break;
        case 404:
          errorMessage = data.msg || '请求的资源不存在';
          break;
        case 500:
          errorMessage = data.msg || '服务器内部错误';
          break;
        default:
          errorMessage = data.msg || `请求失败 (${status})`;
      }
    } else if (error.request) {
      // 请求已发送但没有收到响应
      errorMessage = '网络错误，请检查网络连接';
    } else {
      // 请求配置错误
      errorMessage = error.message;
    }
    
    console.error('API Error:', errorMessage);
    return Promise.reject(new Error(errorMessage));
  }
);

// 创建并导出符合ApiClient接口的apiClient实例
const apiClient: ApiClient = {
  get: async <T = any>(url: string, config?: AxiosRequestConfig): Promise<BaseResponse<T>> => {
    const response = await axiosInstance.get<BaseResponse<T>>(url, config);
    return response.data;
  },
  post: async <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<BaseResponse<T>> => {
    const response = await axiosInstance.post<BaseResponse<T>>(url, data, config);
    return response.data;
  },
  put: async <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<BaseResponse<T>> => {
    const response = await axiosInstance.put<BaseResponse<T>>(url, data, config);
    return response.data;
  },
  delete: async <T = any>(url: string, config?: AxiosRequestConfig): Promise<BaseResponse<T>> => {
    const response = await axiosInstance.delete<BaseResponse<T>>(url, config);
    return response.data;
  },
};

export default apiClient;
