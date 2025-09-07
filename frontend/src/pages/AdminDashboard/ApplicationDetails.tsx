// src/pages/AdminDashboard/ApplicationDetails.tsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import styles from './ApplicationList.module.css';
import { getLoanApplicationDetails } from '../../services/adminService';

// 定义与MongoDB结构匹配的类型
interface Document {
  id: string;
  name: string;
  type: string;
  url: string;
}

interface PersonalInfo {
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

interface CarSelection {
  carBrand: string;
  carModel: string;
  carYear: number;
  carType: 'sedan' | 'suv' | 'electric' | 'hybrid';
  carPrice: number;
}

interface LoanDetails {
  downPayment: number;
  downPaymentAmount: number;
  loanAmount: number;
  interestRate: number;
  loanTerm: number;
  loanStartDate: string;
  loanEndDate: string;
  repaymentFrequency: 'monthly' | 'quarterly' | 'yearly';
  monthlyPayment: number;
  repaymentDate: number;
  repaymentMethod: 'equalPrincipalInterest' | 'equalPrincipal';
}

interface FraudDetectionResult {
  is_suspicious: boolean;
  suspicious_items: string[];
  confidence: number;
  recommendation: string;
}

interface CreditRatingResult {
  score: number;
}

interface LoanApplication {
  _id: string;
  application_id: string;
  user_id: string;
  status: string;
  personalInfo: PersonalInfo;
  carSelection: CarSelection;
  loanDetails: LoanDetails;
  documents: {
    idCard: Document;
    creditReport: Document;
    salarySlip: Document;
    employmentProof: Document;
  };
  created_at: string;
  updated_at: string;
  compliance_check_status: string;
  compliance_result: string;
  credit_rating_result: CreditRatingResult;
  data_collection_status: string;
  decision_result: string;
  fraud_detection_result: FraudDetectionResult;
  fraud_detection_status: string;
  thread_id: string;
}

interface WorkflowStep {
  name: string;
  label: string;
  status: string;
  result: string | string[];
}

const ApplicationDetails: React.FC = () => {
  const { t } = useTranslation();
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [application, setApplication] = useState<LoanApplication | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) {
      setError(t('adminDashboard.invalidId'));
      setLoading(false);
      return;
    }

    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await getLoanApplicationDetails(id);
        setApplication(response.data);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch application details:', err);
        setError(t('adminDashboard.fetchDetailsError'));
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [id, t]);

  const handleBack = () => {
    navigate('/admin-dashboard');
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleString();
  };

  // 构建工作流程步骤数据
  const getWorkflowSteps = (): WorkflowStep[] => {
    if (!application) return [];
    
    return [
      {
        name: 'compliance_check',
        label: t('adminDashboard.workflow.complianceCheck'),
        status: application.compliance_check_status,
        result: application.compliance_result
      },
      {
        name: 'data_collection',
        label: t('adminDashboard.workflow.dataCollection'),
        status: application.data_collection_status,
        result: t('adminDashboard.workflow.dataCollectionCompleted')
      },
      {
        name: 'fraud_detection',
        label: t('adminDashboard.workflow.fraudDetection'),
        status: application.fraud_detection_status,
        result: application.fraud_detection_result.suspicious_items
      }
    ];
  };

  const getStatusClass = (status: string) => {
    switch (status.toLowerCase()) {
      case 'approved':
        return styles.statusApproved;
      case 'completed':
        return styles.statusCompleted;
      case 'rejected':
        return styles.statusRejected;
      default:
        return styles.statusPending;
    }
  };

  if (loading) {
    return <div className={styles.loading}>{t('loading')}</div>;
  }

  if (error || !application) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>{error || t('adminDashboard.applicationNotFound')}</div>
        <button className={styles.backButton} onClick={handleBack}>
          {t('adminDashboard.backToList')}
        </button>
      </div>
    );
  }

  const workflowSteps = getWorkflowSteps();

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>{t('adminDashboard.applicationDetails')}</h1>
        <button className={styles.backButton} onClick={handleBack}>
          {t('adminDashboard.backToList')}
        </button>
      </div>

      <div className={styles.detailsContainer}>
        {/* 申请基本信息卡片 */}
        <div className={styles.infoCard}>
          <h2>{t('adminDashboard.basicInfo')}</h2>
          <div className={styles.infoGrid}>
            <div className={styles.infoItem}>
              <span className={styles.label}>{t('adminDashboard.applicationId')}:</span>
              <span>{application.application_id}</span>
            </div>
            <div className={styles.infoItem}>
              <span className={styles.label}>{t('adminDashboard.status')}:</span>
              <span className={`${styles.statusBadge} ${styles[`status${application.status}`]}`}>
                {t(`loanApplication.status.${application.status}`) || application.status}
              </span>
            </div>
            <div className={styles.infoItem}>
              <span className={styles.label}>{t('adminDashboard.createdAt')}:</span>
              <span>{formatDate(application.created_at)}</span>
            </div>
            <div className={styles.infoItem}>
              <span className={styles.label}>{t('adminDashboard.updatedAt')}:</span>
              <span>{formatDate(application.updated_at)}</span>
            </div>
            <div className={styles.infoItem}>
              <span className={styles.label}>{t('adminDashboard.userId')}:</span>
              <span>{application.user_id}</span>
            </div>
          </div>
        </div>

        {/* 个人信息 */}
        <div className={styles.infoCard}>
          <h2>{t('loanApplication.personalInfo.title')}</h2>
          <div className={styles.infoGrid}>
            <div className={styles.infoItem}>
              <span className={styles.label}>{t('loanApplication.personalInfo.fullName')}:</span>
              <span>{application.personalInfo.fullName}</span>
            </div>
            <div className={styles.infoItem}>
              <span className={styles.label}>{t('loanApplication.personalInfo.idNumber')}:</span>
              <span>{application.personalInfo.idNumber}</span>
            </div>
            <div className={styles.infoItem}>
              <span className={styles.label}>{t('loanApplication.personalInfo.phoneNumber')}:</span>
              <span>{application.personalInfo.phoneNumber}</span>
            </div>
            <div className={styles.infoItem}>
              <span className={styles.label}>{t('loanApplication.personalInfo.email')}:</span>
              <span>{application.personalInfo.email}</span>
            </div>
            <div className={styles.infoItem}>
              <span className={styles.label}>{t('loanApplication.personalInfo.address')}:</span>
              <span>{application.personalInfo.address}</span>
            </div>
            <div className={styles.infoItem}>
              <span className={styles.label}>{t('loanApplication.personalInfo.employmentStatus')}:</span>
              <span>{t(`loanApplication.personalInfo.employmentStatus.${application.personalInfo.employmentStatus}`)}</span>
            </div>
            <div className={styles.infoItem}>
              <span className={styles.label}>{t('loanApplication.personalInfo.monthlyIncome')}:</span>
              <span>{application.personalInfo.monthlyIncome}</span>
            </div>
            <div className={styles.infoItem}>
              <span className={styles.label}>{t('loanApplication.personalInfo.accountHolderName')}:</span>
              <span>{application.personalInfo.accountHolderName}</span>
            </div>
            <div className={styles.infoItem}>
              <span className={styles.label}>{t('loanApplication.personalInfo.accountNumber')}:</span>
              <span>{application.personalInfo.accountNumber}</span>
            </div>
            <div className={styles.infoItem}>
              <span className={styles.label}>{t('loanApplication.personalInfo.bankName')}:</span>
              <span>{application.personalInfo.bankName}</span>
            </div>
          </div>
        </div>

        {/* 车辆信息 */}
        <div className={styles.infoCard}>
          <h2>{t('loanApplication.carSelection.title')}</h2>
          <div className={styles.infoGrid}>
            <div className={styles.infoItem}>
              <span className={styles.label}>{t('loanApplication.carSelection.carBrand')}:</span>
              <span>{application.carSelection.carBrand}</span>
            </div>
            <div className={styles.infoItem}>
              <span className={styles.label}>{t('loanApplication.carSelection.carModel')}:</span>
              <span>{application.carSelection.carModel}</span>
            </div>
            <div className={styles.infoItem}>
              <span className={styles.label}>{t('loanApplication.carSelection.carYear')}:</span>
              <span>{application.carSelection.carYear}</span>
            </div>
            <div className={styles.infoItem}>
              <span className={styles.label}>{t('loanApplication.carSelection.carType')}:</span>
              <span>{t(`loanApplication.carSelection.carType.${application.carSelection.carType}`)}</span>
            </div>
            <div className={styles.infoItem}>
              <span className={styles.label}>{t('loanApplication.carSelection.carPrice')}:</span>
              <span>{application.carSelection.carPrice}</span>
            </div>
          </div>
        </div>

        {/* 贷款信息 */}
        <div className={styles.infoCard}>
          <h2>{t('loanApplication.loanDetails.title')}</h2>
          <div className={styles.infoGrid}>
            <div className={styles.infoItem}>
              <span className={styles.label}>{t('loanApplication.loanDetails.downPayment')}:</span>
              <span>{application.loanDetails.downPayment}%</span>
            </div>
            <div className={styles.infoItem}>
              <span className={styles.label}>{t('loanApplication.loanDetails.downPaymentAmount')}:</span>
              <span>{application.loanDetails.downPaymentAmount}</span>
            </div>
            <div className={styles.infoItem}>
              <span className={styles.label}>{t('loanApplication.loanDetails.loanAmount')}:</span>
              <span>{application.loanDetails.loanAmount}</span>
            </div>
            <div className={styles.infoItem}>
              <span className={styles.label}>{t('loanApplication.loanDetails.interestRate')}:</span>
              <span>{application.loanDetails.interestRate}%</span>
            </div>
            <div className={styles.infoItem}>
              <span className={styles.label}>{t('loanApplication.loanDetails.loanTerm')}:</span>
              <span>{application.loanDetails.loanTerm} {t('home.finance.calculator.months')}</span>
            </div>
            <div className={styles.infoItem}>
              <span className={styles.label}>{t('loanApplication.loanDetails.monthlyPayment')}:</span>
              <span>{application.loanDetails.monthlyPayment}</span>
            </div>
            <div className={styles.infoItem}>
              <span className={styles.label}>{t('loanApplication.loanDetails.repaymentMethod')}:</span>
              <span>{t(`loanApplication.loanDetails.${application.loanDetails.repaymentMethod}`)}</span>
            </div>
            <div className={styles.infoItem}>
              <span className={styles.label}>{t('loanApplication.loanDetails.repaymentFrequency')}:</span>
              <span>{t(`loanApplication.loanDetails.repaymentFrequency.${application.loanDetails.repaymentFrequency}`)}</span>
            </div>
            <div className={styles.infoItem}>
              <span className={styles.label}>{t('loanApplication.loanDetails.repaymentDate')}:</span>
              <span>{application.loanDetails.repaymentDate} {t('adminDashboard.dayOfMonth')}</span>
            </div>
          </div>
        </div>

        {/* 提交文件 */}
        <div className={styles.infoCard}>
          <h2>{t('loanApplication.documents.title')}</h2>
          <div className={styles.documentsGrid}>
            <div className={styles.documentItem}>
              <span className={styles.label}>{t('loanApplication.documents.idCardTitle')}:</span>
              {application.documents.idCard ? (
                <a 
                  href={application.documents.idCard.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className={styles.documentLink}
                >
                  {application.documents.idCard.name}
                </a>
              ) : (
                <span className={styles.noDocument}>{t('loanApplication.documents.notUploaded')}</span>
              )}
            </div>
            <div className={styles.documentItem}>
              <span className={styles.label}>{t('loanApplication.documents.creditReportTitle')}:</span>
              {application.documents.creditReport ? (
                <a 
                  href={application.documents.creditReport.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className={styles.documentLink}
                >
                  {application.documents.creditReport.name}
                </a>
              ) : (
                <span className={styles.noDocument}>{t('loanApplication.documents.notUploaded')}</span>
              )}
            </div>
            <div className={styles.documentItem}>
              <span className={styles.label}>{t('loanApplication.documents.salarySlipTitle')}:</span>
              {application.documents.salarySlip ? (
                <a 
                  href={application.documents.salarySlip.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className={styles.documentLink}
                >
                  {application.documents.salarySlip.name}
                </a>
              ) : (
                <span className={styles.noDocument}>{t('loanApplication.documents.notUploaded')}</span>
              )}
            </div>
            <div className={styles.documentItem}>
              <span className={styles.label}>{t('loanApplication.documents.employmentProofTitle')}:</span>
              {application.documents.employmentProof ? (
                <a 
                  href={application.documents.employmentProof.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className={styles.documentLink}
                >
                  {application.documents.employmentProof.name}
                </a>
              ) : (
                <span className={styles.noDocument}>{t('loanApplication.documents.notUploaded')}</span>
              )}
            </div>
          </div>
        </div>

        {/* 申请流程列表 */}
        <div className={styles.infoCard}>
          <h2>{t('adminDashboard.workflow.title')}</h2>
          <div className={styles.workflowTableContainer}>
            <table className={styles.workflowTable}>
              <thead>
                <tr>
                  <th>{t('adminDashboard.workflow.process')}</th>
                  <th>{t('adminDashboard.workflow.status')}</th>
                  <th>{t('adminDashboard.workflow.result')}</th>
                </tr>
              </thead>
              <tbody>
                {workflowSteps.map((step, index) => (
                  <tr key={index}>
                    <td>{step.label}</td>
                    <td>
                      <span className={`${styles.statusBadge} ${getStatusClass(step.status)}`}>
                        {t(`adminDashboard.workflow.status.${step.status}`) || step.status}
                      </span>
                    </td>
                    <td className={styles.resultCell}>
                      {Array.isArray(step.result) ? (
                        <ul className={styles.resultList}>
                          {step.result.map((item, i) => (
                            <li key={i}>{item}</li>
                          ))}
                        </ul>
                      ) : (
                        <div className={styles.resultText}>{step.result}</div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* 信用评分信息 */}
        {application.credit_rating_result && (
          <div className={styles.infoCard}>
            <h2>{t('adminDashboard.creditRating.title')}</h2>
            <div className={styles.infoGrid}>
              <div className={styles.infoItem}>
                <span className={styles.label}>{t('adminDashboard.creditRating.score')}:</span>
                <span className={styles.creditScore}>{application.credit_rating_result.score}</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ApplicationDetails;