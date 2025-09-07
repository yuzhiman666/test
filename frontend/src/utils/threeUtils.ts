import * as THREE from 'three';
import { Font } from 'three/addons/loaders/FontLoader.js';
import { TextGeometry } from 'three/addons/geometries/TextGeometry.js';

/**
 * 创建基础材质
 * @param color 颜色
 * @param opacity 透明度
 * @returns 材质对象
 */
export const createBasicMaterial = (
  color: string | number = 0xffffff,
  opacity: number = 1,
  transparent: boolean = false
): THREE.MeshStandardMaterial => {
  return new THREE.MeshStandardMaterial({
    color,
    opacity,
    transparent,
    metalness: 0.2,
    roughness: 0.8,
  });
};

/**
 * 创建线框材质
 * @param color 颜色
 * @returns 线框材质
 */
export const createWireframeMaterial = (
  color: string | number = 0x000000
): THREE.MeshBasicMaterial => {
  return new THREE.MeshBasicMaterial({
    color,
    wireframe: true,
    transparent: true,
    opacity: 0.3,
  });
};

/**
 * 创建平面
 * @param width 宽度
 * @param height 高度
 * @param color 颜色
 * @param segments 分段数
 * @returns 平面网格
 */
export const createPlane = (
  width: number = 10,
  height: number = 10,
  color: string | number = 0xeeeeee,
  segments: number = 10
): THREE.Mesh => {
  const geometry = new THREE.PlaneGeometry(width, height, segments, segments);
  const material = createBasicMaterial(color);
  const plane = new THREE.Mesh(geometry, material);
  
  // 旋转平面使其水平
  plane.rotation.x = -Math.PI / 2;
  
  return plane;
};

/**
 * 创建网格平面（带网格线）
 * @param size 大小
 * @param divisions 分割数
 * @param color 颜色
 * @returns 网格辅助对象
 */
export const createGrid = (
  size: number = 10,
  divisions: number = 10,
  color: string | number = 0xcccccc
): THREE.GridHelper => {
  return new THREE.GridHelper(size, divisions, color, color);
};

/**
 * 创建3D文本
 * @param text 文本内容
 * @param font 字体对象
 * @param size 大小
 * @param height 厚度
 * @param color 颜色
 * @returns 文本网格
 */
export const createText = (
  text: string,
  font: Font,
  size: number = 1,
  height: number = 0.2,
  color: string | number = 0x333333
): THREE.Mesh => {
  const geometry = new TextGeometry(text, {
    font,
    size,
    height,
    curveSegments: 12,
    bevelEnabled: true,
    bevelThickness: 0.05,
    bevelSize: 0.02,
    bevelOffset: 0,
    bevelSegments: 5,
  });
  
  // 居中文本
  geometry.computeBoundingBox();
  const centerOffset = new THREE.Vector3(
    (geometry.boundingBox!.max.x - geometry.boundingBox!.min.x) / -2,
    0,
    (geometry.boundingBox!.max.z - geometry.boundingBox!.min.z) / -2
  );
  geometry.translate(centerOffset.x, 0, centerOffset.z);
  
  const material = createBasicMaterial(color);
  const textMesh = new THREE.Mesh(geometry, material);
  
  return textMesh;
};

/**
 * 创建颜色渐变材质
 * @param colors 颜色数组
 * @param direction 渐变方向 (0: 水平, 1: 垂直)
 * @returns 材质
 */
