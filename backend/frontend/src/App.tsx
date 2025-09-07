import { ThemeProvider, createTheme } from '@mui/material/styles';
import Chatbot from './components/Chatbot';
import CssBaseline from '@mui/material/CssBaseline';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Dashboard from './components/Dashboard';

// 创建React Query客户端
const queryClient = new QueryClient();

// 创建自定义主题
const theme = createTheme({
  palette: {
    primary: {
      main: '#1E3A8A', // 宝马蓝
    },
    secondary: {
      main: '#FFFFFF',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Dashboard />
        <Chatbot />
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;