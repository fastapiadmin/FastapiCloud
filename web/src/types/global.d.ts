/// <reference types="vite/client" />

// 基础响应类型定义
declare interface BaseResponse<T = any> {
  code: number;
  msg: string;
  data: T;
}

// 登录请求类型定义
declare interface LoginRequest {
  username: string;
  password: string;
}

// 登录响应类型定义
declare interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

// 分页响应类型定义
declare interface PageResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

declare module 'element-plus/dist/locale/zh-cn.mjs';
declare module 'element-plus/dist/locale/zh-cn';

// 环境变量类型声明
declare interface ImportMetaEnv {
  readonly VITE_NODE_ENV: string;
  readonly VITE_API_BASE_PATH: string;
  readonly VITE_BASE_PATH: string;
  readonly VITE_DROP_DEBUGGER: boolean;
  readonly VITE_DROP_CONSOLE: boolean;
  readonly VITE_SOURCEMAP: boolean;
  readonly VITE_OUT_DIR: string;
  readonly VITE_APP_TITLE: string;
  readonly VITE_USE_BUNDLE_ANALYZER: boolean;
  readonly VITE_USE_ALL_ELEMENT_PLUS_STYLE: boolean;
  readonly VITE_USE_MOCK: boolean;
  readonly VITE_USE_CSS_SPLIT: boolean;
  readonly VITE_USE_ONLINE_ICON: boolean;
  readonly VITE_HIDE_GLOBAL_SETTING: boolean;
  readonly BASE_URL: string;
}

declare interface ImportMeta {
  readonly env: ImportMetaEnv;
}