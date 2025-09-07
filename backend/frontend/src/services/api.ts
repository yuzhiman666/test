import axios from 'axios';
import type { Customer, CreditReviewDetail } from '../types';

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:8000', // FastAPI后端地址
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 获取客户列表
export const getCustomers = async (): Promise<Customer[]> => {
  const response = await api.get('/customers/pending');
  return response.data;
};

// 获取客户信贷详情
export const getCustomerCreditDetail = async (userId: string): Promise<CreditReviewDetail> => {
  const response = await api.get(`/loan/detail?user_id=${userId}`);
  return response.data;
};

// 审批客户贷款申请
export const approveLoan = async (userId: string, human_reult:string,thread_id:string, feedback?: string) => {
  const response = await api.post('/loan/approve', {
    user_id: userId,
    human_reult:human_reult,
    thread_id:"a3051992-88ee-4949-ac7c-4795e2f4bf59",
    feedback: feedback || ''
  });
  return response.data;
};

// 拒绝客户贷款申请
export const rejectLoan = async (userId: string, human_reult:string, thread_id:string, feedback?: string) => {
  const response = await api.post('/loan/reject', {
    user_id: userId,
    human_reult:human_reult,
    thread_id:"a3051992-88ee-4949-ac7c-4795e2f4bf59",
    feedback: feedback || ''
  });
  return response.data;
};

// 批量处理贷款申请
export const batchProcessLoans = async (userIds: string[], action: 'approve' | 'reject', feedback?: string) => {
  const response = await api.post('/loan/batch-process', {
    user_ids: userIds,
    action,
    feedback: feedback || ''
  });
  return response.data;
};

// 向Chatbot发送消息
export const sendChatMessage = async (message: string): Promise<string> => {
  const response = await api.post('/chat', { message });
  return response.data.response;
};

export default api;