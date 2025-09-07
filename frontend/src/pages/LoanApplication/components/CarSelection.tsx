// src/pages/LoanApplication/components/CarSelection.tsx
import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styles from '../LoanApplication.module.css';
import { CarSelection } from '../../../types/loan.ts';
import { getCarBrands, getCarModels, getCarPrice } from '../../../services/loanService.ts';
import i18n from '@/i18n.ts';

// 定义宝马车型价格关联类型
interface MultiLanguageStr {
  zh: string;
  en: string;
  ja: string;
}

interface MultiLanguageList {
  zh: string[];
  en: string[];
  ja: string[];
}

interface MultiLanguagePrice {
  zh: number[];
  en: number[];
  ja: number[];
}

interface CarBrand {
  id: string;
  name: MultiLanguageStr;
  country: MultiLanguageStr;
  series: MultiLanguageList;
  price: MultiLanguagePrice;  // 新增价格字段
  created_at: string;
}

interface CarSelectionProps {
  data: Partial<CarSelection>;
  onChange: (data: CarSelection) => void;
  disabled: boolean;
}

const CarSelectionComponent: React.FC<CarSelectionProps> = ({ data, onChange, disabled }) => {
  const { t } = useTranslation();
  const [brands, setBrands] = useState<CarBrand[]>([]);  // 存储完整品牌数据
  const [models, setModels] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [priceLoading, setPriceLoading] = useState(false);
  
  // 加载汽车品牌数据（多语言）
  // useEffect(() => {
  //   const loadBrands = async () => {
  //     try {
  //       setLoading(true);
  //       const response = await getCarBrands();
  //       setBrands(response.data);
  //       console.log("Loaded car brands data:", response.data);
  //     } catch (error) {
  //       console.error('Failed to load car brands', error);
  //       alert(t('loanApplication.carSelection.loadBrandError'));
  //     } finally {
  //       setLoading(false);
  //     }
  //   };
    
  //   loadBrands();
  // }, [t]);  // 只依赖t，避免不必要的重加载
  
  useEffect(() => {
  // 只在品牌数据为空时加载，避免重复加载
    if (brands.length === 0) {
      const loadBrands = async () => {
        try {
          setLoading(true);
          const response = await getCarBrands();
          // 检查返回数据是否有效
          if (Array.isArray(response.data) && response.data.length > 0) {
            setBrands(response.data);
            console.log("Loaded car brands data:", response.data);
          } else {
            console.warn("No car brands data received from server");
            // 可以考虑设置一个默认品牌列表作为备选
          }
        } catch (error) {
          console.error('Failed to load car brands', error);
          alert(t('loanApplication.carSelection.loadBrandError'));
        } finally {
          setLoading(false);
        }
      };
      
      loadBrands();
    }
  }, [t, brands.length]);  // 添加brands.length作为依赖，避免无限循环

  // 根据当前语言和选中品牌加载车型（优化逻辑）
  useEffect(() => {
    if (brands.length === 0 || !data.carBrand) {
      setModels([]);
      return;
    }

    // 根据选中的品牌ID匹配对应的品牌数据
    const currentBrand = brands.find(brand => brand.id === data.carBrand);
    if (!currentBrand) {
      setModels([]);
      return;
    }

    // 1. 在加载车型的useEffect中
    const validLangs: (keyof MultiLanguageList)[] = ['zh', 'en', 'ja'];
    // 提取当前语言的车型列表
    // const currentLang = i18n.language as keyof MultiLanguageList;
    const currentLang = validLangs.includes(i18n.language as keyof MultiLanguageList)
      ? i18n.language as keyof MultiLanguageList
      : 'zh';
    setModels(currentBrand.series[currentLang] || []);
  }, [data.carBrand, brands, i18n.language]); // 明确依赖项
  
  // 处理表单变化（增加品牌切换时的数据重置）
  const handleChange = async (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    // 初始化新数据，品牌变更时重置车型和价格
    const newData: Partial<CarSelection> = { 
      ...data, 
      [name]: name === 'carPrice' ? Number(value) : value 
    };

    if (name === 'carBrand') {
      // 获取选中选项的显示文本（如"宝马"）
      const selectElement = e.target as HTMLSelectElement;
      const selectedLabel = selectElement.options[selectElement.selectedIndex].text;
      newData.carBrand = value; // 存储品牌value（如"68b1399e1a0761da6fe692a4"）
      newData.carBrandLabel = selectedLabel; // 存储品牌显示文本     
      // 品牌变更时重置车型和价格
      newData.carModel = '';
      newData.carPrice = 0; // 用空字符串而非undefined，避免必选属性缺失
    }
    if (name === 'carModel' && newData.carBrand && newData.carModel) {
      // 找到当前选中的品牌
      const currentBrand = brands.find(brand => brand.id === newData.carBrand);
      if (currentBrand) {
        // 确保语言合法
        const validLangs: (keyof MultiLanguagePrice)[] = ['zh', 'en', 'ja'];
        const currentLang = validLangs.includes(i18n.language as keyof MultiLanguagePrice)
          ? i18n.language as keyof MultiLanguagePrice
          : 'zh';
        
        // 新增数组长度校验
        if (currentBrand.series[currentLang].length !== currentBrand.price[currentLang].length) {
          console.error(`车型与价格数组长度不匹配: ${currentBrand.series[currentLang].length} vs ${currentBrand.price[currentLang].length}`);
          alert(t('loanApplication.carSelection.dataMismatch')); // 需要新增此翻译
          newData.carPrice = undefined;
          return;
        }

        // 通过车型在models数组中的索引匹配价格
        const modelIndex = models.indexOf(newData.carModel);
        if (modelIndex !== -1 && modelIndex < currentBrand.price[currentLang].length) {
          newData.carPrice = currentBrand.price[currentLang][modelIndex];
        } else {
          newData.carPrice = undefined;
        }

        // 在这里添加校验逻辑（关键位置）
        if (newData.carPrice === undefined) {
          console.warn(`No price found for model ${newData.carModel}`);
          alert(t('loanApplication.carSelection.invalidPrice')); // 需要在i18n中添加对应翻译
        }
      }
    }
    
    onChange(newData as CarSelection);
  };
  
  return (
    <div className={styles.section}>
      <h3>{t('loanApplication.carSelection.title')}</h3>
      
      <div className={styles.formGroup}>
        <label>{t('loanApplication.carSelection.carBrand')}</label>
        <select
          name="carBrand"
          value={data.carBrand || ''}
          onChange={handleChange}
          disabled={disabled || loading}
          required
        >
          <option value="">{t('loanApplication.selectOption')}</option>
          {/* 修复品牌选项渲染错误，使用多语言名称和ID */}
          {brands.map(brand => {
            // 2. 在品牌下拉框渲染中
            const validLangs: (keyof MultiLanguageStr)[] = ['zh', 'en', 'ja'];
            // const currentLang = i18n.language as keyof MultiLanguageStr;
            const currentLang = validLangs.includes(i18n.language as keyof MultiLanguageStr)
              ? i18n.language as keyof MultiLanguageStr
              : 'zh';
            return (
              <option key={brand.id} value={brand.id}>
                {brand.name[currentLang]}
              </option>
            );
          })}
        </select>
      </div>
      
      <div className={styles.formGroup}>
        <label>{t('loanApplication.carSelection.carModel')}</label>
        <select
          name="carModel"
          value={data.carModel || ''}
          onChange={handleChange}
          disabled={disabled || loading || priceLoading || !data.carBrand}
          required
        >
          <option value="">{t('loanApplication.selectOption')}</option>
          {models.map(model => (
            <option key={model} value={model}>{model}</option>
          ))}
        </select>
      </div>
      
      <div className={styles.formGroup}>
        <label>{t('loanApplication.carSelection.carYear')}</label>
        <select
          name="carYear"
          value={data.carYear || ''}
          onChange={handleChange}
          disabled={disabled}
          required
        >
          <option value="">{t('loanApplication.selectOption')}</option>
          {[...Array(10)].map((_, i) => {
            const year = new Date().getFullYear() - i;
            return <option key={year} value={year.toString()}>{year}</option>;
          })}
        </select>
      </div>
      
      <div className={styles.formGroup}>
        <label>{t('loanApplication.carSelection.carType')}</label>
        <select
          name="carType"
          value={data.carType || ''}
          onChange={handleChange}
          disabled={disabled}
          required
        >
          <option value="">{t('loanApplication.selectOption')}</option>
          <option value="sedan">{t('loanApplication.carSelection.sedan')}</option>
          <option value="suv">{t('loanApplication.carSelection.suv')}</option>
          <option value="electric">{t('loanApplication.carSelection.electric')}</option>
          <option value="hybrid">{t('loanApplication.carSelection.hybrid')}</option>
        </select>
      </div>
      
      <div className={styles.formGroup}>
        <label>{t('loanApplication.carSelection.carPrice')}</label>
        <input
          type="number"
          name="carPrice"
          // 修复价格为0时显示为空的问题
          // value={data.carPrice ?? ''}
          // 仅在undefined时显示空，0是有效价格
          value={data.carPrice !== undefined ? data.carPrice : ''}
          onChange={handleChange}
          disabled={disabled || priceLoading}
          required
          placeholder={t('loanApplication.carSelection.enterPrice')}
        />
      </div>
    </div>
  );
};

export default CarSelectionComponent;