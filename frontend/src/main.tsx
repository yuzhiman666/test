import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom'; // 只在入口文件引入一次
import App from './App';
// import './index.css';

// 整个应用唯一的Router实例
ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter> {/* 根级路由，所有组件共享此实例 */}
      <App />
    </BrowserRouter>
  </React.StrictMode>
);
