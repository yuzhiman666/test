import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
// 移除.tsx后缀（TypeScript导入可省略），保持路径简洁
import Login from '../../../pages/Login/Login.tsx';
import { getCurrentUser, logout } from '../../../services/authService.ts';

// ========================== 样式组件定义（统一集中在顶部，避免重复）==========================
const NavContainer = styled.nav`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 5%;
  background-color: #ffffff;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000; /* 提升层级，确保导航栏在最上层 */
`;

const NavContent = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%; /* 占满容器宽度，确保子元素均匀分布 */
`;

const Logo = styled(Link)`
  font-size: 1.5rem;
  font-weight: bold;
  color: #2c3e50;
  text-decoration: none;
  transition: color 0.3s;

  &:hover {
    color: #3498db; /* hover时变色，增加交互感 */
  }
`;

const NavLinks = styled.div`
  display: flex;
  gap: 2rem; /* 链接之间的间距 */

  a {
    text-decoration: none;
    color: #34495e;
    font-weight: 500;
    transition: color 0.3s;

    &:hover {
      color: #3498db; /*  hover时变色，统一交互风格 */
    }
  }
`;

const RightSection = styled.div`
  display: flex;
  align-items: center; /* 垂直居中 */
`;

const LanguageSelector = styled.div`
  display: flex;
  gap: 0.5rem;
  margin-right: 1.5rem; /* 与登录按钮/头像保持间距 */
`;

const LanguageButton = styled.button<{ $isActive: boolean }>`
  background: none;
  border: none;
  cursor: pointer;
  color: ${(props) => (props.$isActive ? '#3498db' : '#34495e')}; // 样式中使用 $isActive
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
    background-color: #2980b9; /* 加深颜色，反馈hover状态 */
  }

  &:active {
    transform: scale(0.98); /* 点击时轻微缩小，增强点击反馈 */
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
    background-color: #2980b9; /* hover时加深颜色 */
  }
`;

const DropdownMenu = styled.div`
  position: absolute;
  top: 45px; /* 与头像保持微小间距 */
  right: 0;
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15); /* 增强阴影，提升层次感 */
  width: 180px;
  z-index: 1001; /* 高于导航栏，确保下拉菜单可见 */
  overflow: hidden; /* 防止内容溢出圆角 */
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
    background-color: #f5f5f5; /* hover时背景色变化 */
  }

  /* 注销按钮特殊样式 */
  &.logout {
    color: #e74c3c; /* 红色强调注销操作 */
    &:hover {
      background-color: #fdecea; /* 红色系背景，强化视觉反馈 */
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
    background-color: #f5f5f5; /* 与DropdownItem hover样式统一 */
  }
`;

// ========================== 组件逻辑 ==========================
const Navbar = () => {
  const { i18n, t } = useTranslation();
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);
  const currentUser = getCurrentUser();
  const currentLng = i18n.language; // 当前选中的语言

  // 切换语言逻辑
  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
  };

  // 注销逻辑
  const handleLogout = () => {
    logout(); // 清除localStorage中的token和user
    window.location.reload(); // 刷新页面，重置状态
  };

  return (
    <NavContainer>
      <NavContent>
        {/* 1. Logo区域（使用国际化文本，避免硬编码） */}
        <Logo to="/">
          {t('navbar.logo')} {/* 对应翻译文件中的"汽车金融AI平台"等文本 */}
        </Logo>

        {/* 2. 导航链接区域（锚点跳转至首页对应区块） */}
        <NavLinks>
          <a href="#features">{t('navbar.features')}</a>
          <a href="#models">{t('navbar.models')}</a>
          <a href="#finance">{t('navbar.finance')}</a>
          <a href="#testimonials">{t('navbar.testimonials')}</a>
        </NavLinks>

        {/* 3. 右侧：语言选择器 + 登录/用户信息 */}
        <RightSection>
          {/* 语言选择器（带当前选中状态） */}
          <LanguageSelector>
            <LanguageButton
              $isActive={currentLng === 'zh'}  // 瞬时属性，不会透传到 DOM
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

          {/* 登录/用户区域（根据登录状态切换） */}
          {currentUser ? (
            // 已登录：显示用户头像 + 下拉菜单
            <UserMenu>
              <UserAvatar>
                {/* 显示用户名首字母（大写） */}
                {currentUser.name.charAt(0).toUpperCase()}
              </UserAvatar>
              <DropdownMenu>
                {/* 用户名 */}
                <DropdownItem disabled>
                  {currentUser.name}
                </DropdownItem>

                {/* 贷款申请选项 - 仅客户可见 */}
                {currentUser.role === 'customer' && (
                  <DropdownLink to="/loan-application">
                    {t('navbar.loanApplication')}
                  </DropdownLink>
                )}

                {/* 管理员专属：管理员面板链接 */}
                {currentUser.role === 'admin' && (
                  <DropdownLink to="/admin-dashboard">
                    {t('navbar.adminDashboard')}
                  </DropdownLink>
                )}
                {/* 通用：订单/审批状态链接 */}
                <DropdownLink to="/order-status">
                  {t('navbar.orderStatus')}
                </DropdownLink>
                {/* 注销按钮 */}
                <DropdownItem
                  $isButton
                  className="logout"
                  onClick={handleLogout}
                >
                  {t('navbar.logout')}
                </DropdownItem>
              </DropdownMenu>
            </UserMenu>
          ) : (
            // 未登录：显示登录按钮（点击弹出模态框）
            <LoginButton onClick={() => setIsLoginModalOpen(true)}>
              {t('navbar.login')}
            </LoginButton>
          )}
        </RightSection>
      </NavContent>

      {/* 登录模态框（条件渲染：isLoginModalOpen为true时显示） */}
      {isLoginModalOpen && (
        <Login 
          isOpen={isLoginModalOpen} // 传递显示状态（必传）
          onClose={() => setIsLoginModalOpen(false)} // 传递关闭回调（必传）
        />
      )}
    </NavContainer>
  );
};

export default Navbar;