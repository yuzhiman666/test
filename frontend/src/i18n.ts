import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import Backend from 'i18next-http-backend';
import LanguageDetector from 'i18next-browser-languagedetector';

i18n
  .use(Backend) // 加载 public/locales 下的语言文件
  .use(LanguageDetector) // 自动检测浏览器语言
  .use(initReactI18next)
  .init({
    fallbackLng: 'zh', // 默认语言：中文
    debug: false,
    interpolation: {
      escapeValue: false, // React 已自带转义，关闭即可
    },
    supportedLngs: ['zh', 'en', 'ja'], // 支持的语言
    backend: {
      loadPath: '/locales/{{lng}}.json', // 语言文件路径
    }
  });

export default i18n;