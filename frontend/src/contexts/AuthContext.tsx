import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

// 定义用户信息类型
interface User {
  id: string;
  name: string;
  role: string; // 例如: "admin" 或 "user"
  token?: string;
}

// 定义上下文类型
interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (userData: User) => void;
  logout: () => void;
}

// 创建上下文（默认值为undefined，通过Provider提供实际值）
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// 提供上下文的Provider组件
export const AuthProvider: React.FC<{children: ReactNode}> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // 初始化：从本地存储读取用户信息
  useEffect(() => {
    try {
      const storedUser = localStorage.getItem('authUser');
      if (storedUser) {
        setUser(JSON.parse(storedUser));
      }
    } catch (error) {
      console.error('Failed to load user from storage:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  // 登录方法
  const login = (userData: User) => {
    setUser(userData);
    localStorage.setItem('authUser', JSON.stringify(userData));
  };

  // 登出方法
  const logout = () => {
    setUser(null);
    localStorage.removeItem('authUser');
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        loading,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

// 自定义Hook：简化组件中使用上下文的方式
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// 导出上下文（通常不需要直接使用，优先用useAuth Hook）
export default AuthContext;