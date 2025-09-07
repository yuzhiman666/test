// import { Canvas } from '@react-three/fiber';
// import { OrbitControls, Environment, PerspectiveCamera } from '@react-three/drei';
// import { PlaneGeometry } from 'three'; // 从Three.js导入平面几何体
// import CarModel from '../CarModel/CarModel.tsx';
// import AvatarModel from '../AvatarModel/AvatarModel.tsx';
// import styled from 'styled-components';

// // 3D场景容器样式（占满屏幕高度的80%）
// const ModelViewerContainer = styled.div`
//   width: 100%;
//   height: 80vh;
//   position: relative;
//   overflow: hidden;
// `;

// const ModelViewer = () => {
//   return (
//     <ModelViewerContainer>
//       <Canvas shadows dpr={[1, 2]}>
//         {/* 相机设置（位置：[10,5,10]，视角：50度） */}
//         <PerspectiveCamera makeDefault position={[10, 5, 10]} fov={50} />
        
//         {/* 轨道控制器（支持鼠标旋转/缩放模型） */}
//         <OrbitControls 
//           enableZoom={true} 
//           maxPolarAngle={Math.PI / 2} // 禁止俯视到地面以下
//           enablePan={false} // 禁止平移（避免模型偏移）
//           zoomSpeed={0.5}
//           rotateSpeed={0.5}
//         />
        
//         {/* 加载3D模型 */}
//         <CarModel />
//         <AvatarModel />
        
//         {/* 环境和光照（预设城市环境，提升模型质感） */}
//         <Environment preset="city" />
//         <ambientLight intensity={0.6} /> {/* 环境光 */}
//         <directionalLight 
//           position={[10, 15, 5]} 
//           intensity={1.2} 
//           castShadow 
//           shadow-mapSize-width={2048} 
//           shadow-mapSize-height={2048}
//         />
        
//         {/* 地面（使用Three.js原生组件替代Ground，避免导入错误） */}
//         <mesh 
//           receiveShadow 
//           position={[0, -1, 0]} 
//           rotation={[-Math.PI / 2, 0, 0]} // 旋转90度使其水平
//         >
//           {/* 平面几何体（100x100大小，替代Ground的scale={100}） */}
//           <planeGeometry args={[100, 100]} />
//           <meshStandardMaterial color="#f0f0f0" />
//         </mesh>
//       </Canvas>
//     </ModelViewerContainer>
//   );
// };

// export default ModelViewer;

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
      {/* ❶ 清理 Canvas 内部的多余空格/换行，用注释分隔组件 */}
      <Canvas shadows dpr={[1, 2]}>
        {/* 相机 */}
        <PerspectiveCamera makeDefault position={[10, 5, 10]} fov={50} />
        {/* 控制器 */}
        <OrbitControls 
          enableZoom={true} 
          maxPolarAngle={Math.PI / 2} 
          enablePan={false} 
          zoomSpeed={0.5}
          rotateSpeed={0.5}
        />
        {/* 3D模型 */}
        <CarModel />
        <AvatarModel />
        {/* 环境和光照 */}
        <Environment preset="city" />
        <ambientLight intensity={0.6} />
        <directionalLight 
          position={[10, 15, 5]} 
          intensity={1.2} 
          castShadow 
          shadow-mapSize-width={2048} 
          shadow-mapSize-height={2048}
        />
        {/* 地面 */}
        <mesh 
          receiveShadow 
          position={[0, -1, 0]} 
          rotation={[-Math.PI / 2, 0, 0]}
        >
          <planeGeometry args={[100, 100]} />
          <meshStandardMaterial color="#f0f0f0" />
        </mesh>
      </Canvas>
    </ModelViewerContainer>
  );
};

export default ModelViewer;