// src/services/authService.ts
import axios from './api.ts';
import { LoginFormData } from '../types/auth.ts';
import { LoginResponse } from '../types/auth.ts';

// 登录API调用
export const login = async (data: LoginFormData): Promise<LoginResponse> => {
  // 模拟后端验证，实际项目中替换为真实API调用
  try {
    // 调用后端接口，获取完整响应
    const response = await axios.post('/login', data);
    return response.data;
  } catch (error) {
    // 错误处理（可根据实际需求扩展）
    console.error('登录请求失败:', error);
    throw error; // 抛出错误让调用方处理
  }

};

// 注销
export const logout = () => {
  localStorage.removeItem('user');
  localStorage.removeItem('token');
};

let cachedUser: any = null;
let lastUserStr: string | null = null;
// 获取当前用户
export const getCurrentUser = () => {
  const userStr = localStorage.getItem('user');
  
  // 只有当 localStorage 中的用户数据发生变化时，才重新解析并更新缓存
  if (userStr !== lastUserStr) {
    lastUserStr = userStr;
    cachedUser = userStr ? JSON.parse(userStr) : null;
  }
  
  return cachedUser;
};