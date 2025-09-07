// src/types/loan.ts
export interface PersonalInfo {
  fullName: string;
  idNumber: string;
  phoneNumber: string;
  email: string;
  address: string;
  employmentStatus: 'employed' | 'selfEmployed' | 'unemployed' | 'student';
  monthlyIncome: number;
  accountHolderName: string;
  accountNumber: string;
  bankName: string;
}

export interface CarSelection {
  carBrand: string;
  carBrandLabel: string;
  carModel: string;
  carYear: number;
  carType: 'sedan' | 'suv' | 'electric' | 'hybrid';
  carPrice: number;
}

export interface LoanDetails {
  downPayment: number; // 首付比例（%）
  downPaymentAmount: number; // 首付金额
  loanAmount: number; // 贷款总额
  interestRate: number; // 年利率（%）
  loanTerm: number; // 贷款期限（月）
  loanStartDate: string; // 开始日期
  loanEndDate: string; // 结束日期
  repaymentFrequency: 'monthly' | 'quarterly' | 'yearly';
  monthlyPayment: number; // 每期还款额
  repaymentDate: number; // 每期还款日（如每月5日）
  repaymentMethod: 'equalPrincipalInterest' | 'equalPrincipal';
}

// 修改Document和LoanApplication接口
export interface Document {
  id: string;
  name: string;
  type: string;
  url: string;
}

export interface DocumentSet {
  idCard: Document | null;         // 身份证
  creditReport: Document | null;   // 个人征信报告
  salarySlip: Document | null;     // 工资流水
  employmentProof: Document | null; // 在职证明
}

export interface LoanApplication {
  _id?: string;
  applicationId?: string
  userId: string;
  status: 'Draft' | 'InReview' | 'Submitted' | 'Approved' | 'Rejected';
  //与后端保持一致
  // status: '已提交' | '审核中' | '已批准' | '已拒绝' | '草稿';
  personalInfo: PersonalInfo; // 必选
  carSelection: CarSelection; // 必选
  loanDetails: LoanDetails; // 必选
  documents: DocumentSet; // 替换原有的documents数组
  aiSuggestion?: string;
  createdAt?: string;
  updatedAt?: string;
}

export interface LoanApplicationList {
  application_id: string
  fullName: string;
  createdAt: string;
  status: string;
}