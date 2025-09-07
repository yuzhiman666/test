import { Canvas } from '@react-three/fiber';
import { OrbitControls, Environment, PerspectiveCamera } from '@react-three/drei';
import { PlaneGeometry } from 'three';
import CarModel from '../CarModel/CarModel';
import AvatarModel from '../AvatarModel/AvatarModel';
import styled from 'styled-components';

const ModelViewerContainer = styled.div`
  width: 100%;
  height: 80vh;
  position: relative;
  overflow: hidden;
`;

const ModelViewer = () => {
  return (
    <ModelViewerContainer>
      {/* ❶ Canvas内无多余空格，组件用注释分隔 */}
      <Canvas shadows dpr={[1, 2]}>
        {/* 相机 */}
        <PerspectiveCamera makeDefault position={[10, 5, 10]} fov={50} />
        {/* 控制器 */}
        <OrbitControls enableZoom={true} maxPolarAngle={Math.PI / 2} enablePan={false} zoomSpeed={0.5} rotateSpeed={0.5} />
        {/* 3D模型 */}
        <CarModel />
        <AvatarModel />
        {/* 环境与光照 */}
        {/* <Environment preset="city" /> */}
        <Environment files="../../../../public/models/city_model/metro_noord_4k.hdr" />
        <ambientLight intensity={0.6} />
        <directionalLight position={[10, 15, 5]} intensity={1.2} castShadow shadow-mapSize-width={2048} shadow-mapSize-height={2048} />
        {/* 地面 */}
        <mesh receiveShadow position={[0, -1, 0]} rotation={[-Math.PI / 2, 0, 0]}>
          <planeGeometry args={[100, 100]} />
          <meshStandardMaterial color="#f0f0f0" />
        </mesh>
      </Canvas>
    </ModelViewerContainer>
  );
};

export default ModelViewer;