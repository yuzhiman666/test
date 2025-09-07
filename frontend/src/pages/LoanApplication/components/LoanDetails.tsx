// src/pages/LoanApplication/components/LoanDetails.tsx
import React, { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import styles from '../LoanApplication.module.css';
import { LoanDetails } from '../../../types/loan.ts';

interface LoanDetailsProps {
  data: Partial<LoanDetails>;
  carPrice: number;
  onChange: (data: LoanDetails) => void;
  disabled: boolean;
}

const LoanDetailsComponent: React.FC<LoanDetailsProps> = ({ data, carPrice, onChange, disabled }) => {
  const { t } = useTranslation();
  
  // 单独计算 downPaymentAmount（仅依赖 carPrice 和 downPayment）
  useEffect(() => {
    // 只要车辆价格和首付比例存在，就计算首付金额
    if (carPrice && data.downPayment) {
      const loanAmount = carPrice * (1 - data.downPayment / 100);
      const downPaymentAmount = carPrice - loanAmount;
      
      onChange({
        ...data,
        downPaymentAmount: Number(downPaymentAmount.toFixed(2)),
        // 同步更新贷款金额（因为 loanAmount 也仅依赖这两个参数）
        loanAmount: Number(loanAmount.toFixed(2)),
      } as LoanDetails);
    }
  }, [data.downPayment, carPrice, onChange, data]); // 仅依赖必要参数
  
  // 计算月供等需要其他参数的逻辑（保持不变）
  useEffect(() => {
    if (carPrice && data.downPayment && data.loanTerm && data.interestRate && data.repaymentMethod) {
      const loanAmount = carPrice * (1 - data.downPayment / 100);
      const monthlyRate = data.interestRate / 100 / 12;
      let monthlyPayment = 0;

      if (data.repaymentMethod === 'equalPrincipalInterest') {
        // 等额本息计算
        monthlyPayment = loanAmount * monthlyRate * Math.pow(1 + monthlyRate, data.loanTerm) / 
                        (Math.pow(1 + monthlyRate, data.loanTerm) - 1);
      } else {
        // 等额本金计算
        const principalPerMonth = loanAmount / data.loanTerm;
        const firstMonthInterest = loanAmount * monthlyRate;
        monthlyPayment = principalPerMonth + firstMonthInterest;
      }

      onChange({
        ...data,
        monthlyPayment: Number(monthlyPayment.toFixed(2)),
      } as LoanDetails);
    }
  }, [data.downPayment, data.loanTerm, data.interestRate, data.repaymentMethod, carPrice, onChange, data]);
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    onChange({
      ...data,
      [name]: Number(value)
    } as LoanDetails);
  };
  
  return (
    <div className={styles.section}>
      <h3>{t('loanApplication.loanDetails.title')}</h3>
      
      <div className={styles.formGroup}>
        <label>{t('loanApplication.loanDetails.downPayment')} (%)</label>
        <input
          type="number"
          name="downPayment"
          min="0"
          max="100"
          value={data.downPayment || ''}
          onChange={handleChange}
          disabled={disabled}
          required
        />
      </div>
      <div className={styles.formGroup}>
        <label>{t('loanApplication.loanDetails.downPaymentAmount')}</label>
        <input
          type="number"
          name="downPaymentAmount"
          value={data.downPaymentAmount || ''}
          readOnly
          className={styles.readonlyInput}
        />
      </div>
      <div className={styles.formGroup}>
        <label>{t('loanApplication.loanDetails.loanTerm')} ({t('home.finance.calculator.months')})</label>
        <select
          name="loanTerm"
          value={data.loanTerm || ''}
          onChange={handleChange}
          disabled={disabled}
          required
        >
          <option value="">{t('loanApplication.selectOption')}</option>
          <option value="12">12</option>
          <option value="24">24</option>
          <option value="36">36</option>
          <option value="48">48</option>
          <option value="60">60</option>
        </select>
      </div>
      
      <div className={styles.formGroup}>
        <label>{t('loanApplication.loanDetails.interestRate')} (%)</label>
        <input
          type="number"
          step="0.01"
          min="0"
          max="20"
          name="interestRate"
          value={data.interestRate || ''}
          onChange={handleChange}
          disabled={disabled}
          required
        />
      </div>
      
      <div className={styles.formGroup}>
        <label>{t('loanApplication.loanDetails.repaymentMethod')}</label>
        <select
          name="repaymentMethod"
          value={data.repaymentMethod || ''}
          onChange={handleChange}
          disabled={disabled}
          required
        >
          <option value="">{t('loanApplication.selectOption')}</option>
          <option value="equalPrincipalInterest">{t('loanApplication.loanDetails.equalPrincipalInterest')}</option>
          <option value="equalPrincipal">{t('loanApplication.loanDetails.equalPrincipal')}</option>
        </select>
      </div>
      
      <div className={styles.formGroup}>
        <label>{t('loanApplication.loanDetails.loanAmount')}</label>
        <input
          type="number"
          name="loanAmount"
          value={data.loanAmount || ''}
          disabled={true}
          readOnly
        />
      </div>
      
      <div className={styles.formGroup}>
        <label>{t('loanApplication.loanDetails.monthlyPayment')}</label>
        <input
          type="number"
          name="monthlyPayment"
          value={data.monthlyPayment || ''}
          disabled={true}
          readOnly
        />
      </div>
    </div>
  );
};

export default LoanDetailsComponent;