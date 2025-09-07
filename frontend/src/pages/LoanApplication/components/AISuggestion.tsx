// src/pages/LoanApplication/components/AISuggestion.tsx
import React from 'react';
import { useTranslation } from 'react-i18next';
import ReactMarkdown from 'react-markdown'; // 导入Markdown解析组件
import styles from '../LoanApplicationConfirm.module.css';

interface AISuggestionProps {
  content: string;
  onClose: () => void;
  maxHeight: number;
}

const AISuggestion: React.FC<AISuggestionProps> = ({ content, onClose, maxHeight }) => {
  const { t } = useTranslation();
  
  return (
    <div 
      className={styles.aiSuggestionPanel} 
      style={{ maxHeight: `${maxHeight}px` }}
    >
      <div className={styles.aiHeader}>
        <h3>{t('loanApplication.aiSuggestionTitle')}</h3>
        <button className={styles.closeButton} onClick={onClose}>×</button>
      </div>
      <div className={styles.aiContent}>
        {content ? (
          // 使用ReactMarkdown解析Markdown内容
          <ReactMarkdown>{content}</ReactMarkdown>
        ) : (
          <p>{t('loanApplication.aiLoading')}</p>
        )}
      </div>
    </div>
  );
};

export default AISuggestion;