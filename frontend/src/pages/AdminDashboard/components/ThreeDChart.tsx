import React, { useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useFrame, Canvas } from '@react-three/fiber';
import { Text, Billboard } from '@react-three/drei';
import * as THREE from 'three';
import styles from './ThreeDChart.module.css';
import { ChartData } from '../../../types/admin.ts';

interface ThreeDChartProps {
  chart: ChartData;
  isZoomed?: boolean;
}

// 3D饼图切片组件
const PieSlice: React.FC<{
  startAngle: number;
  endAngle: number;
  radius: number;
  height: number;
  color: string;
  name: string;
  value: number;
  total: number;
}> = ({ startAngle, endAngle, radius, height, color, name, value, total }) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const groupRef = useRef<THREE.Group>(null);
  const [hovered, setHovered] = React.useState(false);

  // 创建饼图切片的几何体
  useEffect(() => {
    if (!meshRef.current) return;

    const shape = new THREE.Shape()
      .moveTo(0, 0)
      .arc(0, 0, radius, startAngle, endAngle, false)
      .lineTo(0, 0);

    // 挤压成3D形状
    const extrudeSettings = {
      depth: height,
      bevelEnabled: false
    };

    const extrudedGeometry = new THREE.ExtrudeGeometry(shape, extrudeSettings);
    meshRef.current.geometry.dispose();
    meshRef.current.geometry = extrudedGeometry;

    // 计算切片中心位置用于标签
    const midAngle = (startAngle + endAngle) / 2;
    const labelRadius = radius * 0.7;
    const x = Math.cos(midAngle) * labelRadius;
    const y = Math.sin(midAngle) * labelRadius;
    
    if (groupRef.current?.children[1]) {
      (groupRef.current.children[1] as THREE.Object3D).position.set(x, y, height / 2);
    }
  }, [startAngle, endAngle, radius, height]);

  // 鼠标交互效果
  useFrame(() => {
    if (meshRef.current) {
      const material = meshRef.current.material as THREE.MeshStandardMaterial;
      material.color.set(hovered ? 
        new THREE.Color(color).convertSRGBToLinear().multiplyScalar(1.2) : 
        new THREE.Color(color).convertSRGBToLinear()
      );
      meshRef.current.position.z = hovered ? height * 0.2 : 0;
    }
  });

  // 计算百分比
  const percentage = Math.round((value / total) * 100);

  return (
    <group ref={groupRef} rotation-x={-Math.PI / 2}>
      <mesh
        ref={meshRef}
        material={new THREE.MeshStandardMaterial({ 
          color,
          metalness: 0.1,
          roughness: 0.7
        })}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
        castShadow
        receiveShadow
      />
      <Billboard position={[0, 0, height / 2]}>
        <Text 
          fontSize={0.5} 
          color="#fff"
          anchorX="center"
          anchorY="middle"
        >
          {`${name} ${percentage}%`}
        </Text>
      </Billboard>
    </group>
  );
};

// 3D柱状图柱子组件
const Bar: React.FC<{
  x: number;
  z: number;
  width: number;
  depth: number;
  height: number;
  color: string;
  name: string;
}> = ({ x, z, width, depth, height, color, name }) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = React.useState(false);

  // 鼠标交互效果
  useFrame(() => {
    if (meshRef.current) {
      (meshRef.current.material as THREE.MeshStandardMaterial).color.set(hovered ? 
        new THREE.Color(color).convertSRGBToLinear().multiplyScalar(1.2) : 
        new THREE.Color(color).convertSRGBToLinear()
      );
      meshRef.current.position.y = hovered ? height * 0.1 : 0;
    }
  });

  return (
    <group>
      <mesh
        ref={meshRef}
        position={[x, height / 2, z]}
        material={new THREE.MeshStandardMaterial({ 
          color,
          metalness: 0.1,
          roughness: 0.7
        })}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
        castShadow
        receiveShadow
      >
        <boxGeometry args={[width, height, depth]} />
      </mesh>
      <Billboard position={[x, 0, z - depth/2 - 0.3]}>
        <Text 
          fontSize={0.4} 
          color="#333"
          anchorX="center"
          anchorY="middle"
        >
          {name}
        </Text>
      </Billboard>
      <Billboard position={[x, height + 0.5, z]}>
        <Text 
          fontSize={0.35} 
          color="#333"
          anchorX="center"
          anchorY="middle"
        >
          {height.toLocaleString()}
        </Text>
      </Billboard>
    </group>
  );
};

