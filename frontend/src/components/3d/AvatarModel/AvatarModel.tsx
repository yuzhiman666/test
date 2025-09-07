import { useFrame } from '@react-three/fiber';
import { useState, Suspense, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useGLTF, Billboard, Html } from '@react-three/drei';
import { Group } from 'three'; // 用于ref类型定义

const AvatarModel = () => {
  return (
    <Suspense fallback={
      // 加载时显示占位提示（可选）
      <Html position={[3, 0, 0]} transform={true}>
        <div style={{ color: '#666', background: 'rgba(255,255,255,0.8)', padding: '6px 12px', borderRadius: '4px' }}>
          加载数字人中...
        </div>
      </Html>
    }>
      <AvatarModelContent />
    </Suspense>
  );
};

const AvatarModelContent = () => {
  // ❶ 解构出 scene（整个数字人模型场景，包含所有节点层级）
  const { scene, materials } = useGLTF('/models/avatar_model/scene_standwoman.gltf');
  const [isHovered, setIsHovered] = useState(false);
  const [showSpeech, setShowSpeech] = useState(true);
  const navigate = useNavigate();
  const avatarRef = useRef<Group>(null); // 数字人场景引用（控制动画和位置）
  const speechTimerRef = useRef(null); // 用于保存气泡切换定时器

  // ❷ 修正模型位置和缩放（抵消GLTF中的初始偏移，确保在视野内）
  useEffect(() => {
    if (avatarRef.current && scene) {
      // 重置模型位置（覆盖GLTF中的matrix偏移，移到汽车右侧）
      avatarRef.current.position.set(8, -1, 0); 
      // 调整缩放（根据实际模型大小微调，这里0.01是关键！原模型尺寸极大）
      avatarRef.current.scale.set(0.025, 0.025, 0.025);   //数字人尺寸放大（原0.01）
      // 允许后续通过useFrame修改位置/旋转（覆盖GLTF的matrix锁定）
      avatarRef.current.matrixAutoUpdate = true;
    }
  }, [scene]);

  // ❸ 数字人呼吸动画（轻微左右旋转）
  useFrame(() => {
    if (avatarRef.current) {
      avatarRef.current.rotation.y = Math.sin(Date.now() * 0.0005) * 0.1; // 缓慢旋转
    }
  });

  // 对话气泡3秒切换显示/隐藏 - 增加定时器引用保存
  useEffect(() => {
    speechTimerRef.current = setInterval(() => setShowSpeech(prev => !prev), 3000);
    return () => clearInterval(speechTimerRef.current);
  }, []);

  // 点击按钮隐藏气泡并跳转的处理函数
  const handleConsultClick = () => {
    // 隐藏对话气泡
    setIsHovered(false);
    setShowSpeech(false);
    // 清除自动切换定时器，防止气泡再次显示
    clearInterval(speechTimerRef.current);
    // 执行跳转
    // window.location.href = 'http://127.0.0.1:8282/ui';
    window.open('http://127.0.0.1:8282/ui', '_blank');
  };

  return (
    // ❹ 用group包裹整个场景，绑定ref控制位置/动画
    <group 
      ref={avatarRef}
      dispose={null}
      onPointerOver={() => setIsHovered(true)}
      onPointerOut={() => setIsHovered(false)}
      onClick={handleConsultClick} // 数字人整体点击也使用相同的处理函数
      cursor="pointer" // 鼠标悬浮显示手型
    >
      {/* ❺ 渲染整个数字人场景（包含所有节点层级，无需单独找Object_3） */}
      {scene && (
        <primitive 
          object={scene} 
          castShadow // 开启阴影（和汽车模型保持一致）
          receiveShadow 
          material={materials.material_0} // 明确使用模型的材质
        />
      )}

      {/* 对话气泡（位置和数字人匹配） */}
      {(isHovered || showSpeech) && (
        <Billboard 
          position={[3, 150, -50]}  // 上移到头部：y从1.8改为2.5（对应数字人头部位置）
          scale={1.2}   // 整体放大气泡（可选，增强视觉效果）
        >  
          <Html>
            <div style={{ 
              background: 'white', 
              padding: '16px',  // 调整内边距，适应正方形布局
              borderRadius: '18px', 
              boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
              width: 'auto',   // 宽度自动适应内容
              aspectRatio: '1', // 保持正方形比例
              minWidth: '180px', // 最小宽度确保正方形基本形态
              minHeight: '180px', // 最小高度确保正方形基本形态
              fontSize: '15px',   // 文字稍放大
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center'
            }}>
              {/* 气泡文字 */}
              <p style={{ margin: 0, lineHeight: '1.5' }}>
                Hi! I’m Auto Xiao Ai – here to help you pick a car, sort out loans, and get pre-approvals!
              </p>
              {/* 立即咨询按钮 */}
              <button 
                style={{ 
                  marginTop: '8px', 
                  padding: '6px 12px', 
                  background: '#007bff', 
                  color: 'white', 
                  border: 'none', 
                  borderRadius: '16px', 
                  fontSize: '14px', 
                  cursor: 'pointer',
                  transition: 'background 0.2s',
                  alignSelf: 'center'
                }}
                onClick={handleConsultClick} // 使用新的处理函数
              >
                Consult Now
              </button>
            </div>
          </Html>
        </Billboard>
      )}
    </group>
  );
};

// 预加载数字人模型（提升加载速度）
useGLTF.preload('/models/avatar_model/scene_standwoman.gltf');

export default AvatarModel;