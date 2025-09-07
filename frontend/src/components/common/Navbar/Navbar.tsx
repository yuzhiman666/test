import { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import Login from '../../../pages/Login/Login';
import { getCurrentUser, logout } from '../../../services/authService';

// ========================== 样式组件定义 ==========================
const NavContainer = styled.nav`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 5%;
  background-color: #ffffff;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
`;

const NavContent = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
`;

const Logo = styled(Link)`
  font-size: 1.5rem;
  font-weight: bold;
  color: #2c3e50;
  text-decoration: none;
  transition: color 0.3s;

  &:hover {
    color: #3498db;
  }
`;

const NavLinks = styled.div`
  display: flex;
  gap: 2rem;

  a {
    text-decoration: none;
    color: #3498db;
    font-weight: 500;
    transition: color 0.3s;

    &:hover {
      color: #2980b9;
    }
  }
`;

const RightSection = styled.div`
  display: flex;
  align-items: center;
`;

const LanguageSelector = styled.div`
  display: flex;
  gap: 0.5rem;
  margin-right: 1.5rem;
`;

const LanguageButton = styled.button<{ $isActive: boolean }>`
  background: none;
  border: none;
  cursor: pointer;
  color: ${(props) => (props.$isActive ? '#3498db' : '#34495e')};
  font-weight: 500;
  padding: 0.3rem 0.6rem;
  border-radius: 4px;
  transition: all 0.3s;

  &:hover {
    background-color: #f5f5f5;
  }
`;

const LoginButton = styled.button`
  padding: 0.5rem 1rem;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.3s;

  &:hover {
    background-color: #2980b9;
  }

  &:active {
    transform: scale(0.98);
  }
`;

// 用户菜单相关样式
const UserMenu = styled.div`
  position: relative;
  display: inline-block;
`;

const UserAvatar = styled.div`
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: #3498db;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.3s;

  &:hover {
    background-color: #2980b9;
  }
`;

const DropdownMenu = styled.div`
  position: absolute;
  top: 45px;
  right: 0;
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
  width: 180px;
  z-index: 1001;
  overflow: hidden;
`;

const DropdownItem = styled.button<{ $isButton?: boolean }>`
  padding: 0.8rem 1.2rem;
  color: #333;
  cursor: pointer;
  transition: background-color 0.2s;
  border: none;
  background: none;
  width: 100%;
  text-align: left;
  font-size: 0.9rem;

  &:hover {
    background-color: #f5f5f5;
  }

  &.logout {
    color: #e74c3c;
    &:hover {
      background-color: #fdecea;
    }
  }

  &:disabled {
    opacity: 0.7;
    cursor: default;
    &:hover {
      background-color: transparent;
    }
  }
`;

const DropdownLink = styled(Link)`
  display: block;
  padding: 0.8rem 1.2rem;
  color: #333;
  text-decoration: none;
  transition: background-color 0.2s;
  font-size: 0.9rem;

  &:hover {
    background-color: #f5f5f5;
  }
`;

// ========================== 组件逻辑 ==========================
const Navbar = () => {
  const { i18n, t } = useTranslation();
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false); // 控制下拉菜单显示/隐藏
  const currentUser = getCurrentUser();
  const currentLng = i18n.language;
  const dropdownRef = useRef<HTMLDivElement>(null); // 用于检测点击外部关闭下拉菜单

  // 切换语言逻辑
  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
  };

  // 注销逻辑
  const handleLogout = () => {
    logout();
    setShowDropdown(false); // 注销后关闭下拉菜单
    window.location.reload();
  };

  // 点击头像切换下拉菜单显示状态
  const toggleDropdown = () => {
    setShowDropdown(!showDropdown);
  };

  // 点击外部关闭下拉菜单
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowDropdown(false);
      }
    };

    // 监听全局点击事件
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      // 组件卸载时移除监听
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  return (
    <NavContainer>
      <NavContent>
        {/* Logo区域 */}
        <Logo to="/">
          {t('navbar.logo')}
        </Logo>

        {/* 导航链接区域 */}
        <NavLinks>
          <a href="#features">{t('navbar.features')}</a>
          <a href="#models">{t('navbar.models')}</a>
          <a href="#finance">{t('navbar.finance')}</a>
          <a href="#testimonials">{t('navbar.testimonials')}</a>
        </NavLinks>

        {/* 右侧：语言选择器 + 登录/用户信息 */}
        <RightSection>
          {/* 语言选择器 */}
          <LanguageSelector>
            <LanguageButton
              $isActive={currentLng === 'zh'}
              onClick={() => changeLanguage('zh')}
            >
              中文
            </LanguageButton>
            <LanguageButton
              $isActive={currentLng === 'en'}
              onClick={() => changeLanguage('en')}
            >
              英文
            </LanguageButton>
            <LanguageButton
              $isActive={currentLng === 'ja'}
              onClick={() => changeLanguage('ja')}
            >
              日文
            </LanguageButton>
          </LanguageSelector>

          {/* 登录/用户区域 */}
          {currentUser ? (
            // 已登录：显示用户头像 + 下拉菜单（受控显示）
            <UserMenu ref={dropdownRef}>
              <UserAvatar onClick={toggleDropdown}>
                {/* {currentUser.username} */}
              </UserAvatar>
              
              {/* 只有当showDropdown为true时才显示下拉菜单 */}
              {showDropdown && (
                <DropdownMenu>
                  {/* 显示用户名（替换原来的Profile） */}
                  <DropdownLink to="/profile">
                    {currentUser.username}
                  </DropdownLink>
                  
                  {/* 贷款申请选项 - 仅客户可见 */}
                  {currentUser.role === 'customer' && (
                    <DropdownLink to="/loan-application">
                      {t('navbar.loanApplication')}
                    </DropdownLink>
                  )}

                  {/* 我的订单/审批 */}
                  <DropdownLink to="/order-status">
                    {t('navbar.orderStatus')}
                  </DropdownLink>
                  
                  {/* 管理员专属：管理员面板链接 */}
                  {currentUser.role === 'admin' && (
                    <DropdownLink to="/admin-dashboard">
                      {t('navbar.adminDashboard')}
                    </DropdownLink>
                  )}
                  
                  {/* 注销按钮 */}
                  <DropdownItem
                    $isButton
                    className="logout"
                    onClick={handleLogout}
                  >
                    {t('navbar.logout')}
                  </DropdownItem>
                </DropdownMenu>
              )}
            </UserMenu>
          ) : (
            // 未登录：显示登录按钮
            <LoginButton onClick={() => setIsLoginModalOpen(true)}>
              {t('navbar.login')}
            </LoginButton>
          )}
        </RightSection>
      </NavContent>

      {/* 登录模态框 */}
      {isLoginModalOpen && (
        <Login 
          isOpen={isLoginModalOpen}
          onClose={() => setIsLoginModalOpen(false)}
        />
      )}
    </NavContainer>
  );
};

export default Navbar;