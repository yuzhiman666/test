import { useState, useEffect, useRef, useCallback } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { DataGroup } from '../types/chart';

interface ChartOptions {
  width?: number;
  height?: number;
  backgroundColor?: string;
  cameraPosition?: [number, number, number];
  enableControls?: boolean;
}

interface ChartDataPoint {
  x: number | string;
  y: number | string;
  z: number;
  color?: string;
  label?: string;
}

interface Use3DChartResult {
  canvasRef: React.RefObject<HTMLCanvasElement>;
  isLoading: boolean;
  error: string | null;
  updateData: (data: DataGroup<ChartDataPoint>[]) => void;
  resize: () => void;
  dispose: () => void;
}

/**
 * 3D图表渲染Hook，基于Three.js
 * @param options 图表配置选项
 * @returns 图表相关引用和操作方法
 */
const use3DCharts = ({
  width = 800,
  height = 600,
  backgroundColor = '#f8fafc',
  cameraPosition = [10, 10, 10],
  enableControls = true,
}: ChartOptions = {}): Use3DChartResult => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Three.js核心对象引用
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const controlsRef = useRef<OrbitControls | null>(null);
  const dataObjectsRef = useRef<THREE.Object3D[]>([]);
  const axesRef = useRef<THREE.AxesHelper | null>(null);

  // 初始化3D场景
  const initScene = useCallback(() => {
    try {
      // 清理现有场景
      dispose();

      const canvas = canvasRef.current;
      if (!canvas) {
        throw new Error('Canvas element not found');
      }

      // 创建场景
      const scene = new THREE.Scene();
      scene.background = new THREE.Color(backgroundColor);
      sceneRef.current = scene;

      // 创建相机
      const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
      camera.position.set(...cameraPosition);
      cameraRef.current = camera;

      // 创建渲染器
      const renderer = new THREE.WebGLRenderer({
        canvas,
        antialias: true,
        alpha: true,
      });
      renderer.setSize(width, height);
      renderer.setPixelRatio(window.devicePixelRatio);
      rendererRef.current = renderer;

      // 添加轨道控制器
      if (enableControls) {
        const controls = new OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.1;
        controlsRef.current = controls;
      }

      // 添加坐标轴辅助线
      const axes = new THREE.AxesHelper(10);
      scene.add(axes);
      axesRef.current = axes;

      // 添加光源
      const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
      scene.add(ambientLight);

      const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
      directionalLight.position.set(5, 10, 7.5);
      scene.add(directionalLight);

      // 动画循环
      const animate = () => {
        requestAnimationFrame(animate);
        controlsRef.current?.update();
        rendererRef.current?.render(scene, camera);
      };
      animate();

      setIsLoading(false);
      setError(null);
    } catch (err) {
      console.error('Failed to initialize 3D chart:', err);
      setError(err instanceof Error ? err.message : 'Failed to initialize 3D chart');
      setIsLoading(false);
    }
  }, [width, height, backgroundColor, cameraPosition, enableControls]);

  // 初始化场景
  useEffect(() => {
    initScene();
    
    // 窗口大小变化时重新渲染
    const handleResize = () => {
      resize();
    };
    
    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
      dispose();
    };
  }, [initScene]);

  // 清理场景资源
  const dispose = useCallback(() => {
    // 移除所有数据对象
    dataObjectsRef.current.forEach(obj => {
      if (sceneRef.current?.children.includes(obj)) {
        sceneRef.current.remove(obj);
      }
      // 递归清理几何体和材质
      obj.traverse((child) => {
        if (child instanceof THREE.Mesh) {
          child.geometry.dispose();
          if (Array.isArray(child.material)) {
            child.material.forEach(mat => mat.dispose());
          } else {
            child.material.dispose();
          }
        }
      });
    });
    dataObjectsRef.current = [];

    // 移除坐标轴
    if (axesRef.current && sceneRef.current?.children.includes(axesRef.current)) {
      sceneRef.current.remove(axesRef.current);
      axesRef.current = null;
    }

    // 销毁控制器
    controlsRef.current?.dispose();
    controlsRef.current = null;

    // 销毁渲染器
    rendererRef.current?.dispose();
    rendererRef.current = null;

    sceneRef.current = null;
    cameraRef.current = null;
  }, []);

  // 调整大小
  const resize = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas || !cameraRef.current || !rendererRef.current) return;

    const { clientWidth, clientHeight } = canvas;
    cameraRef.current.aspect = clientWidth / clientHeight;
    cameraRef.current.updateProjectionMatrix();
    rendererRef.current.setSize(clientWidth, clientHeight);
  }, []);

  // 更新图表数据
  const updateData = useCallback((dataGroups: DataGroup<ChartDataPoint>[]) => {
    if (!sceneRef.current || !cameraRef.current) {
      setError('3D scene not initialized');
      return;
    }

    // 清除现有数据对象
    dataObjectsRef.current.forEach(obj => {
      sceneRef.current?.remove(obj);
    });
    dataObjectsRef.current = [];

    try {
      // 找出数据范围用于缩放
      let minX = Infinity, maxX = -Infinity;
      let minY = Infinity, maxY = -Infinity;
      let minZ = Infinity, maxZ = -Infinity;

      // 先收集所有数据点确定范围
      dataGroups.flatMap(group => group.data).forEach(point => {
        const x = Number(point.x);
        const y = Number(point.y);
        const z = point.z;
        
        minX = Math.min(minX, x);
        maxX = Math.max(maxX, x);
        minY = Math.min(minY, y);
        maxY = Math.max(maxY, y);
        minZ = Math.min(minZ, z);
        maxZ = Math.max(maxZ, z);
      });

      // 如果所有值都相同，设置一个默认范围
      const rangeX = maxX === minX ? 1 : maxX - minX;
      const rangeY = maxY === minY ? 1 : maxY - minY;
      const rangeZ = maxZ === minZ ? 1 : maxZ - minZ;

      // 为每个数据组创建对象
      dataGroups.forEach(group => {
        const groupObject = new THREE.Group();
        groupObject.name = group.name;
        
        group.data.forEach(point => {
          const x = Number(point.x);
          const y = Number(point.y);
          const z = point.z;

          // 归一化坐标到合适的范围
          const normalizedX = ((x - minX) / rangeX) * 8 - 4; // 范围: -4 到 4
          const normalizedY = ((y - minY) / rangeY) * 8 - 4;
          const normalizedZ = ((z - minZ) / rangeZ) * 4; // Z轴范围稍小

          // 创建柱状体
          const geometry = new THREE.BoxGeometry(0.3, 0.3, normalizedZ > 0 ? normalizedZ : 0.1);
          const material = new THREE.MeshStandardMaterial({
            color: point.color || group.color || 0x3b82f6,
            transparent: true,
            opacity: 0.8,
          });
          
          const cube = new THREE.Mesh(geometry, material);
          cube.position.set(normalizedX, normalizedY, normalizedZ / 2); // Z轴居中
          cube.userData = { ...point }; // 存储原始数据
          
          groupObject.add(cube);
        });
        
        sceneRef.current?.add(groupObject);
        dataObjectsRef.current.push(groupObject);
      });

      setError(null);
    } catch (err) {
      console.error('Failed to update 3D chart data:', err);
      setError(err instanceof Error ? err.message : 'Failed to update chart data');
    }
  }, []);

  return {
    canvasRef,
    isLoading,
    error,
    updateData,
    resize,
    dispose,
  };
};

export default use3DCharts;