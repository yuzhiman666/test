// src/pages/LoanApplication/LoanApplication.tsx
import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import styles from './LoanApplication.module.css';
import PersonalInfo from './components/PersonalInfo.tsx';
import CarSelection from './components/CarSelection.tsx';
import LoanDetails from './components/LoanDetails.tsx';
import DocumentUpload from './components/DocumentUpload.tsx';
import AISuggestion from './components/AISuggestion.tsx';
import { submitLoanApplication, saveDraft, getLoanApplication } from '../../services/loanService.ts';

const LoanApplication: React.FC = () => {
  const { t } = useTranslation();
  const [formData, setFormData] = useState<any>({
    personalInfo: {},
    carSelection: {},
    loanDetails: {},
    documents: []
  });
  const [isSubmitted, setIsSubmitted] = useState<boolean>(false);
  const [isEditing, setIsEditing] = useState<boolean>(true);
  const [showAISuggestion, setShowAISuggestion] = useState<boolean>(false);
  const [aiSuggestion, setAiSuggestion] = useState<string>('');
  const [applicationId, setApplicationId] = useState<string>('');

  // 加载草稿数据
  useEffect(() => {
    const loadDraft = async () => {
      try {
        const response = await getLoanApplication();
        if (response.data.status === 'Draft') {
          setFormData(response.data);
          setApplicationId(response.data._id);
          setIsSubmitted(true);
        }
      } catch (error) {
        console.log('No draft found');
      }
    };
    loadDraft();
  }, []);

  const handleInputChange = (section: string, data: any) => {
    if (!isEditing) return;
    setFormData(prev => ({ ...prev, [section]: data }));
  };

  const handleDocumentUpload = (documents: any[]) => {
    if (!isEditing) return;
    setFormData(prev => ({ ...prev, documents }));
  };

  const handleReset = () => {
    if (window.confirm(t('loanApplication.confirmReset'))) {
      setFormData({
        personalInfo: {},
        carSelection: {},
        loanDetails: {},
        documents: []
      });
    }
  };

  const handleSave = async () => {
    try {
      const response = await saveDraft(formData);
      setApplicationId(response.data._id);
      alert(t('loanApplication.saveSuccess'));
    } catch (error) {
      alert(t('loanApplication.saveFailed'));
    }
  };

  const handleSubmit = async () => {
    try {
      const response = await submitLoanApplication(formData);
      setApplicationId(response.data._id);
      setIsSubmitted(true);
      setIsEditing(false);
      alert(t('loanApplication.submitSuccess'));
    } catch (error) {
      alert(t('loanApplication.submitFailed'));
    }
  };

  const handleGetAISuggestion = async () => {
    try {
      const response = await getAISuggestion(applicationId || 'draft');
      setAiSuggestion(response.data.analysis);
      setShowAISuggestion(true);
    } catch (error) {
      alert(t('loanApplication.aiError'));
    }
  };

  return (
    <div className={styles.container}>
      <h1>{t('loanApplication.title')}</h1>
      
      <div className={styles.formContainer}>
        <div className={styles.formContent}>
          <PersonalInfo 
            data={formData.personalInfo} 
            onChange={(data) => handleInputChange('personalInfo', data)}
            disabled={!isEditing}
          />
          
          <CarSelection 
            data={formData.carSelection} 
            onChange={(data) => handleInputChange('carSelection', data)}
            disabled={!isEditing}
          />
          
          <LoanDetails 
            data={formData.loanDetails} 
            onChange={(data) => handleInputChange('loanDetails', data)}
            disabled={!isEditing}
          />
          
          <DocumentUpload 
            documents={formData.documents} 
            onUpload={handleDocumentUpload}
            disabled={!isEditing}
          />
          
          <div className={styles.actionButtons}>
            {isEditing ? (
              <>
                <button 
                  className={styles.resetButton} 
                  onClick={handleReset}
                >
                  {t('loanApplication.reset')}
                </button>
                <button 
                  className={styles.saveButton} 
                  onClick={handleSave}
                >
                  {t('loanApplication.save')}
                </button>
                <button 
                  className={styles.submitButton} 
                  onClick={handleSubmit}
                >
                  {t('loanApplication.submit')}
                </button>
              </>
            ) : (
              <>
                <button 
                  className={styles.editButton} 
                  onClick={() => setIsEditing(true)}
                >
                  {t('loanApplication.edit')}
                </button>
                <button 
                  className={styles.aiButton} 
                  onClick={handleGetAISuggestion}
                >
                  {t('loanApplication.aiSuggestion')}
                </button>
                <button 
                  className={styles.submitButton} 
                  onClick={handleSubmit}
                >
                  {t('loanApplication.finalSubmit')}
                </button>
              </>
            )}
          </div>
        </div>
        
        {showAISuggestion && (
          <AISuggestion 
            content={aiSuggestion} 
            onClose={() => setShowAISuggestion(false)}
          />
        )}
      </div>
    </div>
  );
};

export default LoanApplication;