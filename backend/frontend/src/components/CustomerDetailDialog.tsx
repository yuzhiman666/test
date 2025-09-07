import { useState, useEffect } from 'react';  // 确保包含 useEffect
import { 
  Dialog, DialogTitle, DialogContent, DialogContentText, 
  DialogActions, Button, TextField, Grid, Paper, Typography 
} from '@mui/material';
import { useStore } from '../store';
import { approveLoan, rejectLoan, getCustomerCreditDetail } from '../services/api';
import type { CreditReviewDetail } from '../types';

const CustomerDetailDialog = () => {
  const { 
    isDetailDialogOpen, 
    setIsDetailDialogOpen, 
    selectedCustomer 
  } = useStore();
  
  const [feedback, setFeedback] = useState('');
  const [creditDetail, setCreditDetail] = useState<CreditReviewDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [human_reult,setHumanResult] = useState('')
  const [thread_id,setThreadId] = useState('')
  
  // 当选中客户变化时加载信贷详情
  const loadCreditDetail = async () => {
    if (!selectedCustomer) return;
    
    setLoading(true);
    try {
      const detail = await getCustomerCreditDetail(selectedCustomer.id);
      setCreditDetail(detail);
    } catch (error) {
      console.error('Failed to load credit detail:', error);
    } finally {
      setLoading(false);
    }
  };
  
  // 组件挂载或选中客户变化时加载详情
  useEffect(() => {
    if (isDetailDialogOpen && selectedCustomer) {
      loadCreditDetail();
    }
  }, [isDetailDialogOpen, selectedCustomer]);
  
  const handleApprove = async () => {
    if (!selectedCustomer) return;
    
    setLoading(true);
    setHumanResult('approve')
    setThreadId('a3051992-88ee-4949-ac7c-4795e2f4bf59')
    try {
      await approveLoan(selectedCustomer.id, human_reult, thread_id, feedback);
      setIsDetailDialogOpen(false);
      // 可以在这里刷新客户列表
    } catch (error) {
      console.error('Failed to approve loan:', error);
    } finally {
      setLoading(false);
      setFeedback('');
    }
  };
  
  const handleReject = async () => {
    if (!selectedCustomer) return;
    
    setLoading(true);
    setHumanResult('reject')
    setThreadId('a3051992-88ee-4949-ac7c-4795e2f4bf59')
    try {
      await rejectLoan(selectedCustomer.id, human_reult, feedback);
      setIsDetailDialogOpen(false);
      // 可以在这里刷新客户列表
    } catch (error) {
      console.error('Failed to reject loan:', error);
    } finally {
      setLoading(false);
      setFeedback('');
    }
  };
  
  if (!selectedCustomer) return null;
  
  return (
    <Dialog 
      open={isDetailDialogOpen} 
      onClose={() => setIsDetailDialogOpen(false)}
      maxWidth="md"
      fullWidth
    >
      <DialogTitle>客户信贷审查详情</DialogTitle>
      <DialogContent dividers>
        <Grid container spacing={2}>
          {/* 客户基本信息 */}
          <Grid size={{ md: 6 }} sx={{ width: '100%' }}>  {/* 修正 md 属性为 size */}
            <Paper elevation={1} sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>客户基本信息</Typography>
              <DialogContentText>
                <strong>姓名:</strong> {selectedCustomer.name}<br />
                <strong>年龄:</strong> {selectedCustomer.age}<br />
                <strong>身份证号:</strong> {selectedCustomer.idNumber}<br />
                <strong>职位:</strong> {selectedCustomer.employmentPosition}<br />
                <strong>工作年限:</strong> {selectedCustomer.employmentTenure}年<br />
              </DialogContentText>
            </Paper>
          </Grid>
          
          {/* 财务信息 */}
          <Grid size={{ md: 6 }} sx={{ width: '100%' }}>  {/* 修正此处 */}
            <Paper elevation={1} sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>财务信息</Typography>
              <DialogContentText>
                <strong>月收入:</strong> ¥{selectedCustomer.monthlyIncome.toLocaleString()}<br />
                <strong>年收入:</strong> ¥{selectedCustomer.annualIncome.toLocaleString()}<br />
                <strong>贷款金额:</strong> ¥{selectedCustomer.loanAmount.toLocaleString()}<br />
                <strong>贷款用途:</strong> {selectedCustomer.loanPurpose}<br />
                <strong>验证状态:</strong> {selectedCustomer.verificationStatus}<br />
              </DialogContentText>
            </Paper>
          </Grid>
          
          {/* 信用信息 */}
          <Grid size={{ md: 12 }} sx={{ width: '100%' }}>  {/* 修正此处 */}
            <Paper elevation={1} sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>信用审查结果</Typography>
              {loading ? (
                <Typography>加载中...</Typography>
              ) : creditDetail ? (
                <DialogContentText>
                  <strong>信用评级:</strong> {creditDetail.creditRating}<br />
                  <strong>反欺诈结果:</strong> {creditDetail.fraudDetection}<br />
                  <strong>合规检查:</strong> {creditDetail.compliance}<br />
                </DialogContentText>
              ) : (
                <Typography>无法加载信用审查信息</Typography>
              )}
            </Paper>
          </Grid>
          
          {/* 审核意见 */}
          <Grid size={{ md: 12 }} sx={{ width: '100%' }}>  {/* 修正此处 */}
            <TextField
              autoFocus
              margin="dense"
              label="审核意见（可选）"
              type="text"
              fullWidth
              multiline
              rows={3}
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
            />
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button 
          onClick={() => setIsDetailDialogOpen(false)}
          disabled={loading}
        >
          取消
        </Button>
        <Button 
          onClick={handleReject} 
          color="error"
          disabled={loading}
        >
          拒绝
        </Button>
        <Button 
          onClick={handleApprove} 
          color="primary"
          disabled={loading}
        >
          批准
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default CustomerDetailDialog;