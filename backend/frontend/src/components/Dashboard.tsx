import { AppBar, Toolbar, Typography, Box, Container, Grid, Paper } from '@mui/material';
import { CarRental } from '@mui/icons-material';
import CustomerTable from './CustomerTable';
import CustomerDetailDialog from './CustomerDetailDialog';
import Chatbot from './Chatbot';
import BackgroundScene from './BackgroundScene';

const Dashboard = () => {
  return (
    <Box sx={{ flexGrow: 1, minHeight: '100vh', position: 'relative' }}>
      {/* 3D背景 */}
      <BackgroundScene />
      
      {/* 顶部导航栏 */}
      <AppBar position="static">
        <Toolbar>
          <CarRental sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            宝马汽车金融信贷AI平台
          </Typography>
          <Typography variant="body1">
            管理员控制台
          </Typography>
        </Toolbar>
      </AppBar>
      
      {/* 主内容区域 */}
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Grid container spacing={3}>
          {/* 客户表格卡片 */}
          <Grid sx={{ width: '100%' }}>
            <CustomerTable />
          </Grid>
        </Grid>
      </Container>
      
      {/* 客户详情弹窗 */}
      <CustomerDetailDialog />
      
      {/* 右下角聊天机器人 */}
      <Chatbot />
    </Box>
  );
};

export default Dashboard;