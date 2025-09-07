// src/types/index.ts
export interface Customer {
  id: string;
  name: string;
  age: number;
  idNumber: string;
  monthlyIncome: number;
  annualIncome: number;
  employmentTenure: number;
  employmentPosition: string;
  delinquencies: number;
  creditLines: number;
  loanAmount: number;
  loanPurpose: string;
  status: 'pending' | 'approved' | 'rejected';
  verificationStatus: string;
}

export interface CreditReviewDetail {
  creditRating: string;
  fraudDetection: string;
  compliance: string;
  [key: string]: any;
}

// 确保以下接口被正确导出
export interface ChatMessage {
  id: string;
  content: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}