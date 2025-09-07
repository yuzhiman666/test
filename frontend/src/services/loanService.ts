// src/services/loanService.ts
import axios from './api.ts';
import { LoanApplication } from '../types/loan.ts';

// 提交贷款申请
export const submitLoanApplication = (data: Omit<LoanApplication, '_id' | 'createdAt' | 'updatedAt'>) => {
  return axios.post('/loan-application', data);
};

// 保存草稿
export const saveDraft = (data: Omit<LoanApplication, '_id' | 'createdAt' | 'updatedAt'>) => {
  // return axios.post('/loan-application/draft', data);
  return axios.post('/loan-application', { ...data, status: 'Draft'});
};

// 获取贷款申请
export const getLoanApplication = (id?: string) => {
  // return id ? axios.get(`/loan-application/${id}`) : axios.get('/loan-application/my');
  return id 
    ? axios.get(`/loan-application/${id}`, { timeout: 5000 }) 
    : axios.get('/loan-application/my', { timeout: 5000 });
};

// 获取AI建议
export const getAISuggestion = (applicationId: string) => {
  return axios.get(`/loan-application/${applicationId}/ai-suggestion`);
};

// 获取车辆品牌列表
export const getCarBrands = () => {
  return axios.get('/car-brands');
};

// 根据品牌获取车型
export const getCarModels = (brand: string) => {
  return axios.get(`/car-models?brand=${brand}`);
};

// 根据品牌和车型获取车辆价格
export const getCarPrice = (brand: string, model: string, lang: string) => {
  return axios.get(`/car-price?brand=${brand}&model=${model}&lang=${lang}`);
};

// 获取贷款方案
export const getLoanPlans = () => {
  return axios.get('/loan-plans');
};