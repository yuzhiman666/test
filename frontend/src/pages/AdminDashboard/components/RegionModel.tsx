import React, { useRef, useState, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import { Text, Billboard, Html } from '@react-three/drei';
import * as THREE from 'three';
import styles from './RegionModel.module.css';
import { RegionData } from '../../../types/admin.ts';
import { useTranslation } from 'react-i18next';

interface RegionModelProps {
  regions: RegionData[];
  selectedRegion: string | null;
  onSelectRegion: (regionId: string) => void;
}

// 区域几何体组件
const RegionGeometry: React.FC<{
  coordinates: number[][];
  height: number;
  color: string;
  selected: boolean;
  onClick: () => void;
  name: string;
  sales: number;
}> = ({
  coordinates,
  height,
  color,
  selected,
  onClick,
  name,
  sales
}) => {
  // 明确指定为MeshStandardMaterial材质的网格引用
  const meshRef = useRef<THREE.Mesh<THREE.ExtrudeGeometry, THREE.MeshStandardMaterial>>(null);
  const [hovered, setHovered] = useState(false);
  const { i18n } = useTranslation();

  // 创建区域几何体
  useEffect(() => {
    if (!meshRef.current) return;

    // 创建形状
    const shape = new THREE.Shape();
    
    // 假设坐标是二维数组 [x, z]
    if (coordinates.length > 0) {
      shape.moveTo(coordinates[0][0], coordinates[0][1]);
      
      for (let i = 1; i < coordinates.length; i++) {
        shape.lineTo(coordinates[i][0], coordinates[i][1]);
      }
      
      shape.closePath();
    }

    // 挤压成3D形状
    const extrudeSettings = {
      depth: height,
      bevelEnabled: false
    };

    const geometry = new THREE.ExtrudeGeometry(shape, extrudeSettings);
    meshRef.current.geometry.dispose();
    meshRef.current.geometry = geometry;
  }, [coordinates, height]);

  // 区域交互动画 - 修复材质访问
  useFrame((state, delta) => {
    if (meshRef.current) {
      // 类型断言：明确材质是单个MeshStandardMaterial而非数组
      const material = meshRef.current.material as THREE.MeshStandardMaterial;
      
      // 颜色变化
      const baseColor = new THREE.Color(color);
      const targetColor = selected 
        ? baseColor.multiplyScalar(1.3)
        : hovered 
          ? baseColor.multiplyScalar(1.1)
          : baseColor;
      
      material.color.lerp(targetColor, delta * 10);
      
      // 高度变化
      const targetHeight = selected ? height * 1.3 : hovered ? height * 1.1 : height;
      const currentScale = meshRef.current.scale.y;
      meshRef.current.scale.y = THREE.MathUtils.lerp(currentScale, targetHeight / height, delta * 10);
    }
  });

  return (
    <group onClick={onClick}>
      <mesh
        ref={meshRef}
        material={new THREE.MeshStandardMaterial({ 
          color,
          metalness: 0.1,
          roughness: 0.7,
          transparent: true,
          opacity: 0.8
        })}
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
        castShadow
        receiveShadow
      />
      
      {/* 区域名称标签 */}
      <Billboard position={[0, height + 0.5, 0]}>
        <Text 
          fontSize={0.6} 
          color="#333"
          anchorX="center"
          anchorY="middle"
        >
          {name}
        </Text>
      </Billboard>
      
      {/* 悬停时显示销售额 */}
      {hovered && (
        <Html position={[0, height + 1.5, 0]} transform>
          <div className={styles.tooltip}>
            <div className={styles.tooltipTitle}>{name}</div>
            <div className={styles.tooltipValue}>
              ¥{sales.toLocaleString()}
            </div>
          </div>
        </Html>
      )}
    </group>
  );
};

// 主区域模型组件
const RegionModel: React.FC<RegionModelProps> = ({
  regions,
  selectedRegion,
  onSelectRegion
}) => {
  const { i18n } = useTranslation();
  const [regionColors, setRegionColors] = useState<Record<string, string>>({});
  
  // 为每个区域生成唯一颜色
  useEffect(() => {
    const colors: Record<string, string> = {};
    regions.forEach((region, index) => {
      // 使用HSL颜色空间生成均匀分布的颜色
      const hue = (index * 360) / regions.length;
      colors[region.id] = `hsl(${hue}, 70%, 60%)`;
    });
    setRegionColors(colors);
  }, [regions]);

  // 计算最大销售额用于高度缩放
  const maxSales = Math.max(
    ...regions.map(region => region.salesData.totalSales), 
    1 // 避免除以零
  );

  return (
    <group>
      {/* 区域网格 */}
      {regions.map(region => (
        <RegionGeometry
          key={region.id}
          coordinates={region.coordinates}
          height={(region.salesData.totalSales / maxSales) * 3 + 0.5} // 高度基于销售额，最低0.5
          color={regionColors[region.id] || '#888888'}
          selected={selectedRegion === region.id}
          onClick={() => onSelectRegion(region.id)}
          name={region.name[i18n.language]}
          sales={region.salesData.totalSales}
        />
      ))}
      
      {/* 基础平面 */}
      <mesh position={[0, -0.1, 0]} rotation-x={-Math.PI / 2} receiveShadow>
        <planeGeometry args={[50, 50]} />
        <meshStandardMaterial color="#e8e8e8" />
      </mesh>
      
      {/* 区域选择提示 */}
      <Billboard position={[0, 5, -15]}>
        <Text 
          fontSize={0.8} 
          color="#666"
          anchorX="center"
          anchorY="middle"
        >
          {selectedRegion 
            ? regions.find(r => r.id === selectedRegion)?.name[i18n.language]
            : '点击区域查看详情'
          }
        </Text>
      </Billboard>
    </group>
  );
};

export default RegionModel;