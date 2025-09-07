import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom'; // 只引入路由规则组件
import Home from './pages/Home/Home';
import LoanApplication from './pages/LoanApplication/LoanApplication';
import LoanApplicationConfirm from './pages/LoanApplication/LoanApplicationConfirm';
import ApplicationList from './pages/AdminDashboard/ApplicationList.tsx';
import ApplicationDetails from './pages/AdminDashboard/ApplicationDetails.tsx';
// import NotFound from '../pages/NotFound';

const AppRouter: React.FC = () => {
  return (
    // 只包含路由规则，不包裹任何Router
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/loan-application" element={<LoanApplication />} />
      {/* 确保确认页路由正确配置 */}
      <Route 
        path="/loan-application/confirm" 
        element={<LoanApplicationConfirm />} 
      />
      <Route path="/admin-dashboard" element={<ApplicationList />} />
      <Route path="/admin-dashboard/details/:id" element={<ApplicationDetails />} />
      {/* <Route path="/404" element={<NotFound />} /> */}
      <Route path="*" element={<Navigate to="/404" replace />} />
    </Routes>
  );
};

export default AppRouter;
