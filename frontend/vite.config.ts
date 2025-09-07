// import { defineConfig } from 'vite';
// import react from '@vitejs/plugin-react';
// import path from 'path';

// export default defineConfig({
//   plugins: [react()],  // 确保 React 插件正确加载
//   resolve: {
//     alias: {
//       '@': path.resolve(__dirname, './src'), // 别名：@ 指向 src 目录
//     },
//   },
//   server: {
//     port: 3000, // 前端运行端口（固定3000，方便和后端对接）
//     proxy: {
//       // 后端 FastAPI 接口代理（后端需运行在 8000 端口）
//       '/api': {
//         target: 'http://localhost:8000',
//         changeOrigin: true,
//         rewrite: (path) => path.replace(/^\/api/, ''),
//       },
//       // OpenAvatarChat 服务代理（运行在 8001 端口）
//       '/open-avatar': {
//         target: 'http://localhost:8001',
//         changeOrigin: true,
//         rewrite: (path) => path.replace(/^\/open-avatar/, ''),
//       }
//     }
//   }
// });

import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path'

export default defineConfig({
  build: {
    //sourcemap: process.env.NODE_ENV !== 'production',  // 生产环境不生成sourcemap
    // 或者完全禁用sourcemap
    sourcemap: false,  // 完全禁用 sourcemap
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src') // 关键配置：@ 映射到 src 目录
    }
  },
  plugins: [react()],
  server: {
    port: 3000, // 前端运行端口（固定3000，方便和后端对接）
    proxy: {
      // API请求代理
      '/api': {
        target: 'http://localhost:8000', // FastAPI后端地址
        changeOrigin: true,
        //rewrite: (path) => path.replace(/^\/api/, ''), // 错误：将 '/api/car-brands' 重写为 '/car-brands'
        // 移除rewrite或修改为不删除/api前缀（两种方式二选一）
        // 方式1：删除rewrite配置（推荐）
        // 方式2：修改rewrite为不替换/api
        rewrite: (path) => path // 保持原路径，即 '/api/car-brands' 代理后仍为 '/api/car-brands'
      },
      // OpenAvatarChat代理
      '/open-avatar': {
        target: 'http://127.0.0.1:8282', // OpenAvatarChat服务地址
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/open-avatar/, ''),
      },
    },
  },
});