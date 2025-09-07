import axios from './api';
import { Customer, StatisticData, RegionData } from '../types/admin.ts';
import { LoanApplication } from '../types/loan.ts';

// 获取客户列表
export const getCustomerList = (page: number, pageSize: number, filters?: any) => {
  return axios.get('/admin/customers', {
    params: { page, pageSize, ...filters }
  });
};

// 获取客户详情
export const getCustomerDetail = (id: string) => {
  return axios.get(`/admin/customers/${id}`);
};

// 审核客户贷款申请
export const auditApplication = (id: string, result: 'Approve' | 'Reject', feedback?: string) => {
  return axios.post(`/admin/customers/${id}/audit`, {
    auditResult: result,
    feedback
  });
};

// 批量审核
export const batchAuditApplications = (ids: string[], result: 'Approve' | 'Reject') => {
  return axios.post('/admin/customers/batch-audit', {
    ids,
    auditResult: result
  });
};

// 导出客户数据
export const exportCustomers = (ids?: string[]) => {
  return axios.get('/admin/customers/export', {
    params: ids ? { ids: ids.join(',') } : {},
    responseType: 'blob'
  });
};

// 获取统计数据
export const getStatisticData = (region?: string) => {
  return axios.get('/admin/statistics', {
    params: region ? { region } : {}
  });
};

// 获取区域数据
export const getRegionData = () => {
  return axios.get('/admin/regions');
};

// AI聊天查询
export const adminChatQuery = (message: string) => {
  return axios.post('/admin/ai/chat', { message });
};


// 获取所有贷款申请（管理员）
export const getAllLoanApplications = () => {
  return axios.get('/admin/loan-applications', { timeout: 10000 });
};

// 获取单个贷款申请详情（管理员）
export const getLoanApplicationDetails = (applicationId: string) => {
  return axios.get(`/admin/loan-applications/${applicationId}`, { timeout: 5000 });
};

// 获取贷款申请的审批流程日志
export const getLoanApplicationWorkflowLogs = (applicationId: string) => {
  return axios.get(`/admin/loan-applications/${applicationId}/workflow-logs`, { timeout: 5000 });
};