// src/pages/LoanApplication/components/PersonalInfo.tsx
import React from 'react';
import { useTranslation } from 'react-i18next';
import styles from '../LoanApplication.module.css';
// 保留类型原名
import { PersonalInfo } from '../../../types/loan.ts';

// 接口中使用原类型名
interface PersonalInfoProps {
  data: Partial<PersonalInfo>;
  onChange: (data: PersonalInfo) => void;
  disabled: boolean;
}

// 组件名修改为不同的名称（例如加后缀Component）
const PersonalInfoComponent: React.FC<PersonalInfoProps> = ({ data, onChange, disabled }) => {
  const { t } = useTranslation();
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    onChange({
      ...data,
      [name]: name === 'monthlyIncome' ? Number(value) : value
    } as PersonalInfo);
  };
  
  return (
    <div className={styles.section}>
      <h3>{t('loanApplication.personalInfo.title')}</h3>
      
      <div className={styles.formGroup}>
        <label>{t('loanApplication.personalInfo.fullName')}</label>
        <input
          type="text"
          name="fullName"
          value={data.fullName || ''}
          onChange={handleChange}
          disabled={disabled}
          required
        />
      </div>
      
      <div className={styles.formGroup}>
        <label>{t('loanApplication.personalInfo.idNumber')}</label>
        <input
          type="text"
          name="idNumber"
          value={data.idNumber || ''}
          onChange={handleChange}
          disabled={disabled}
          required
        />
      </div>
      
      <div className={styles.formGroup}>
        <label>{t('loanApplication.personalInfo.phoneNumber')}</label>
        <input
          type="tel"
          name="phoneNumber"
          value={data.phoneNumber || ''}
          onChange={handleChange}
          disabled={disabled}
          required
        />
      </div>
      
      <div className={styles.formGroup}>
        <label>{t('loanApplication.personalInfo.email')}</label>
        <input
          type="email"
          name="email"
          value={data.email || ''}
          onChange={handleChange}
          disabled={disabled}
          required
        />
      </div>
      
      <div className={styles.formGroup}>
        <label>{t('loanApplication.personalInfo.address')}</label>
        <input
          type="text"
          name="address"
          value={data.address || ''}
          onChange={handleChange}
          disabled={disabled}
          required
        />
      </div>
      
      <div className={styles.formGroup}>
        <label>{t('loanApplication.personalInfo.employmentStatus')}</label>
        <select
          name="employmentStatus"
          value={data.employmentStatus || ''}
          onChange={handleChange}
          disabled={disabled}
          required
        >
          <option value="">{t('loanApplication.selectOption')}</option>
          <option value="employed">{t('loanApplication.personalInfo.employed')}</option>
          <option value="self-employed">{t('loanApplication.personalInfo.selfEmployed')}</option>
          <option value="unemployed">{t('loanApplication.personalInfo.unemployed')}</option>
          <option value="student">{t('loanApplication.personalInfo.student')}</option>
        </select>
      </div>
      
      <div className={styles.formGroup}>
        <label>{t('loanApplication.personalInfo.monthlyIncome')}</label>
        <input
          type="number"
          name="monthlyIncome"
          value={data.monthlyIncome || ''}
          onChange={handleChange}
          disabled={disabled}
          required
        />
      </div>
      
      <div className={styles.formGroup}>
        <label>{t('loanApplication.personalInfo.accountNumber')}</label>  
        <input
          type="text"
          name="accountNumber"  // 修正字段名
          value={data.accountNumber || ''}  // 修正数据键
          onChange={handleChange}
          disabled={disabled}
          required
        />
      </div>
      <div className={styles.formGroup}>
        <label>{t('loanApplication.personalInfo.accountHolderName')}</label>  
        <input
          type="text"
          name="accountHolderName"  // 修正字段名
          value={data.accountHolderName || ''}  // 修正数据键
          onChange={handleChange}
          disabled={disabled}
          required
        />
      </div>
      <div className={styles.formGroup}>
        <label>{t('loanApplication.personalInfo.bankName')}</label>
        <input
          type="text"
          name="bankName"
          value={data.bankName || ''}
          onChange={handleChange}
          disabled={disabled}
          required
        />
      </div>
    </div>
  );
};

export default PersonalInfoComponent;