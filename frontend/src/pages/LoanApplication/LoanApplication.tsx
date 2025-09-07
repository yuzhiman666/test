import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import styles from './LoanApplication.module.css';
import PersonalInfoComponent from './components/PersonalInfo.tsx';
import CarSelectionComponent from './components/CarSelection.tsx';
import LoanDetailsComponent from './components/LoanDetails.tsx';
// import DocumentUpload from './components/DocumentUpload.tsx';
import { saveDraft, getLoanApplication} from '../../services/loanService.ts';
import { getCurrentUser } from '../../services/authService.ts';
import { CarSelection, LoanApplication as LoanApplicationType, LoanDetails, PersonalInfo, Document } from '../../types/loan.ts';
import FileUpload from './components/FileUpload.tsx'; // 导入FileUpload组件
import { useNavigate } from 'react-router-dom';

// 提取初始表单数据为函数，减少冗余
const getInitialFormData = (): Partial<LoanApplicationType> => ({
  personalInfo: {
    fullName: '',
    idNumber: '',
    phoneNumber: '',
    email: '',
    address: '',
    employmentStatus: 'employed',
    monthlyIncome: 0,
    accountHolderName: '',
    accountNumber: '',
    bankName: ''
  },
  carSelection: {
    carBrand: '',
    carBrandLabel:'',
    carModel: '',
    carYear: 0,
    carType: 'sedan',
    carPrice: 0
  },
  loanDetails: {
    downPayment: 0,
    downPaymentAmount: 0,
    loanAmount: 0,
    interestRate: 0,
    loanTerm: 0,
    loanStartDate: '',
    loanEndDate: '',
    repaymentFrequency: 'monthly',
    monthlyPayment: 0,
    repaymentDate: 1,
    repaymentMethod: 'equalPrincipalInterest'
  },
  documents: {
    idCard: null,
    creditReport: null,
    salarySlip: null,
    employmentProof: null
  }
});

// 验证表单数据完整性
const validateForm = (formData: Partial<LoanApplicationType>): boolean => {
  const { personalInfo, carSelection, loanDetails } = formData;
  
  // 验证个人信息必填项
  if (!personalInfo?.fullName || !personalInfo.idNumber || !personalInfo.phoneNumber) {
    alert(t('loanApplication.validation.personalInfoRequired'));
    return false;
  }
  
  // 验证车辆信息必填项
  if (!carSelection?.carBrand || !carSelection.carModel || !carSelection.carPrice) {
    alert(t('loanApplication.validation.carInfoRequired'));
    return false;
  }
  
  // 验证贷款信息必填项
  if (!loanDetails?.downPayment || !loanDetails.loanTerm || !loanDetails.interestRate) {
    alert(t('loanApplication.validation.loanInfoRequired'));
    return false;
  }
  
  return true;
};

