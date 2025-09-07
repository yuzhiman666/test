import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import LoginForm from '../../components/auth/LoginForm.tsx';
import WechatQrCode from '../../components/auth/WechatQrCode.tsx';
import Modal from '../../components/common/Modal/Modal.tsx';
import { login } from '../../services/authService.ts';
import { LoginFormData } from '../../types/auth.ts';

// ========================== 1. 新增 Props 类型定义（解决 TypeScript 爆红核心）==========================
/**
 * Login 组件接收的 Props 类型
 * - isOpen: 控制登录模态框的显示/隐藏（由 Navbar 统一管理状态，避免状态冗余）
 * - onClose: 关闭模态框的回调（通知 Navbar 更新显示状态）
 */
interface LoginProps {
  isOpen: boolean;
  onClose: () => void;
}

// ========================== 2. 组件接收 Props 并指定类型 ==========================
// 明确组件类型为 React.FC<LoginProps>，声明接收 isOpen 和 onClose
const Login: React.FC<LoginProps> = ({ isOpen, onClose }) => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false); // 登录加载状态
  const [error, setError] = useState(''); // 登录错误提示
  const [activeTab, setActiveTab] = useState('account'); // 登录方式切换（账号/微信）

  // 登录逻辑（无修改，仅关闭模态框改为调用 props.onClose）
  const handleLogin = async (data: LoginFormData) => {
    try {
      setIsLoading(true);
      setError('');
      
      const response = await login(data);
      
      // 存储用户信息到 localStorage
      localStorage.setItem('user', JSON.stringify(response.user));
      
      // 根据用户角色跳转到对应页面
      if (response.user.role === 'admin') {
        navigate('/admin-dashboard');
      } else {
        navigate('/');
      }
      
      // 登录成功后关闭模态框（调用父组件传递的 onClose，通知 Navbar 更新状态）
      onClose();
    } catch (err) {
      console.error('Login error:', err);
      setError(t('login.loginFailed')); // 显示登录失败提示
    } finally {
      setIsLoading(false); // 无论成功失败，都停止加载状态
    }
  };

  return (
    // 3. 模态框状态由 props 控制（移除组件内部冗余的 isModalOpen 状态）
    <Modal
      isOpen={isOpen} // 由 Navbar 传递的 isOpen 控制显示/隐藏
      onClose={onClose} // 由 Navbar 传递的 onClose 控制关闭逻辑
      title={t('login.title')}
      className="login-modal"
    >
      {/* 登录错误提示 */}
      {error && <ErrorMessage>{error}</ErrorMessage>}
      
      {/* 登录方式切换标签（账号登录/微信登录） */}
      <TabSelector>
        <Tab
          $isActive={activeTab === 'account'}
          onClick={() => setActiveTab('account')}
        >
          {t('login.accountLogin')}
        </Tab>
        <Tab
          $isActive={activeTab === 'wechat'}
          onClick={() => setActiveTab('wechat')}
        >
          {t('login.wechatLogin')}
        </Tab>
      </TabSelector>
      
      {/* 根据选中的标签显示对应内容 */}
      {activeTab === 'account' ? (
        <LoginForm onSubmit={handleLogin} isLoading={isLoading} />
      ) : (
        <WechatQrCode />
      )}
      
      {/* 注册引导 */}
      <RegisterSection>
        {t('login.noAccount')}
        <RegisterLink href="#">{t('login.register')}</RegisterLink>
      </RegisterSection>
    </Modal>
  );
};

// 样式组件（无修改，保持原设计）
const ErrorMessage = styled.div`
  background-color: #fdecea;
  color: #e74c3c;
  padding: 0.8rem;
  border-radius: 4px;
  margin-bottom: 1rem;
  font-size: 0.9rem;
`;

const TabSelector = styled.div`
  display: flex;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid #eee;
`;

const Tab = styled.div<{ $isActive: boolean }>`
  padding: 0.5rem 1rem;
  cursor: pointer;
  color: ${props => props.$isActive ? '#3498db' : '#777'};
  border-bottom: 2px solid ${props => props.$isActive ? '#3498db' : 'transparent'};
  font-weight: ${props => props.$isActive ? '500' : 'normal'};
  transition: all 0.2s;
`;

const RegisterSection = styled.div`
  margin-top: 1.5rem;
  text-align: center;
  color: #777;
  font-size: 0.9rem;
`;

const RegisterLink = styled.a`
  color: #3498db;
  text-decoration: none;
  margin-left: 0.5rem;
  
  &:hover {
    text-decoration: underline;
  }
`;

export default Login;