// 3D折线图组件
const LineChart: React.FC<{
  data: { name: string; value: number; color: string }[];
  width: number;
  height: number;
}> = ({ data, width, height }) => {
  const lineRef = useRef<THREE.Line>(null);
  const maxValue = Math.max(...data.map(item => item.value));
  const stepX = width / (data.length - 1);
  const yScale = height / maxValue;

  // 创建折线
  useEffect(() => {
    if (!lineRef.current) return;

    const points = data.map((item, index) => 
      new THREE.Vector3(
        index * stepX - width / 2, 
        item.value * yScale, 
        0
      )
    );

    const geometry = new THREE.BufferGeometry().setFromPoints(points);
    lineRef.current.geometry.dispose();
    lineRef.current.geometry = geometry;
  }, [data, width, height, stepX, yScale]);

  return (
    <group>
      {/* 折线 */}
      <line>
        <bufferGeometry attach="geometry" />
        <lineBasicMaterial color="#333" linewidth={3} />
      </line>
      
      {/* 数据点 */}
      {data.map((item, index) => (
        <group key={index}>
          <mesh
            position={[
              index * stepX - width / 2, 
              item.value * yScale, 
              0
            ]}
            onPointerOver={(e) => e.stopPropagation()}
            onPointerOut={(e) => e.stopPropagation()}
          >
            <sphereGeometry args={[0.2, 16, 16]} />
            <meshStandardMaterial color={item.color} />
          </mesh>
          
          {/* 数据标签 */}
          <Billboard position={[
            index * stepX - width / 2, 
            item.value * yScale + 0.5, 
            0
          ]}>
            <Text 
              fontSize={0.35} 
              color="#333"
              anchorX="center"
              anchorY="middle"
            >
              {item.value.toLocaleString()}
            </Text>
          </Billboard>
          
          {/* X轴标签 */}
          <Billboard position={[
            index * stepX - width / 2, 
            -0.5, 
            0
          ]}>
            <Text 
              fontSize={0.4} 
              color="#333"
              anchorX="center"
              anchorY="middle"
            >
              {item.name}
            </Text>
          </Billboard>
        </group>
      ))}
      
      {/* X轴 */}
      <line>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes.position"
            array={new Float32Array([-width/2, 0, 0, width/2, 0, 0])}
            itemSize={3}
          />
        </bufferGeometry>
        <lineBasicMaterial color="#999" />
      </line>
      
      {/* Y轴 */}
      <line>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes.position"
            array={new Float32Array([-width/2, 0, 0, -width/2, height, 0])}
            itemSize={3}
          />
        </bufferGeometry>
        <lineBasicMaterial color="#999" />
      </line>
    </group>
  );
};

// 主图表组件
const ThreeDChart: React.FC<ThreeDChartProps> = ({ chart, isZoomed = false }) => {
  const { t, i18n } = useTranslation();
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = React.useState({ width: 0, height: 0 });
  
  // 响应式尺寸
  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        const { width, height } = containerRef.current.getBoundingClientRect();
        setDimensions({ width, height });
      }
    };
    
    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  // 根据图表类型渲染不同的图表
  const renderChartContent = () => {
    const { type, data, dimensions: chartDims } = chart;
    const baseSize = isZoomed ? 1.5 : 1;
    const width = (chartDims?.x || 10) * baseSize;
    const height = (chartDims?.y || 8) * baseSize;

    switch (type) {
      case 'pie':
        const total = data.reduce((sum, item) => sum + item.value, 0);
        const radius = Math.min(width, height) / 3;
        const sliceHeight = (chartDims?.z || 3) * baseSize;
        
        let startAngle = 0;
        return data.map((item, index) => {
          const percentage = item.value / total;
          const endAngle = startAngle + percentage * Math.PI * 2;
          
          const slice = (
            <PieSlice
              key={index}
              startAngle={startAngle}
              endAngle={endAngle}
              radius={radius}
              height={sliceHeight}
              color={item.color}
              name={item.name}
              value={item.value}
              total={total}
            />
          );
          
          startAngle = endAngle;
          return slice;
        });
        
      case 'bar':
        const barWidth = width / data.length * 0.6;
        const barDepth = barWidth * 0.8;
        const maxValue = Math.max(...data.map(item => item.value));
        const barHeightScale = height / maxValue * 0.8;
        
        return data.map((item, index) => (
          <Bar
            key={index}
            x={index * (width / (data.length - 1)) - width / 2}
            z={0}
            width={barWidth}
            depth={barDepth}
            height={item.value * barHeightScale}
            color={item.color}
            name={item.name}
          />
        ));
        
      case 'line':
        return (
          <LineChart
            data={data}
            width={width}
            height={height}
          />
        );
        
      default:
        return null;
    }
  };

  return (
    <div 
      ref={containerRef}
      className={`${styles.container} ${isZoomed ? styles.zoomed : ''}`}
      style={{ 
        width: isZoomed ? '100%' : 'auto',
        height: isZoomed ? '80vh' : '400px'
      }}
    >
      {!isZoomed && (
        <h3 className={styles.title}>{chart.title[i18n.language]}</h3>
      )}
      <div className={styles.canvasContainer}>
        <Canvas 
          camera={{ position: [0, 15, 20], fov: 45 }}
          style={{ width: '100%', height: '100%' }}
        >
          <ambientLight intensity={0.5} />
          <directionalLight 
            position={[10, 20, 15]} 
            intensity={1} 
            castShadow
            shadow-mapSize-width={1024}
            shadow-mapSize-height={1024}
          />
          <directionalLight 
            position={[-10, 10, -5]} 
            intensity={0.3} 
          />
          
          {/* 图表内容 */}
          <group position={[0, 0, 0]}>
            {renderChartContent()}
          </group>
          
          {/* 图表底座 */}
          <mesh 
            position={[0, -0.1, 0]}
            rotation-x={-Math.PI / 2}
            receiveShadow
          >
            <planeGeometry 
              args={[
                (chart.dimensions?.x || 15) * (isZoomed ? 1.8 : 1.2), 
                (chart.dimensions?.y || 10) * (isZoomed ? 1.8 : 1.2)
              ]} 
            />
            <meshStandardMaterial color="#f5f5f5" />
          </mesh>
        </Canvas>
      </div>
    </div>
  );
};

export default ThreeDChart;