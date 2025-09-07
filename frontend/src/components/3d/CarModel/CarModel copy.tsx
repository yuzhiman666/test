import { useGLTF } from '@react-three/drei';
// import Group from '@react-three/fiber';
// import { Suspense } from 'react';
// CarModel.tsx 正确导入（只导入需要的成员）
import { Group, Suspense } from '@react-three/fiber';

const CarModel = () => {
  return (
    <Suspense fallback={null}>
      <CarModelContent />
    </Suspense>
  );
};

const CarModelContent = () => {
  // 加载 public/models 下的汽车模型
  const { nodes, materials } = useGLTF('/models/car_model/scene_car.gltf');
  
  return (
    <Group dispose={null}>
      {/* 模型节点名可能需要调整：打开模型文件查看实际节点名，常见为 "Car" 或 "Vehicle" */}
      {nodes.Car && (
        <mesh 
          castShadow 
          receiveShadow 
          geometry={nodes.Car.geometry} 
          material={materials.CarMaterial || materials.base}
          position={[0, -1, 0]} // 调整位置（y轴-1：下沉1单位，避免悬空）
          scale={0.8} // 缩放模型大小（根据实际模型调整）
        />
      )}
    </Group>
  );
};

// 预加载模型（提升加载速度）
useGLTF.preload('/models/car_model/scene_car.gltf');

export default CarModel;