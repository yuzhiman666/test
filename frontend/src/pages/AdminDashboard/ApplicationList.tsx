// src/pages/AdminDashboard/AdminDashboard.tsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import styles from './ApplicationList.module.css';
import { getAllLoanApplications } from '../../services/adminService.ts';
import { LoanApplicationList } from '../../types/loan.ts';

const AdminDashboard: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [applications, setApplications] = useState<LoanApplicationList[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // 页面初始化时获取所有贷款申请
  useEffect(() => {
    const fetchApplications = async () => {
      try {
        setLoading(true);
        const response = await getAllLoanApplications();
        setApplications(response.data);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch loan applications:', err);
        setError(t('adminDashboard.fetchError'));
      } finally {
        setLoading(false);
      }
    };

    fetchApplications();
  }, [t]);

  // 查看详情
  const handleViewDetails = (id: string) => {
    navigate(`/admin-dashboard/details/${id}`);
  };

  // 格式化日期
  const formatDate = (dateString?: string) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleString();
  };

  // 状态标签样式映射
  const getStatusClass = (status: string) => {
    switch (status) {
      case 'Draft':
        return styles.statusDraft;
      case 'InReview':
        return styles.statusInReview;
      case 'Submitted':
        return styles.statusSubmitted;
      case 'Approved':
        return styles.statusApproved;
      case 'Rejected':
        return styles.statusRejected;
      default:
        return styles.statusDefault;
    }
  };

  if (loading) {
    return <div className={styles.loading}>{t('loading')}</div>;
  }

  if (error) {
    return <div className={styles.error}>{error}</div>;
  }

  return (
    <div className={styles.container}>
      <h1>{t('adminDashboard.title')}</h1>
      
      <div className={styles.tableContainer}>
        <table className={styles.applicationsTable}>
          <thead>
            <tr>
              <th>{t('adminDashboard.columns.applicationId')}</th>
              <th>{t('adminDashboard.columns.applicantName')}</th>
              <th>{t('adminDashboard.columns.applicationDate')}</th>
              <th>{t('adminDashboard.columns.status')}</th>
              <th>{t('adminDashboard.columns.actions')}</th>
            </tr>
          </thead>
          <tbody>
            {applications.length === 0 ? (
              <tr>
                <td colSpan={5} className={styles.noData}>
                  {t('adminDashboard.noApplications')}
                </td>
              </tr>
            ) : (
              applications.map(application => (
                <tr>
                  <td>{application.application_id}</td>
                  <td>{application.fullName}</td>
                  <td>{formatDate(application.createdAt)}</td>
                  <td>{application.status}</td>
                  <td>
                    <button 
                      className={styles.detailsButton}
                      onClick={() => handleViewDetails(application.application_id as string)}
                    >
                      {t('adminDashboard.viewDetails')}
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AdminDashboard;