const LoanApplication: React.FC = () => {
  const { t } = useTranslation();
  // 获取当前用户信息，其中currentUser.id已从后端获取，为邮箱@前的部分（如zhangsan）
  const currentUser = getCurrentUser();
  const navigate = useNavigate();
  
  // 组件内部状态定义
  const [formData, setFormData] = useState<Partial<LoanApplicationType>>(getInitialFormData());
  const [isEditing, setIsEditing] = useState(true);
  const [applicationId, setApplicationId] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  
  // 处理文件上传的回调函数
  const handleFileChange = (type: string, file: Document | null) => {
    if (!isEditing) {
      console.log('编辑模式已关闭，无法上传文件');
      return;
    }
    setFormData(prev => ({
      ...prev,
      documents: {
        ...prev.documents,
        [type]: file
      }
    }));
  };
  
  // 加载草稿数据 - 使用currentUser.id（从邮箱提取的userid）关联用户的贷款申请
  useEffect(() => {
    // 验证用户信息，确保已登录且userid有效
    if (!currentUser?.id) {
      console.log('用户未登录或userid无效');
      return;
    }
    
    console.log('当前用户ID (从邮箱提取的userid):', currentUser.id);
    console.log('关联的用户邮箱:', currentUser.email);
    
    const loadDraft = async () => {
      try {
        setLoading(true);
        // 调用API获取当前用户（通过userid）的贷款申请草稿
        const response = await getLoanApplication(currentUser.id);
        if (response.data) {
          setFormData(response.data);
          setApplicationId(response.data._id);
          setIsEditing(response.data.status !== '已提交');
        }
      } catch (error) {
        console.log('未找到草稿，初始化新表单');
        if (error.response?.status === 404) {
          setFormData(getInitialFormData());
        }
      } finally {
        setLoading(false);
      }
    };
    
    // 添加防抖，避免短时间内多次调用
    const timer = setTimeout(loadDraft, 300);
    return () => clearTimeout(timer);
  }, [currentUser?.id]);  // 仅监听userid变化，确保用户身份唯一
  
  // 处理子组件数据变更
  const handleInputChange = (
    section: 'personalInfo' | 'carSelection' | 'loanDetails',
    data: Partial<PersonalInfo> | Partial<CarSelection> | Partial<LoanDetails>
  ) => {
    if (!isEditing) return;
    setFormData(prev => ({
      ...prev,
      [section]: { ...prev[section], ...data }
    }));
  };
  
  // 重置表单
  const handleReset = () => {
    if (window.confirm(t('loanApplication.confirmReset'))) {
      setFormData(getInitialFormData());
    }
  };
  
  // 构建提交 payload 的辅助函数 - 确保使用正确的userid
  const buildPayload = (
    status: 'Draft' | 'InReview' | 'Submitted'
  ): Omit<LoanApplicationType, "_id" | "createdAt" | "updatedAt"> => {
    // 映射英文状态到中文状态
    const statusMap: Record<'Draft' | 'InReview' | 'Submitted', "Draft" | "InReview" | "Submitted"> = {
      Draft: 'Draft',
      InReview: 'InReview',
      Submitted: 'Submitted'
    };
    
    return {
      ...formData,
      // 使用从后端获取的userid（邮箱@前的部分）
      applicationId:applicationId,
      userId: currentUser?.id,
      status: statusMap[status],
      personalInfo: { ...getInitialFormData().personalInfo, ...formData.personalInfo },
      carSelection: { ...getInitialFormData().carSelection, ...formData.carSelection },
      loanDetails: { ...getInitialFormData().loanDetails, ...formData.loanDetails },
      documents: formData.documents ?? getInitialFormData().documents
    };
  };
  
  // console.log('当前用于关联的userid:', currentUser?.id);
  
  // 保存草稿 - 关联当前用户的userid
  const handleSave = async () => {
    if (!currentUser?.id) {
      alert(t('loanApplication.loginRequired'));
      return;
    }
    
    try {
      setLoading(true);
      // const payload = buildPayload('Draft');
      const payload = {
        ...buildPayload('Draft')
      };
      const response = await saveDraft(payload);
      setApplicationId(response.data.application_id);
      alert(t('loanApplication.saveSuccess'));
    } catch (error) {
      console.error('保存草稿错误:', error);
      alert(t('loanApplication.saveFailed'));
    } finally {
      setLoading(false);
    }
  };
  
  const handleSubmit = () => {
    if (!currentUser?.id) {
      alert(t('loanApplication.loginRequired'));
      return;
    }
    if (!validateForm(formData)) return;
    
    // 确保formData是可序列化的对象
    const sanitizedFormData = JSON.parse(JSON.stringify(formData));
    
    // 使用replace避免历史记录问题
    navigate('/loan-application/confirm', {
      state: {
        formData: sanitizedFormData,
        currentUser: { ...currentUser },
        applicationId: applicationId
      },
      replace: true
    });
  };
    
  if (loading) {
    return <div className={styles.loading}>{t('loading')}</div>;
  }
  
  if (!currentUser?.id) {
    return <div className={styles.accessDenied}>{t('loanApplication.loginRequired')}</div>;
  }
  
  return (
    <div className={styles.container}>
      <h1>{t('loanApplication.title')}</h1>
      
      <div className={styles.formContainer}>
        <div className={styles.formContent}>
          {/* 个人信息组件 */}
          <PersonalInfoComponent
            data={formData.personalInfo || getInitialFormData().personalInfo} 
            onChange={(data: Partial<PersonalInfo>) => handleInputChange('personalInfo', data)}
            disabled={!isEditing}
          />
          
          {/* 车辆信息组件 */}
          <CarSelectionComponent  
            data={formData.carSelection || getInitialFormData().carSelection} 
            onChange={(data: Partial<CarSelection>) => handleInputChange('carSelection', data)}
            disabled={!isEditing}
          />
          
          {/* 贷款信息组件 */}
          <LoanDetailsComponent 
            data={formData.loanDetails || getInitialFormData().loanDetails} 
            carPrice={formData.carSelection?.carPrice || 0}
            onChange={(data: Partial<LoanDetails>) => handleInputChange('loanDetails', data)}
            disabled={!isEditing}
          />
          
          {/* 文件上传组件 */}
          <FileUpload 
            fileType="idCard"
            titleKey="loanApplication.documents.idCardTitle"
            file={formData.documents?.idCard || null}
            onFileChange={(file) => handleFileChange('idCard', file)}
            disabled={!isEditing}
          />

          <FileUpload 
            fileType="creditReport"
            titleKey="loanApplication.documents.creditReportTitle"
            file={formData.documents?.creditReport || null}
            onFileChange={(file) => handleFileChange('creditReport', file)}
            disabled={!isEditing}
          />

          <FileUpload 
            fileType="salarySlip"
            titleKey="loanApplication.documents.salarySlipTitle"
            file={formData.documents?.salarySlip || null}
            onFileChange={(file) => handleFileChange('salarySlip', file)}
            disabled={!isEditing}
          />

          <FileUpload 
            fileType="employmentProof"
            titleKey="loanApplication.documents.employmentProofTitle"
            file={formData.documents?.employmentProof || null}
            onFileChange={(file) => handleFileChange('employmentProof', file)}
            disabled={!isEditing}
          />
          
          <div className={styles.actionButtons}>
              <button 
                className={styles.resetButton} 
                onClick={handleReset}
                disabled={loading}
              >
                {t('loanApplication.reset')}
              </button>
              <button 
                className={styles.saveButton} 
                onClick={handleSave}
                disabled={loading}
              >
                {t('loanApplication.save')}
              </button>
              <button 
                className={styles.submitButton} 
                onClick={handleSubmit}
                disabled={loading}
              >
                {t('loanApplication.confirm')}
              </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoanApplication;

// 合理实现 t 函数，优先使用 useTranslation 的 t
function t(key: string): string {
  // 可以根据需要自定义 fallback 或直接返回 key
  // 这里简单返回 key，实际项目应使用 i18next 或 context
  return key;
}
