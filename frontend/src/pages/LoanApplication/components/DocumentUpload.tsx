// src/pages/LoanApplication/components/DocumentUpload.tsx
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styles from '../LoanApplication.module.css';
import { Document } from '../../../types/loan.ts';

interface DocumentUploadProps {
  documents: Document[];
  onUpload: (documents: Document[]) => void;
  disabled: boolean;
}

const DocumentUpload: React.FC<DocumentUploadProps> = ({ documents, onUpload, disabled }) => {
  const { t } = useTranslation();
  const [preview, setPreview] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    
    const file = e.target.files[0];
    const reader = new FileReader();
    
    reader.onloadend = () => {
      const newDoc: Document = {
        id: Date.now().toString(),
        name: file.name,
        type: file.type,
        url: reader.result as string
      };
      
      const updatedDocs = [...documents, newDoc];
      onUpload(updatedDocs);
      setPreview(reader.result as string);
    };
    
    reader.readAsDataURL(file);
  };

  const handleRemove = (id: string) => {
    const updatedDocs = documents.filter(doc => doc.id !== id);
    onUpload(updatedDocs);
  };

  return (
    <div className={styles.section}>
      <h3>{t('loanApplication.documents.title')}</h3>
      
      <div className={styles.uploadArea}>
        <input
          type="file"
          accept=".jpg,.jpeg,.pdf,.docx"
          onChange={handleFileChange}
          disabled={disabled}
          className={styles.fileInput}
        />
        
        <div className={styles.uploadedFiles}>
          {documents.map(doc => (
            <div key={doc.id} className={styles.fileItem}>
              <span>{doc.name}</span>
              <button 
                onClick={() => handleRemove(doc.id)} 
                disabled={disabled}
                className={styles.removeButton}
              >
                {t('loanApplication.documents.remove')}
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default DocumentUpload;