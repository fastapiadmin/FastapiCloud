// 用户创建/更新请求类型定义
export interface UserForm {
  username: string
  password: string
  name: string
  status: boolean
  description?: string | null
}

// 用户类型定义
export interface UserTable {
  id: number
  username: string
  name: string
  status: boolean
  description?: string | null
  is_superuser: boolean
  created_time: string
  updated_time: string
}

// 用户查询参数类型定义
export interface UserQuery {
  page?: number
  size?: number
  username?: string
  name?: string
}
