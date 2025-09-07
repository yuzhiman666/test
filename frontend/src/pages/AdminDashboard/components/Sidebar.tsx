import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useLocation } from 'react-router-dom';
import { 
  DashboardOutlined, 
  UserOutlined, 
  FileTextOutlined, 
  SettingOutlined,
  BarChartOutlined,
  CarOutlined,
  BellOutlined,
  LogoutOutlined
} from '@ant-design/icons';
import styles from './Sidebar.module.css';
// Update the import path if AuthContext is located elsewhere, for example:
// import { useAuth } from '../../contexts/AuthContext.tsx';
// Or correct the path to where AuthContext actually exists.

interface SidebarProps {
  open: boolean;
  onToggle: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ open, onToggle }) => {
  const { t } = useTranslation();
  const location = useLocation();
  const { user, logout } = useAuth();
  const [activeKey, setActiveKey] = useState('dashboard');
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);

  // 监听窗口大小变化
  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768);
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // 确定当前激活的菜单项
  useEffect(() => {
    const path = location.pathname;
    if (path.includes('dashboard')) setActiveKey('dashboard');
    else if (path.includes('customers')) setActiveKey('customers');
    else if (path.includes('applications')) setActiveKey('applications');
    else if (path.includes('reports')) setActiveKey('reports');
    else if (path.includes('cars')) setActiveKey('cars');
    else if (path.includes('settings')) setActiveKey('settings');
  }, [location.pathname]);

  // 菜单项定义
  const menuItems = [
    {
      key: 'dashboard',
      icon: <DashboardOutlined />,
      label: t('sidebar.dashboard'),
      path: '/admin-dashboard'
    },
    {
      key: 'customers',
      icon: <UserOutlined />,
      label: t('sidebar.customers'),
      path: '/admin/customers'
    },
    {
      key: 'applications',
      icon: <FileTextOutlined />,
      label: t('sidebar.applications'),
      path: '/admin/applications'
    },
    {
      key: 'reports',
      icon: <BarChartOutlined />,
      label: t('sidebar.reports'),
      path: '/admin/reports'
    },
    {
      key: 'cars',
      icon: <CarOutlined />,
      label: t('sidebar.cars'),
      path: '/admin/cars'
    },
    {
      key: 'notifications',
      icon: <BellOutlined />,
      label: t('sidebar.notifications'),
      path: '/admin/notifications'
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: t('sidebar.settings'),
      path: '/admin/settings'
    }
  ];

  // 移动端在点击菜单项后关闭侧边栏
  const handleMenuItemClick = (key: string) => {
    setActiveKey(key);
    if (isMobile) {
      onToggle();
    }
  };

  return (
    <aside className={`${styles.sidebar} ${open ? styles.open : styles.closed}`}>
      <div className={styles.logoContainer}>
        <div className={styles.logo}>
          <CarOutlined className={styles.logoIcon} />
          {open && <span className={styles.logoText}>AutoFinance AI</span>}
        </div>
      </div>

      <div className={styles.menuContainer}>
        <ul className={styles.menuList}>
          {menuItems.map(item => (
            <li 
              key={item.key}
              className={`${styles.menuItem} ${activeKey === item.key ? styles.active : ''}`}
              onClick={() => handleMenuItemClick(item.key)}
            >
              <Link to={item.path} className={styles.menuLink}>
                <span className={styles.menuIcon}>{item.icon}</span>
                {open && <span className={styles.menuLabel}>{item.label}</span>}
              </Link>
            </li>
          ))}
        </ul>
      </div>

      <div className={styles.userSection}>
        {open ? (
          <div className={styles.userInfo}>
            <div className={styles.avatar}>
              {user?.name?.charAt(0) || 'A'}
            </div>
            <div className={styles.userDetails}>
              <div className={styles.userName}>{user?.name}</div>
              <div className={styles.userRole}>{t('role.admin')}</div>
            </div>
            <button 
              className={styles.logoutButton}
              onClick={logout}
              aria-label={t('auth.logout')}
            >
              <LogoutOutlined />
            </button>
          </div>
        ) : (
          <button 
            className={styles.logoutIcon}
            onClick={logout}
            aria-label={t('auth.logout')}
          >
            <LogoutOutlined />
          </button>
        )}
      </div>
    </aside>
  );
};

export default Sidebar;

function useAuth(): { user: any; logout: any; } {
    throw new Error('Function not implemented.');
}