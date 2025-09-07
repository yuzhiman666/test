import { useTranslation } from 'react-i18next';
import styled from 'styled-components';

const WechatQrCode = () => {
  const { t } = useTranslation();
  
  return (
    <WechatContainer>
      <QrCodePlaceholder>
        {/* 实际项目中替换为真实二维码图片 */}
        <div style={{ 
          width: '160px', 
          height: '160px', 
          margin: '0 auto',
          backgroundColor: '#f5f5f5',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '12px',
          color: '#999'
        }}>
          微信二维码
        </div>
      </QrCodePlaceholder>
      <WechatText>{t('login.wechatScan')}</WechatText>
    </WechatContainer>
  );
};

const WechatContainer = styled.div`
  text-align: center;
  padding: 1rem;
`;

const QrCodePlaceholder = styled.div`
  margin-bottom: 1rem;
`;

const WechatText = styled.p`
  color: #333;
  margin: 0;
  font-size: 0.9rem;
`;

export default WechatQrCode;