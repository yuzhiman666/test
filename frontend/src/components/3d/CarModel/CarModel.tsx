import { Suspense, useState, useRef, useEffect } from 'react';
import { useGLTF, Html } from '@react-three/drei'; // 移除drei中的useFrame导入
import { useFrame } from '@react-three/fiber'; // 正确从fiber导入useFrame
import { Group, Object3D } from 'three';

const CarModel = () => {
  return (
    <Suspense fallback={
      <Html position={[0, 0, 0]} transform={true}>
        <div style={{
          color: '#666',
          fontSize: '16px',
          padding: '8px 16px',
          background: 'rgba(255,255,255,0.8)',
          borderRadius: '4px'
        }}>
          加载汽车模型中...
        </div>
      </Html>
    }>
      <CarModelContent />
    </Suspense>
  );
};

const CarModelContent = () => {
  const { nodes, materials, scene } = useGLTF('/models/car_model/scene_car.gltf');
  const carRef = useRef<Group>(null);

  // 汽车自转动画（useFrame来自正确的导入）
  useFrame(() => {
    if (carRef.current) {
      carRef.current.rotation.y += 0.005;
    }
  });

  // 自动检测汽车模型节点
  const getCarNode = () => {
    const possibleNames = ['Car', 'Vehicle', 'car', 'vehicle', 'Scene'];
    if (scene) return scene;
    for (const name of possibleNames) {
      if (nodes[name]) return nodes[name];
    }
    return Object.values(nodes)[0] || null;
  };
  const carNode = getCarNode();

  return (
    <group ref={carRef} dispose={null}>
      {carNode ? (
        carNode.isMesh ? (
          <mesh
            castShadow
            receiveShadow
            geometry={carNode.geometry}
            material={materials[Object.keys(materials)[0]]}
            position={[0, -1, 0]}
            scale={2.5}
          />
        ) : (
          <primitive
            object={carNode}
            castShadow
            receiveShadow
            position={[0, -1, 0]}
            scale={2.5}
          />
        )
      ) : (
        <mesh position={[0, -1, 0]}>
          <boxGeometry args={[3, 1, 1.5]} />
          <meshBasicMaterial color="#ccc" transparent opacity={0.6} />
        </mesh>
      )}
    </group>
  );
};

// 预加载模型
useGLTF.preload('/models/car_model/scene_car.gltf');

export default CarModel;