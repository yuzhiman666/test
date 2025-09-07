export type UserRole = 'customer' | 'admin';

export interface LoginFormData {
  identifier: string; // 手机号或邮箱
  password: string;
  role: UserRole;
}

export interface LoginResponse {
  token: string;
  user: {
    id: string;
    name: string;
    role: UserRole;
    avatar?: string;
  };
}

export interface ValidationError {
  field: string;
  message: string;
}