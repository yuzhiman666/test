import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styles from '../LoanApplication.module.css';

interface Document {
  id: string;
  name: string;
  type: string;
  url: string;
}

interface FileUploadProps {
  fileType: string;
  titleKey: string;
  file: Document | null;
  onFileChange: (file: Document | null) => void;
  disabled: boolean;
}

const FileUpload: React.FC<FileUploadProps> = ({ 
  fileType, 
  titleKey, 
  file, 
  onFileChange, 
  disabled 
}) => {
  const { t } = useTranslation();
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    try {
      if (!e.target.files || e.target.files.length === 0) {
        console.log('未选择文件');
        return;
      }
      const selectedFile = e.target.files[0];
      console.log('选中的文件:', selectedFile);

      // 检查文件类型
      const allowedTypes = ['image/jpeg', 'image/png', 'application/pdf','application/msword','application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
      if (!allowedTypes.includes(selectedFile.type)) {
        alert(t('loanApplication.documents.invalidType'));
        return;
      }

      const reader = new FileReader();
      reader.onloadend = () => {
        console.log('文件读取完成');
        if (typeof reader.result === 'string') {
          const newDoc: Document = {
            id: Date.now().toString(),
            name: selectedFile.name,
            type: fileType,
            url: reader.result,
          };
          onFileChange(newDoc); // 触发父组件回调
          setPreviewUrl(reader.result); // 更新预览
        } else {
          alert(t('loanApplication.documents.readFailed'));
        }
      };
      reader.readAsDataURL(selectedFile);
    } catch (error) {
      console.error('文件上传错误:', error);
      alert(t('loanApplication.documents.uploadError'));
    }
  };

  const handleRemove = () => {
    onFileChange(null);
    setPreviewUrl(null);
  };

  return (
    <div className={styles.documentSection}>
      <h3>{t(titleKey)}</h3>
      <div className={styles.uploadContainer}>
        {/* 自定义上传按钮：放在文件输入框上方 */}
        {/* 1. 修复按钮点击事件，确保能找到输入框 */}
        <button 
          type="button"
          className={styles.uploadButton}
          onClick={(e) => {
            e.preventDefault(); // 阻止默认行为
            const input = document.getElementById(`file-input-${fileType}`);
            if (input) {
              input.click(); // 强制触发点击
            } else {
              console.error(`File input with id "file-input-${fileType}" not found`);
            }
          }}
          disabled={disabled}
        >
          {file ? t('loanApplication.documents.replace') : t('loanApplication.documents.upload')}
        </button>

        {/* 2. 确保输入框可见且可交互 */}
        <input
          id={`file-input-${fileType}`}
          type="file"
          accept=".jpg,.jpeg,.pdf,.doc,.docx"
          onChange={handleFileSelect}
          disabled={disabled}
          className={styles.fileInput}
          style={{ display: 'none' }} // 明确隐藏，但保留可交互性
        />

        {/* 预览区域 */}
        {file && previewUrl && (
          <div className={styles.previewBox}>
            {previewUrl.startsWith('data:image') && (
              <img 
                src={previewUrl} 
                alt="File preview" 
                className={styles.previewImage} 
              />
            )}
            <p className={styles.fileName}>{file.name}</p>
            <button 
              onClick={handleRemove} 
              disabled={disabled}
              className={styles.removeBtn}
            >
              {t('loanApplication.documents.remove')}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default FileUpload;