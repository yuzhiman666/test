import { Canvas } from '@react-three/fiber';
import { Environment, OrbitControls, PerspectiveCamera } from '@react-three/drei';
import { Suspense } from 'react';

const CarModel = () => {
  return (
    <mesh position={[0, -1, 0]} rotation={[-Math.PI / 2, 0, 0]} scale={0.5}>
      {/* 这里可以替换为宝马汽车模型，这里使用简单几何体代替 */}
      <boxGeometry args={[4, 2, 1.5]} />
      <meshStandardMaterial color="#1E3A8A" transparent opacity={0.1} />
    </mesh>
  );
};

const BackgroundScene = () => {
  return (
    <Canvas 
      style={{ 
        position: 'absolute', 
        top: 0, 
        left: 0, 
        width: '100%', 
        height: '100%',
        zIndex: -1
      }}
    >
      <PerspectiveCamera makeDefault position={[10, 5, 10]} />
      <OrbitControls enableZoom={false} enablePan={false} enableRotate={false} />
      <ambientLight intensity={0.5} />
      <directionalLight position={[10, 10, 5]} intensity={1} />
      <Suspense fallback={null}>
        <CarModel />
        <Environment preset="city" />
      </Suspense>
    </Canvas>
  );
};

export default BackgroundScene;