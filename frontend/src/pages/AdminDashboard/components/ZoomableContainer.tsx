import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { 
  SearchOutlined,
  InfoOutlined
} from '@ant-design/icons';
import { Tooltip } from 'antd';
import styles from './ZoomableContainer.module.css';

interface ZoomableContainerProps {
  children: React.ReactNode;
  onZoom: () => void;
  title?: string;
}

const ZoomableContainer: React.FC<ZoomableContainerProps> = ({
  children,
  onZoom,
  title
}) => {
  const { t } = useTranslation();
  const [hovered, setHovered] = useState(false);

  return (
    <div 
      className={`${styles.container} ${hovered ? styles.hovered : ''}`}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      {title && (
        <div className={styles.header}>
          <h3 className={styles.title}>{title}</h3>
          <Tooltip title={t('zoom.zoomIn')}>
            <button 
              className={styles.zoomButton}
              onClick={(e) => {
                e.stopPropagation();
                onZoom();
              }}
              aria-label={t('zoom.zoomIn')}
            >
              <SearchOutlined />
            </button>
          </Tooltip>
        </div>
      )}
      
      <div className={styles.content} onClick={onZoom}>
        {children}
      </div>
      
      {hovered && !title && (
        <div className={styles.overlay}>
          <Tooltip title={t('zoom.zoomIn')}>
            <button 
              className={styles.overlayButton}
              onClick={(e) => {
                e.stopPropagation();
                onZoom();
              }}
              aria-label={t('zoom.zoomIn')}
            >
              <SearchOutlined />
              <span className={styles.overlayText}>{t('zoom.zoomIn')}</span>
            </button>
          </Tooltip>
        </div>
      )}
    </div>
  );
};

export default ZoomableContainer;