import { ValidationError } from '../types/auth.ts';

export const validateLoginForm = (data: {
  identifier: string;
  password: string;
}): ValidationError[] => {
  const errors: ValidationError[] = [];

  // 验证标识符(手机号或邮箱)
  if (!data.identifier) {
    errors.push({ field: 'identifier', message: '请输入手机号或邮箱' });
  } else if (
    !/^1[3-9]\d{9}$/.test(data.identifier) &&
    !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.identifier)
  ) {
    errors.push({ field: 'identifier', message: '请输入有效的手机号或邮箱' });
  }

  // 验证密码
  if (!data.password) {
    errors.push({ field: 'password', message: '请输入密码' });
  } else if (data.password.length < 6) {
    errors.push({ field: 'password', message: '密码长度不能少于6位' });
  }

  return errors;
};