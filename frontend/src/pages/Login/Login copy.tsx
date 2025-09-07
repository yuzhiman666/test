import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import LoginForm from '../../components/auth/LoginForm.tsx';
import WechatQrCode from '../../components/auth/WechatQrCode.tsx';
import Modal from '../../components/common/Modal/Modal.tsx';
import { login } from '../../services/authService.ts';
import { LoginFormData } from '../../types/auth.ts';

const Login = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [isModalOpen, setIsModalOpen] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('account');

  const handleLogin = async (data: LoginFormData) => {
    try {
      setIsLoading(true);
      setError('');
      
      const response = await login(data);
      
      // 存储用户信息
      localStorage.setItem('user', JSON.stringify(response.user));
      
      // 根据角色跳转到不同页面
      if (response.user.role === 'admin') {
        navigate('/admin-dashboard');
      } else {
        navigate('/');
      }
      
      setIsModalOpen(false);
    } catch (err) {
      console.error('Login error:', err);
      setError(t('login.loginFailed'));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Modal
      isOpen={isModalOpen}
      onClose={() => setIsModalOpen(false)}
      title={t('login.title')}
      className="login-modal"
    >
      {error && <ErrorMessage>{error}</ErrorMessage>}
      
      <TabSelector>
        <Tab
          isActive={activeTab === 'account'}
          onClick={() => setActiveTab('account')}
        >
          {t('login.accountLogin')}
        </Tab>
        <Tab
          isActive={activeTab === 'wechat'}
          onClick={() => setActiveTab('wechat')}
        >
          {t('login.wechatLogin')}
        </Tab>
      </TabSelector>
      
      {activeTab === 'account' ? (
        <LoginForm onSubmit={handleLogin} isLoading={isLoading} />
      ) : (
        <WechatQrCode />
      )}
      
      <RegisterSection>
        {t('login.noAccount')}
        <RegisterLink href="#">{t('login.register')}</RegisterLink>
      </RegisterSection>
    </Modal>
  );
};

// 样式组件
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

const Tab = styled.div<{ isActive: boolean }>`
  padding: 0.5rem 1rem;
  cursor: pointer;
  color: ${props => props.isActive ? '#3498db' : '#777'};
  border-bottom: 2px solid ${props => props.isActive ? '#3498db' : 'transparent'};
  font-weight: ${props => props.isActive ? '500' : 'normal'};
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