import { useEffect, useState } from 'react';
import {
  Paper, Table, TableBody, TableCell, TableContainer, TableHead,
  TableRow, Button, Checkbox, Box, Typography, IconButton,
  TablePagination, Chip, ButtonGroup
} from '@mui/material';
import { Edit, Visibility } from '@mui/icons-material';
import { useStore } from '../store';
import { getCustomers, batchProcessLoans } from '../services/api';

const CustomerTable = () => {
  const {
    customers,
    setCustomers,
    selectedCustomer,
    setSelectedCustomer,
    setIsDetailDialogOpen,
    selectedCustomerIds,
    toggleCustomerSelection,
    clearCustomerSelections
  } = useStore();
  
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [batchActionLoading, setBatchActionLoading] = useState(false);
  
  // 加载客户列表
  const loadCustomers = async () => {
    setLoading(true);
    try {
      const data = await getCustomers();
      setCustomers(data);
    } catch (error) {
      console.error('Failed to load customers:', error);
    } finally {
      setLoading(false);
    }
  };
  
  // 组件挂载时加载客户
  useEffect(() => {
    loadCustomers();
  }, []);
  
  // 处理编辑按钮点击
  const handleEdit = (customer: any) => {
    setSelectedCustomer(customer);
    setIsDetailDialogOpen(true);
  };
  
  // 处理查看按钮点击
  const handleView = (customer: any) => {
    setSelectedCustomer(customer);
    setIsDetailDialogOpen(true);
  };
  
  // 处理全选
  const handleSelectAllClick = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.checked) {
      const newSelected = customers.map((n) => n.id);
      // 更新状态以选中所有客户
      // 这里需要根据实际状态管理方式实现
      return;
    }
    clearCustomerSelections();
  };
  
  // 处理批量批准
  const handleBatchApprove = async () => {
    if (selectedCustomerIds.length === 0) return;
    
    setBatchActionLoading(true);
    try {
      await batchProcessLoans(selectedCustomerIds, 'approve');
      clearCustomerSelections();
      loadCustomers(); // 重新加载客户列表
    } catch (error) {
      console.error('Failed to batch approve:', error);
    } finally {
      setBatchActionLoading(false);
    }
  };
  
  // 处理批量拒绝
  const handleBatchReject = async () => {
    if (selectedCustomerIds.length === 0) return;
    
    setBatchActionLoading(true);
    try {
      await batchProcessLoans(selectedCustomerIds, 'reject');
      clearCustomerSelections();
      loadCustomers(); // 重新加载客户列表
    } catch (error) {
      console.error('Failed to batch reject:', error);
    } finally {
      setBatchActionLoading(false);
    }
  };
  
  // 处理分页变化
  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };
  
  // 处理每页行数变化
  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };
  
  // 渲染状态标签
  const renderStatusChip = (status: string) => {
    const statusConfig = {
      pending: { color: 'default', label: '待处理' },
      approved: { color: 'success', label: '已批准' },
      rejected: { color: 'error', label: '已拒绝' }
    };
    
    const config = statusConfig[status as keyof typeof statusConfig] || 
                  { color: 'default', label: status };
    
    return (
      <Chip 
        label={config.label} 
        color={config.color as 'default' | 'success' | 'error'} 
        size="small" 
      />
    );
  };
  
  // 计算要显示的客户
  const displayedCustomers = customers
    .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage);
  
  return (
    <Paper sx={{ width: '100%', overflow: 'hidden' }}>
      <Box sx={{ p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h6">客户信贷申请列表</Typography>
        <ButtonGroup disabled={selectedCustomerIds.length === 0 || batchActionLoading}>
          <Button 
            color="primary" 
            variant="contained" 
            size="small"
            onClick={handleBatchApprove}
          >
            批量批准
          </Button>
          <Button 
            color="error" 
            variant="contained" 
            size="small"
            onClick={handleBatchReject}
          >
            批量拒绝
          </Button>
        </ButtonGroup>
      </Box>
      
      <TableContainer>
        <Table stickyHeader>
          <TableHead>
            <TableRow>
              <TableCell padding="checkbox">
                <Checkbox
                  color="primary"
                  indeterminate={selectedCustomerIds.length > 0 && selectedCustomerIds.length < customers.length}
                  checked={customers.length > 0 && selectedCustomerIds.length === customers.length}
                  onChange={handleSelectAllClick}
                />
              </TableCell>
              <TableCell>ID</TableCell>
              <TableCell>姓名</TableCell>
              <TableCell>年龄</TableCell>
              <TableCell>月收入</TableCell>
              <TableCell>贷款金额</TableCell>
              <TableCell>贷款用途</TableCell>
              <TableCell>状态</TableCell>
              <TableCell>操作</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={9} align="center">加载中...</TableCell>
              </TableRow>
            ) : displayedCustomers.length === 0 ? (
              <TableRow>
                <TableCell colSpan={9} align="center">没有客户数据</TableCell>
              </TableRow>
            ) : (
              displayedCustomers.map((customer) => (
                <TableRow key={customer.id}>
                  <TableCell padding="checkbox">
                    <Checkbox
                      color="primary"
                      checked={selectedCustomerIds.includes(customer.id)}
                      onChange={() => toggleCustomerSelection(customer.id)}
                    />
                  </TableCell>
                  <TableCell>{customer.id}</TableCell>
                  <TableCell>{customer.name}</TableCell>
                  <TableCell>{customer.age}</TableCell>
                  <TableCell>¥{customer.monthlyIncome.toLocaleString()}</TableCell>
                  <TableCell>¥{customer.loanAmount.toLocaleString()}</TableCell>
                  <TableCell>{customer.loanPurpose}</TableCell>
                  <TableCell>{renderStatusChip(customer.status)}</TableCell>
                  <TableCell>
                    <IconButton size="small" onClick={() => handleView(customer)}>
                      <Visibility fontSize="small" />
                    </IconButton>
                    <IconButton size="small" onClick={() => handleEdit(customer)}>
                      <Edit fontSize="small" />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
      
      <TablePagination
        rowsPerPageOptions={[5, 10, 25]}
        component="div"
        count={customers.length}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
      />
    </Paper>
  );
};

export default CustomerTable;