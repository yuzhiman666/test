import React from 'react';
import AppRouter from './router'; // 引入路由配置
import Footer from './components/common/Footer/Footer';
import Header from './components/common/Navbar/Navbar';

const App: React.FC = () => {
  return (
    <div className="app-container">
      {/* 不添加任何Router相关组件 */}
      <Header />
      <main className="main-content">
        <AppRouter /> {/* 直接使用路由配置 */}
      </main>
      <Footer />
    </div>
  );
};

export default App;
