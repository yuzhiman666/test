import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { 
  Modal, 
  Button, 
  Row, 
  Col, 
  Typography, 
  Input, 
  Divider, 
  Card, 
  Space, 
  Tag  // 用Tag替代Chip（antd低版本无Chip时）
} from 'antd';
import { 
  CheckCircleOutlined, 
  CloseCircleOutlined,
  InfoOutlined,
  CarOutlined,
  HomeOutlined,
  CreditCardOutlined,
  CalendarOutlined
} from '@ant-design/icons';
import styles from './CustomerDialog.module.css';
import { Customer } from '../../../types/admin.ts';

const { Title, Paragraph, Text } = Typography;

interface CustomerDialogProps {
  visible: boolean;
  customer: Customer;
  mode: 'view' | 'edit';
  onClose: () => void;
  onAudit: (result: 'Approve' | 'Reject') => Promise<void>;
  onSuccess?: () => void;
}

const CustomerDialog: React.FC<CustomerDialogProps> = ({
  visible,
  customer,
  mode,
  onClose,
  onAudit,
  onSuccess
}) => {
  const { t } = useTranslation();
  const [feedback, setFeedback] = useState('');
  const [loading, setLoading] = useState(false);

  // 处理审核操作
  const handleAudit = async (result: 'Approve' | 'Reject') => {
    if (result === 'Reject' && !feedback.trim() && mode === 'edit') {
      alert(t('validation.rejectReasonRequired'));
      return;
    }

    try {
      setLoading(true);
      await onAudit(result);
      onSuccess?.();
      onClose();
    } catch (error) {
      console.error('审核操作失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 格式化日期
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  // 状态标签颜色映射（适配antd Tag组件）
  const getStatusColor = (status: string) => {
    switch (status) {
      case '已批准': return 'success';
      case '已拒绝': return 'error';
      case '审核中': return 'processing';
      case '已提交': return 'warning';
      default: return 'default';
    }
  };

  return (
    <Modal
      title={
        <div className={styles.titleContainer}>
          <Title level={5} style={{ margin: 0 }}>
            {mode === 'view' 
              ? t('admin.dialog.viewTitle', { name: customer.name }) 
              : t('admin.dialog.editTitle', { name: customer.name })}
          </Title>
          {/* 用Tag替代Chip，antd全版本兼容 */}
          <Tag 
            color={getStatusColor(customer.applicationStatus)}
            className={styles.statusChip}
          >
            {t(`status.${customer.applicationStatus}`)}
          </Tag>
        </div>
      }
      visible={visible}  // 修正属性名：open -> visible（antd Modal标准属性）
      onCancel={onClose}
      width="80%"
      // 移除maxWidth属性（antd Modal无此属性），通过样式控制最大宽度
      style={{ maxWidth: '1000px' }}
      footer={[
        <Button 
          key="close" 
          onClick={onClose} 
          disabled={loading}
        >
          {t('common.close')}
        </Button>,
        ...(mode === 'edit' 
          ? [
              <Button 
                key="reject" 
                onClick={() => handleAudit('Reject')} 
                danger 
                icon={<CloseCircleOutlined />}
                disabled={loading}
              >
                {t('admin.actions.reject')}
              </Button>,
              <Button 
                key="approve" 
                onClick={() => handleAudit('Approve')} 
                type="primary" 
                icon={<CheckCircleOutlined />}
                disabled={loading}
              >
                {t('admin.actions.approve')}
              </Button>
            ] 
          : [])
      ]}
    >
      <div className={styles.content}>
        <Row gutter={[16, 16]}>
          {/* 基本信息 */}
          <Col xs={24} md={12}>
            <Card className={styles.section}>
              <div className={styles.sectionHeader}>
                <InfoOutlined className={styles.sectionIcon} />
                <Title level={5} style={{ margin: 0 }}>{t('admin.dialog.basicInfo')}</Title>
              </div>
              
              <Divider style={{ margin: '12px 0' }} />
              
              <Space direction="vertical" size="middle" className={styles.infoGrid}>
                <div className={styles.infoItem}>
                  <Text strong className={styles.label}>{t('form.name')}:</Text>
                  <Paragraph style={{ margin: 0 }}>{customer.name}</Paragraph>
                </div>
                
                <div className={styles.infoItem}>
                  <Text strong className={styles.label}>{t('form.phone')}:</Text>
                  <Paragraph style={{ margin: 0 }}>{customer.phone}</Paragraph>
                </div>
                
                <div className={styles.infoItem}>
                  <Text strong className={styles.label}>{t('form.email')}:</Text>
                  <Paragraph style={{ margin: 0 }}>{customer.email}</Paragraph>
                </div>
                
                <div className={styles.infoItem}>
                  <Text strong className={styles.label}>{t('form.idNumber')}:</Text>
                  <Paragraph style={{ margin: 0 }}>
                    {customer.idNumber 
                      ? `${customer.idNumber.substr(0, 6)}********${customer.idNumber.substr(-4)}` 
                      : '-'}
                  </Paragraph>
                </div>
                
                <div className={styles.infoItem}>
                  <Text strong className={styles.label}>{t('form.address')}:</Text>
                  <Paragraph style={{ margin: 0 }}>{customer.address || '-'}</Paragraph>
                </div>
                
                <div className={styles.infoItem}>
                  <Text strong className={styles.label}>{t('form.monthlyIncome')}:</Text>
                  <Paragraph style={{ margin: 0 }}>¥{customer.monthlyIncome.toLocaleString()}</Paragraph>
                </div>
              </Space>
            </Card>
          </Col>
          
          {/* 车辆信息 */}
          <Col xs={24} md={12}>
            <Card className={styles.section}>
              <div className={styles.sectionHeader}>
                <CarOutlined className={styles.sectionIcon} />
                <Title level={5} style={{ margin: 0 }}>{t('admin.dialog.carInfo')}</Title>
              </div>
              
              <Divider style={{ margin: '12px 0' }} />
              
              <Space direction="vertical" size="middle" className={styles.infoGrid}>
                <div className={styles.infoItem}>
                  <Text strong className={styles.label}>{t('form.carBrand')}:</Text>
                  <Paragraph style={{ margin: 0 }}>{customer.carBrand}</Paragraph>
                </div>
                
                <div className={styles.infoItem}>
                  <Text strong className={styles.label}>{t('form.carModel')}:</Text>
                  <Paragraph style={{ margin: 0 }}>{customer.carModel}</Paragraph>
                </div>
                
                <div className={styles.infoItem}>
                  <Text strong className={styles.label}>{t('form.carPrice')}:</Text>
                  <Paragraph style={{ margin: 0 }}>¥{customer.carPrice.toLocaleString()}</Paragraph>
                </div>
                
                <div className={styles.infoItem}>
                  <Text strong className={styles.label}>{t('form.loanAmount')}:</Text>
                  <Paragraph style={{ margin: 0 }}>¥{customer.loanAmount.toLocaleString()}</Paragraph>
                </div>
                
                <div className={styles.infoItem}>
                  <Text strong className={styles.label}>{t('form.applicationDate')}:</Text>
                  <Paragraph style={{ margin: 0 }}>{formatDate(customer.createdAt)}</Paragraph>
                </div>
                
                {customer.auditResult && (
                  <div className={styles.infoItem}>
                    <Text strong className={styles.label}>{t('form.auditResult')}:</Text>
                    <Paragraph 
                      style={{ 
                        margin: 0,
                        color: customer.auditResult === 'Approve' ? '#52c41a' : '#f5222d'
                      }}
                    >
                      {t(`audit.${customer.auditResult}`)}
                    </Paragraph>
                  </div>
                )}
                
                {customer.auditTime && (
                  <div className={styles.infoItem}>
                    <Text strong className={styles.label}>{t('form.auditTime')}:</Text>
                    <Paragraph style={{ margin: 0 }}>{formatDate(customer.auditTime)}</Paragraph>
                  </div>
                )}
              </Space>
            </Card>
          </Col>
          
          {/* 审核反馈（仅编辑模式显示） */}
          {mode === 'edit' && (
            <Col xs={24}>
              <Card className={styles.section}>
                <div className={styles.sectionHeader}>
                  <InfoOutlined className={styles.sectionIcon} />
                  <Title level={5} style={{ margin: 0 }}>{t('admin.dialog.auditFeedback')}</Title>
                </div>
                
                <Divider style={{ margin: '12px 0' }} />
                
                <Input.TextArea
                  rows={4}
                  placeholder={t('admin.dialog.feedbackPlaceholder')}
                  value={feedback}
                  onChange={(e) => setFeedback(e.target.value)}
                  className={styles.feedbackField}
                />
                
                <Text type="secondary" className={styles.feedbackNote}>
                  {t('admin.dialog.feedbackNote')}
                </Text>
              </Card>
            </Col>
          )}
        </Row>
      </div>
    </Modal>
  );
};

export default CustomerDialog;