import React, { useRef, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import styles from './ThreeDIcon.module.css';

interface ThreeDIconProps {
  name: string;
  icon: string; // 图标类型标识（如"car"、"users"等）
  color: string;
  onClick: () => void;
  size?: number;
}

const ThreeDIcon: React.FC<ThreeDIconProps> = ({
  name,
  icon,
  color,
  onClick,
  size = 1
}) => {
  const groupRef = useRef<THREE.Group>(null);
  const [hovered, setHovered] = useState(false);
  const [clicked, setClicked] = useState(false);

  // 根据图标类型返回基础几何体（完全替代SVG解析方案）
  const createIconGeometry = () => {
    switch (icon) {
      case 'hand-paper-o': // 催收
        return new THREE.TorusKnotGeometry(0.8, 0.3, 50, 16); //  torus knot 形状
      case 'car': // 选车
        return new THREE.BoxGeometry(1.5, 0.8, 0.5); // 长方体（模拟汽车）
      case 'users': // CRM
        return new THREE.SphereGeometry(0.7, 32, 32); // 球体（模拟用户）
      case 'shield': // 防欺诈
        return new THREE.ConeGeometry(0.8, 1.5, 32); // 圆锥体（模拟盾牌）
      case 'line-chart': // 数据分析
        return new THREE.CylinderGeometry(0.5, 0.5, 1.2, 32); // 圆柱体（模拟图表）
      case 'cog': // 设置
        return new THREE.TorusGeometry(0.7, 0.2, 16, 100); // 圆环（模拟齿轮）
      default:
        return new THREE.IcosahedronGeometry(0.8, 1); // 默认二十面体
    }
  };

  // 3D交互动画
  useFrame((state, delta) => {
    if (groupRef.current) {
      // 基础旋转动画
      if (!hovered && !clicked) {
        groupRef.current.rotation.y += delta * 0.5;
      }
      
      // 悬停上浮效果
      const targetY = hovered ? 0.5 : 0;
      groupRef.current.position.y = THREE.MathUtils.lerp(
        groupRef.current.position.y, 
        targetY, 
        delta * 10
      );
      
      // 点击缩放反馈
      if (clicked) {
        groupRef.current.scale.x = THREE.MathUtils.lerp(groupRef.current.scale.x, 0.9, delta * 20);
        groupRef.current.scale.y = THREE.MathUtils.lerp(groupRef.current.scale.y, 0.9, delta * 20);
        groupRef.current.scale.z = THREE.MathUtils.lerp(groupRef.current.scale.z, 0.9, delta * 20);
        
        // 恢复正常状态
        setTimeout(() => setClicked(false), 200);
      } else {
        groupRef.current.scale.x = THREE.MathUtils.lerp(groupRef.current.scale.x, 1, delta * 10);
        groupRef.current.scale.y = THREE.MathUtils.lerp(groupRef.current.scale.y, 1, delta * 10);
        groupRef.current.scale.z = THREE.MathUtils.lerp(groupRef.current.scale.z, 1, delta * 10);
      }
    }
  });

  // 点击事件处理
  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    setClicked(true);
    setTimeout(() => onClick(), 200); // 延迟触发，配合动画效果
  };

  return (
    <div className={styles.container} onClick={handleClick}>
      <div className={styles.iconContainer}>
        {/* 3D渲染区域 */}
        <canvas
          className={styles.iconCanvas}
          width={isNaN(size) ? 120 : size * 120}
          height={isNaN(size) ? 150 : size * 150}
        >
          {/* 3D场景内容 */}
          <group ref={groupRef} scale={[size, size, size]}>
            {/* 图标主体 */}
            <mesh
              onPointerOver={() => setHovered(true)}
              onPointerOut={() => setHovered(false)}
              castShadow
            >
              <primitive object={createIconGeometry()} />
              <meshStandardMaterial 
                color={color}
                metalness={0.3}
                roughness={0.5}
              />
            </mesh>
            
            {/* 底部底座（增强立体感） */}
            <mesh position={[0, -0.3, 0]} rotation-x={-Math.PI / 2}>
              <circleGeometry args={[1.5, 32]} />
              <meshStandardMaterial color="#f0f0f0" />
            </mesh>
          </group>
          
          {/* 光源（提升3D质感） */}
          <ambientLight intensity={0.6} />
          <directionalLight position={[5, 10, 7]} intensity={1} />
        </canvas>
      </div>
      
      {/* 图标名称 */}
      <div className={styles.iconName}>{name}</div>
    </div>
  );
};

export default ThreeDIcon;