export const createGradientMaterial = (
  colors: string[],
  direction: number = 0
): THREE.ShaderMaterial => {
  // 将颜色转换为RGB
  const rgbColors = colors.map(color => {
    const c = new THREE.Color(color);
    return [c.r, c.g, c.b];
  });

  return new THREE.ShaderMaterial({
    uniforms: {
      colorStops: { value: rgbColors },
      direction: { value: direction },
    },
    vertexShader: `
      varying vec2 vUv;
      void main() {
        vUv = uv;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      varying vec2 vUv;
      uniform vec3 colorStops[${rgbColors.length}];
      uniform int direction;
      
      void main() {
        float t = direction == 0 ? vUv.x : vUv.y;
        t = clamp(t, 0.0, 1.0);
        
        int numStops = ${rgbColors.length};
        float segment = 1.0 / float(numStops - 1);
        
        int i = int(floor(t / segment));
        i = clamp(i, 0, numStops - 2);
        
        float localT = (t - float(i) * segment) / segment;
        vec3 color = mix(colorStops[i], colorStops[i+1], localT);
        
        gl_FragColor = vec4(color, 1.0);
      }
    `,
  });
};

/**
 * 为对象添加悬停效果
 * @param object 3D对象
 * @param originalColor 原始颜色
 * @param hoverColor 悬停颜色
 */
export const addHoverEffect = (
  object: THREE.Object3D,
  originalColor: number | string,
  hoverColor: number | string
): void => {
  const original = new THREE.Color(originalColor);
  const hover = new THREE.Color(hoverColor);
  
  object.traverse((child) => {
    if (child instanceof THREE.Mesh) {
      // 保存原始材质
      const originalMaterial = child.material;
      
      // 鼠标进入
      child.onBeforeRender = () => {
        if ((child.material as THREE.MeshStandardMaterial).color) {
          (child.material as THREE.MeshStandardMaterial).color.copy(hover);
        }
      };
      
      // 鼠标离开
      child.onAfterRender = () => {
        if ((child.material as THREE.MeshStandardMaterial).color) {
          (child.material as THREE.MeshStandardMaterial).color.copy(original);
        }
      };
    }
  });
};

/**
 * 加载字体
 * @param url 字体URL
 * @returns 字体对象
 */
export const loadFont = async (url: string): Promise<Font> => {
  return new Promise((resolve, reject) => {
    const loader = new THREE.FontLoader();
    loader.load(
      url,
      (font) => resolve(font),
      undefined,
      (error) => reject(new Error(`Failed to load font: ${error.message}`))
    );
  });
};

/**
 * 计算对象的包围盒并居中
 * @param object 3D对象
 */
export const centerObject = (object: THREE.Object3D): void => {
  object.geometry.computeBoundingBox();
  const box = object.geometry.boundingBox;
  
  if (box) {
    const center = new THREE.Vector3();
    box.getCenter(center);
    object.position.sub(center);
  }
};

/**
 * 创建发光效果
 * @param object 要应用发光效果的对象
 * @param color 发光颜色
 * @param strength 发光强度
 * @returns 包含原始对象和发光效果的组
 */
export const createGlowEffect = (
  object: THREE.Object3D,
  color: number | string = 0x00ffff,
  strength: number = 2
): THREE.Group => {
  const group = new THREE.Group();
  
  // 添加原始对象
  group.add(object);
  
  // 创建发光材质
  const glowMaterial = new THREE.ShaderMaterial({
    uniforms: {
      glowColor: { value: new THREE.Color(color) },
      glowStrength: { value: strength },
    },
    vertexShader: `
      varying vec3 vNormal;
      void main() {
        vNormal = normalize(normalMatrix * normal);
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      varying vec3 vNormal;
      uniform vec3 glowColor;
      uniform float glowStrength;
      
      void main() {
        float intensity = 1.0 - abs(dot(vNormal, vec3(0.0, 0.0, 1.0)));
        gl_FragColor = vec4(glowColor, pow(intensity, 3.0) * glowStrength);
      }
    `,
    side: THREE.BackSide,
    blending: THREE.AdditiveBlending,
    transparent: true,
  });
  
  // 创建发光网格（克隆原始对象的几何体）
  object.traverse((child) => {
    if (child instanceof THREE.Mesh) {
      const glowMesh = new THREE.Mesh(
        child.geometry.clone(),
        glowMaterial
      );
      glowMesh.scale.multiplyScalar(1.05); // 稍微大一点以产生发光效果
      group.add(glowMesh);
    }
  });
  
  return group;
};