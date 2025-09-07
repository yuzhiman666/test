import React, { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { 
  Table, 
  Button, 
  Checkbox, 
  Pagination, 
  Space, 
  Tooltip, 
  Input,
  Select,
  Spin,
  message
} from 'antd';
import type { ColumnsType } from 'antd/es/table'; // 单独导入表格列类型
import { 
  EditOutlined, 
  EyeOutlined, 
  DownloadOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  SearchOutlined
} from '@ant-design/icons';
import styles from './CustomerTable.module.css';
import CustomerDialog from './CustomerDialog.tsx';
import { 
  getCustomerList, 
  batchAuditApplications, 
  exportCustomers 
} from '../../../services/adminService';
import { Customer } from '../../../types/admin.ts';
import usePagination from '../../../hooks/usePagination.ts';

const { Option } = Select;
const { Search } = Input;

interface CustomerTableProps {
  isZoomed?: boolean;
  regionId?: string;
}

const CustomerTable: React.FC<CustomerTableProps> = ({ isZoomed = false, regionId }) => {
  const { t } = useTranslation();
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [selectedRows, setSelectedRows] = useState<string[]>([]);
  const [visibleDialog, setVisibleDialog] = useState(false);
  const [currentCustomer, setCurrentCustomer] = useState<Customer | null>(null);
  const [dialogMode, setDialogMode] = useState<'view' | 'edit'>('view');
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    search: '',
    status: '',
    auditResult: ''
  });
  const [messageApi, contextHolder] = message.useMessage();
  
  // 修复分页配置 - 与usePagination返回类型匹配
  const { 
    currentPage: page, 
    pageSize, 
    totalItems: total, 
    setCurrentPage: handlePageChange,
    setPageSize: onPageSizeChange,
    setTotalItems: setTotal
  } = usePagination({
    initialPage: 1,
    pageSize: 10
  });

  // 加载客户列表
  const loadCustomers = useCallback(async () => {
    try {
      setLoading(true);
      const response = await getCustomerList(
        page, 
        pageSize, 
        { ...filters, region: regionId }
      );
      setCustomers(response.data.items);
      setTotal(response.data.total);
    } catch (error) {
      console.error('Failed to load customers:', error);
      messageApi.error(t('notification.loadFailed'));
    } finally {
      setLoading(false);
    }
  }, [page, pageSize, filters, regionId, messageApi, t, setTotal]);

  useEffect(() => {
    loadCustomers();
  }, [loadCustomers]);

  // 处理行选择
  const handleRowSelection = (selectedKeys: string[]) => {
    setSelectedRows(selectedKeys);
  };

  // 处理查看
  const handleView = (customer: Customer) => {
    setCurrentCustomer(customer);
    setDialogMode('view');
    setVisibleDialog(true);
  };

  // 处理编辑
  const handleEdit = (customer: Customer) => {
    setCurrentCustomer(customer);
    setDialogMode('edit');
    setVisibleDialog(true);
  };

  // 处理审核结果
  const handleAuditResult = async (result: 'Approve' | 'Reject') => {
    if (!currentCustomer) return;
    
    try {
      // 调用API更新审核结果
      await batchAuditApplications([currentCustomer.id], result);
      
      // 刷新列表
      await loadCustomers();
      setVisibleDialog(false);
      messageApi.success(t(`notification.${result.toLowerCase()}Success`));
    } catch (error) {
      console.error('Failed to update audit result:', error);
      messageApi.error(t('notification.updateFailed'));
    }
  };

  // 批量审核
  const handleBatchAudit = async (result: 'Approve' | 'Reject') => {
    if (selectedRows.length === 0) {
      messageApi.warning(t('notification.selectItemsFirst'));
      return;
    }
    
    try {
      setLoading(true);
      await batchAuditApplications(selectedRows, result);
      
      // 刷新列表
      await loadCustomers();
      setSelectedRows([]);
      messageApi.success(t(`notification.batch${result}Success`, { count: selectedRows.length }));
    } catch (error) {
      console.error('Failed to batch update audit results:', error);
      messageApi.error(t('notification.batchUpdateFailed'));
    } finally {
      setLoading(false);
    }
  };

  // 导出Excel
  const handleExport = async () => {
    try {
      setLoading(true);
      const response = await exportCustomers(selectedRows.length > 0 ? selectedRows : undefined);
      
      // 创建下载链接
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `customers_${new Date().toISOString()}.xlsx`);
      document.body.appendChild(link);
      link.click();
      messageApi.success(t('notification.exportSuccess'));
    } catch (error) {
      console.error('Failed to export customers:', error);
      messageApi.error(t('notification.exportFailed'));
    } finally {
      setLoading(false);
    }
  };

  // 处理搜索
  const handleSearch = (value: string) => {
    setFilters(prev => ({ ...prev, search: value }));
  };

  // 处理筛选变化
  const handleFilterChange = (field: string, value: string) => {
    setFilters(prev => ({ ...prev, [field]: value }));
  };

  // 表格列定义 - 明确类型并修复fixed属性
  const columns: ColumnsType<Customer> = [
    {
      title: '',
      key: 'selection',
      render: (_, record: Customer) => (
        <Checkbox value={record.id} />
      ),
      width: 50,
      fixed: 'left' as const,
    },
    {
      title: t('admin.table.name'),
      dataIndex: 'name',
      key: 'name',
      fixed: 'left' as const,
      width: 120,
      sorter: (a: Customer, b: Customer) => a.name.localeCompare(b.name)
    },
    {
      title: t('admin.table.phone'),
      dataIndex: 'phone',
      key: 'phone',
      width: 140
    },
    {
      title: t('admin.table.email'),
      dataIndex: 'email',
      key: 'email',
      width: 200
    },
    {
      title: t('admin.table.idNumber'),
      dataIndex: 'idNumber',
      key: 'idNumber',
      width: 180,
      render: (idNumber: string) => {
        if (!idNumber) return '-';
        return `${idNumber.substr(0, 6)}********${idNumber.substr(-4)}`;
      }
    },
    {
      title: t('admin.table.car'),
      key: 'car',
      render: (_, record: Customer) => `${record.carBrand} ${record.carModel}`,
      width: 200
    },
    {
      title: t('admin.table.carPrice'),
      key: 'carPrice',
      render: (_, record: Customer) => `¥${record.carPrice.toLocaleString()}`,
      width: 120,
      sorter: (a: Customer, b: Customer) => a.carPrice - b.carPrice
    },
    {
      title: t('admin.table.loanAmount'),
      key: 'loanAmount',
      render: (_, record: Customer) => `¥${record.loanAmount.toLocaleString()}`,
      width: 130,
      sorter: (a: Customer, b: Customer) => a.loanAmount - b.loanAmount
    },
    {
      title: t('admin.table.monthlyIncome'),
      key: 'monthlyIncome',
      render: (_, record: Customer) => `¥${record.monthlyIncome.toLocaleString()}`,
      width: 140,
      sorter: (a: Customer, b: Customer) => a.monthlyIncome - b.monthlyIncome
    },
    {
      title: t('admin.table.status'),
      dataIndex: 'applicationStatus',
      key: 'status',
      width: 130,
      filters: [
        { text: t('status.草稿'), value: '草稿' },
        { text: t('status.已提交'), value: '已提交' },
        { text: t('status.审核中'), value: '审核中' },
        { text: t('status.已批准'), value: '已批准' },
        { text: t('status.已拒绝'), value: '已拒绝' }
      ],
      onFilter: (value, record) => record.applicationStatus === value,
      render: (status: string) => {
        let color = '';
        let bgColor = '';
        switch (status) {
          case '草稿':
            color = '#999';
            bgColor = '#9991';
            break;
          case '已提交':
            color = '#f39c12';
            bgColor = '#f39c121';
            break;
          case '审核中':
            color = '#3498db';
            bgColor = '#3498db1';
            break;
          case '已批准':
            color = '#2ecc71';
            bgColor = '#2ecc711';
            break;
          case '已拒绝':
            color = '#e74c3c';
            bgColor = '#e74c3c1';
            break;
          default:
            color = '#999';
            bgColor = '#9991';
        }
        return (
          <span style={{ 
            color, 
            backgroundColor: bgColor,
            padding: '3px 8px',
            borderRadius: '4px',
            fontSize: '12px'
          }}>
            {t(`status.${status}`)}
          </span>
        );
      },
    },
    {
      title: t('admin.table.auditResult'),
      dataIndex: 'auditResult',
      key: 'auditResult',
      width: 130,
      filters: [
        { text: t('audit.Approve'), value: 'Approve' },
        { text: t('audit.Reject'), value: 'Reject' }
      ],
      onFilter: (value, record) => record.auditResult === value,
      render: (result?: string) => {
        if (!result) return '-';
        const color = result === 'Approve' ? '#2ecc71' : '#e74c3c';
        const bgColor = result === 'Approve' ? '#2ecc711' : '#e74c3c1';
        const icon = result === 'Approve' ? 
          <CheckCircleOutlined style={{ color, marginRight: 4 }} /> : 
          <CloseCircleOutlined style={{ color, marginRight: 4 }} />;
        return (
          <span style={{ 
            color, 
            backgroundColor: bgColor,
            padding: '3px 8px',
            borderRadius: '4px',
            fontSize: '12px',
            display: 'inline-flex',
            alignItems: 'center'
          }}>
            {icon}
            {t(`audit.${result}`)}
          </span>
        );
      },
    },
    {
      title: t('admin.table.createdAt'),
      dataIndex: 'createdAt',
      key: 'createdAt',
      width: 180,
      render: (date: string) => new Date(date).toLocaleString(),
      sorter: (a: Customer, b: Customer) => 
        new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()
    },
    {
      title: t('admin.table.action'),
      key: 'action',
      width: 120,
      fixed: 'right' as const,
      render: (_, record: Customer) => (
        <Space size="middle">
          <Tooltip title={t('admin.table.view')}>
            <Button 
              icon={<EyeOutlined />} 
              size="small" 
              onClick={() => handleView(record)}
              className={styles.actionButton}
            />
          </Tooltip>
          <Tooltip title={t('admin.table.edit')}>
            <Button 
              icon={<EditOutlined />} 
              size="small" 
              type="primary"
              onClick={() => handleEdit(record)}
              disabled={record.applicationStatus === '已批准' || record.applicationStatus === '已拒绝'}
              className={styles.actionButton}
            />
          </Tooltip>
        </Space>
      ),
    },
  ];

  return (
    <div className={`${styles.container} ${isZoomed ? styles.zoomed : ''}`}>
      {contextHolder}
      
      <div className={styles.tableHeader}>
        <h2>{t('admin.table.title')}</h2>
        
        <div className={styles.tableControls}>
          <div className={styles.filters}>
            <Search
              placeholder={t('search.placeholder')}
              allowClear
              enterButton={<SearchOutlined />}
              style={{ width: 250 }}
              onSearch={handleSearch}
            />
            
            <Select
              placeholder={t('filter.status')}
              style={{ width: 150, marginLeft: 8 }}
              allowClear
              onChange={(value) => handleFilterChange('status', value)}
            >
              <Option value="草稿">{t('status.草稿')}</Option>
              <Option value="已提交">{t('status.已提交')}</Option>
              <Option value="审核中">{t('status.审核中')}</Option>
              <Option value="已批准">{t('status.已批准')}</Option>
              <Option value="已拒绝">{t('status.已拒绝')}</Option>
            </Select>
            
            <Select
              placeholder={t('filter.auditResult')}
              style={{ width: 150, marginLeft: 8 }}
              allowClear
              onChange={(value) => handleFilterChange('auditResult', value)}
            >
              <Option value="Approve">{t('audit.Approve')}</Option>
              <Option value="Reject">{t('audit.Reject')}</Option>
            </Select>
          </div>
          
          <div className={styles.tableActions}>
            <Button 
              type="primary" 
              icon={<CheckCircleOutlined />}
              onClick={() => handleBatchAudit('Approve')}
              disabled={selectedRows.length === 0}
            >
              {t('admin.actions.approve')}
            </Button>
            <Button 
              danger 
              icon={<CloseCircleOutlined />}
              onClick={() => handleBatchAudit('Reject')}
              disabled={selectedRows.length === 0}
              style={{ marginLeft: 8 }}
            >
              {t('admin.actions.reject')}
            </Button>
            <Button 
              icon={<DownloadOutlined />}
              onClick={handleExport}
              style={{ marginLeft: 8 }}
            >
              {t('admin.actions.export')}
            </Button>
          </div>
        </div>
      </div>

      <div className={styles.tableContainer}>
        <Spin spinning={loading}>
          <Table
            columns={columns}
            dataSource={customers}
            rowKey="id"
            pagination={false}
            rowSelection={{
              type: 'checkbox',
              selectedRowKeys: selectedRows,
              onChange: handleRowSelection,
            }}
            scroll={{ x: 'max-content' }}
            size={isZoomed ? 'middle' : 'small'}
            showSorterTooltip={false}
          />
        </Spin>
      </div>

      <div className={styles.pagination}>
        <Pagination
          current={page}
          pageSize={pageSize}
          total={total}
          onChange={handlePageChange}
          onShowSizeChange={(_, size) => onPageSizeChange(size)}
          showSizeChanger
          showQuickJumper
          showTotal={(total) => `${t('pagination.total')} ${total} ${t('pagination.items')}`}
        />
      </div>

      {/* 客户信息弹窗 */}
      {currentCustomer && (
        <CustomerDialog
          visible={visibleDialog}
          customer={currentCustomer}
          mode={dialogMode}
          onClose={() => setVisibleDialog(false)}
          onAudit={handleAuditResult}
          onSuccess={loadCustomers}
        />
      )}
    </div>
  );
};

export default CustomerTable;