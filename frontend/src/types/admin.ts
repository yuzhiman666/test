import { MultiLanguageStr } from './common';

// 客户信息类型
export interface Customer {
  id: string;
  userId: string;
  name: string;
  phone: string;
  email: string;
  idNumber: string;
  address: string;
  monthlyIncome: number;
  applicationStatus: '草稿' | '已提交' | '审核中' | '已批准' | '已拒绝';
  auditResult?: 'Approve' | 'Reject';
  auditTime?: string;
  carBrand: string;
  carModel: string;
  carPrice: number;
  loanAmount: number;
  createdAt: string;
}

// 统计数据类型
export interface StatisticData {
  totalApplications: number;
  pendingApplications: number;
  approvedApplications: number;
  rejectedApplications: number;
  totalSales: number;
  monthlySales: { month: string; amount: number }[];
  regionalSales: { region: string; amount: number }[];
}

// 3D图表数据类型
export interface ChartData {
  type: 'pie' | 'bar' | 'line';
  title: MultiLanguageStr;
  data: { name: string; value: number; color: string }[];
  dimensions?: { x: number; y: number; z: number };
}

// 区域数据类型
export interface RegionData {
  id: string;
  name: MultiLanguageStr;
  coordinates: number[][];
  salesData: StatisticData;
}