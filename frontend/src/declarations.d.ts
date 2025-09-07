// src/declarations.d.ts 类型声明文件
import type { JSX } from '@react-three/fiber';

// 扩展 JSX 类型，让 TypeScript 识别 React Three Fiber 的 3D 组件
declare global {
  namespace JSX {
    interface IntrinsicElements extends JSX.IntrinsicElements {}
  }
}