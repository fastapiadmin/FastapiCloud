// 基础响应类型定义
export interface BaseResponse<T = any> {
  code: number;
  msg: string;
  data: T;
}


// 登录请求类型定义
export interface LoginRequest {
  username: string;
  password: string;
}


// 登录响应类型定义
export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}


// 分页响应类型定义
export interface PageResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}
