// src/pages/LoanApplication/LoanApplicationConfirm.tsx
import React, { useState, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation, useNavigate } from 'react-router-dom';
import styles from './LoanApplicationConfirm.module.css';
import { submitLoanApplication } from '../../services/loanService.ts';
import { getAISuggestion } from '../../services/loanService.ts';
import { LoanApplication } from '../../types/loan.ts';
import AISuggestion from './components/AISuggestion.tsx';

const LoanApplicationConfirm: React.FC = () => {
  const { t } = useTranslation();
  const location = useLocation();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  // AI建议相关状态
  const [aiSuggestion, setAiSuggestion] = useState<string>('');
  const [loadingAI, setLoadingAI] = useState<boolean>(true);
  const [showAISuggestion, setShowAISuggestion] = useState<boolean>(true);
  
  // 新增：用于跟踪左侧确认信息区域的高度
  const formContentRef = useRef<HTMLDivElement>(null);
  const [formContentHeight, setFormContentHeight] = useState<number>(0);
  
  // 从路由获取数据
  const formData = location.state?.formData as Partial<LoanApplication>;
  const currentUser = location.state?.currentUser;
  const applicationId = location.state.applicationId;

  // 页面加载时自动获取AI建议
  useEffect(() => {
    const fetchAISuggestion = async () => {
      if (!applicationId) {
        console.log('没有申请ID，无法获取AI建议');
        setLoadingAI(false);
        return;
      }
      
      try {
        setLoadingAI(true);
        const response = await getAISuggestion(applicationId);
        setAiSuggestion(response.data.analysis);
        setShowAISuggestion(true);
      } catch (error) {
        console.error('获取AI建议错误:', error);
        setAiSuggestion(t('loanApplication.aiErrorContent'));
      } finally {
        setLoadingAI(false);
      }
    };

    fetchAISuggestion();
  }, [applicationId, t]);

  // 新增：获取左侧区域初始高度
  useEffect(() => {
    if (formContentRef.current) {
      // 保存左侧内容的初始高度
      setFormContentHeight(formContentRef.current.offsetHeight);
    }
  }, [formData]); // 当表单数据变化时重新计算高度

  useEffect(() => {
    if (!formData) {
      console.error('未获取到表单数据');
      setTimeout(() => {
        navigate('/loan-application');
      }, 3000);
    }
  }, [formData, navigate]);

  if (!formData) {
    return (
      <div className={styles.accessDenied}>
        {t('loanApplication.invalidData')}
        <p>{t('loanApplication.redirecting')}</p>
      </div>
    );
  }

  const handleFinalSubmit = async () => {
    if (!currentUser?.id) {
      alert(t('loanApplication.loginRequired'));
      return;
    }

    try {
      setLoading(true);
      const payload = {
        ...formData,
        userId: currentUser.id,
        status: 'Submitted' as const,
        applicationId: applicationId,
        aiSuggestion:aiSuggestion
      };
      await submitLoanApplication(payload as Omit<LoanApplication, '_id' | 'createdAt' | 'updatedAt'>);
      alert(t('loanApplication.submitSuccess'));
      navigate('/loan-application/success');
    } catch (error) {
      console.error('提交申请错误:', error);
      alert(t('loanApplication.submitFailed'));
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className={styles.loading}>{t('loading')}</div>;
  }

  return (
    <div className={styles.container}>
      <h1>{t('loanApplication.confirmTitle')}</h1>
      
      {/* 布局调整：左侧确认信息，右侧AI建议 */}
      <div className={styles.formContainer}>
        {/* 左侧：确认信息（添加ref跟踪高度） */}
        <div className={styles.formContent} ref={formContentRef}>
          <h2>{t('loanApplication.confirmInfo')}</h2>
          
          {/* 个人信息确认 */}
          <div className={styles.section}>
            <h3>{t('loanApplication.personalInfo.title')}</h3>
            <p><strong>{t('loanApplication.personalInfo.fullName')}:</strong> {formData.personalInfo?.fullName}</p>
            <p><strong>{t('loanApplication.personalInfo.idNumber')}:</strong> {formData.personalInfo?.idNumber}</p>
            <p><strong>{t('loanApplication.personalInfo.phoneNumber')}:</strong> {formData.personalInfo?.phoneNumber}</p>
            <p><strong>{t('loanApplication.personalInfo.email')}:</strong> {formData.personalInfo?.email}</p>
          </div>
          
          {/* 车辆信息确认 */}
          <div className={styles.section}>
            <h3>{t('loanApplication.carSelection.title')}</h3>
            <p><strong>{t('loanApplication.carSelection.carBrand')}:</strong> {formData.carSelection?.carBrandLabel}</p>
            <p><strong>{t('loanApplication.carSelection.carModel')}:</strong> {formData.carSelection?.carModel}</p>
            <p><strong>{t('loanApplication.carSelection.carPrice')}:</strong> {formData.carSelection?.carPrice}</p>
          </div>
          
          {/* 贷款信息确认 */}
          <div className={styles.section}>
            <h3>{t('loanApplication.loanDetails.title')}</h3>
            <p><strong>{t('loanApplication.loanDetails.downPayment')}:</strong> {formData.loanDetails?.downPayment}%</p>
            <p><strong>{t('loanApplication.loanDetails.loanTerm')}:</strong> {formData.loanDetails?.loanTerm} {t('home.finance.calculator.months')}</p>
            <p><strong>{t('loanApplication.loanDetails.interestRate')}:</strong> {formData.loanDetails?.interestRate}%</p>
            <p><strong>{t('loanApplication.loanDetails.loanAmount')}:</strong> {formData.loanDetails?.loanAmount}</p>
            <p><strong>{t('loanApplication.loanDetails.monthlyPayment')}:</strong> {formData.loanDetails?.monthlyPayment}</p>
          </div>
          
          <div className={styles.actionButtons}>
            <button 
              className={styles.resetButton} 
              onClick={() => navigate(-1)}
            >
              {t('loanApplication.back')}
            </button>
            <button 
              className={styles.submitButton} 
              onClick={handleFinalSubmit}
            >
              {t('loanApplication.finalSubmit')}
            </button>
          </div>
        </div>
        
        {/* 右侧：AI建议（传递左侧高度） */}
        {showAISuggestion && (
          <AISuggestion 
            content={loadingAI ? t('loanApplication.aiLoading') : aiSuggestion} 
            onClose={() => setShowAISuggestion(false)}
            maxHeight={formContentHeight}
          />
        )}
      </div>
    </div>
  );
};

export default LoanApplicationConfirm;