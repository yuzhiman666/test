import React from 'react';
import { useTranslation } from 'react-i18next';
// Removed invalid import of IconType
import { 
  ArrowUpOutlined, 
  ArrowDownOutlined,
  ArrowRightOutlined
} from '@ant-design/icons';
import styles from './StatisticCard.module.css';

interface StatisticCardProps {
  title: string;
  value: string | number;
  icon: string | React.ComponentType | React.ReactElement;
  color: string;
  trend?: 'up' | 'down' | 'same';
  trendPercent?: number;
}

const StatisticCard: React.FC<StatisticCardProps> = ({
  title,
  value,
  icon: Icon,
  color,
  trend = 'same',
  trendPercent = 0
}) => {
  const { t } = useTranslation();
  
  // 动态导入Ant Design图标
  const getIcon = () => {
    if (typeof Icon === 'string') {
      // 这里简化处理，实际项目中可能需要动态导入
      const IconComponent = require('@ant-design/icons')[Icon];
      return <IconComponent />;
    }
    if (React.isValidElement(Icon)) {
      return Icon;
    }
    if (typeof Icon === 'function') {
      const IconComponent = Icon as React.ComponentType;
      return <IconComponent />;
    }
    return null;
  };

  // 获取趋势图标和样式
  const getTrendIndicator = () => {
    if (trend === 'up') {
      return (
        <div className={styles.trendUp}>
          <ArrowUpOutlined />
          <span>{trendPercent}%</span>
          <span className={styles.trendText}>{t('trend.increase')}</span>
        </div>
      );
    } else if (trend === 'down') {
      return (
        <div className={styles.trendDown}>
          <ArrowDownOutlined />
          <span>{trendPercent}%</span>
          <span className={styles.trendText}>{t('trend.decrease')}</span>
        </div>
      );
    } else {
      return (
        <div className={styles.trendSame}>
          <ArrowRightOutlined />
          <span className={styles.trendText}>{t('trend.same')}</span>
        </div>
      );
    }
  };

  return (
    <div className={styles.card} style={{ borderLeft: `4px solid ${color}` }}>
      <div className={styles.header}>
        <h3 className={styles.title}>{title}</h3>
        <div className={styles.iconContainer} style={{ backgroundColor: `${color}20` }}>
          <div className={styles.icon} style={{ color }}>
            {getIcon()}
          </div>
        </div>
      </div>
      
      <div className={styles.value}>{value}</div>
      
      <div className={styles.trend}>
        {getTrendIndicator()}
      </div>
    </div>
  );
};

export default StatisticCard;