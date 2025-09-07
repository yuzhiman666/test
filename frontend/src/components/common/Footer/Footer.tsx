import { useTranslation } from 'react-i18next';
import styled from 'styled-components';

const FooterContainer = styled.footer`
  background-color: #000000;
  color: #ffffff;
  padding: 3rem 5% 1.5rem;
  margin-top: 3rem;
`;

const FooterContent = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
`;

const FooterColumn = styled.div`
  h3 {
    font-size: 1.2rem;
    margin-bottom: 1rem;
    color: #f0f0f0;
  }
  
  ul {
    list-style: none;
    padding: 0;
  }
  
  li {
    margin-bottom: 0.7rem;
  }
  
  a {
    color: #bbbbbb;
    text-decoration: none;
    transition: color 0.3s;
    
    &:hover {
      color: #ffffff;
    }
  }
`;

const Copyright = styled.div`
  text-align: center;
  padding-top: 1.5rem;
  border-top: 1px solid #333333;
  color: #999999;
  font-size: 0.9rem;
`;

const Footer = () => {
  const { t } = useTranslation();
  
  return (
    <FooterContainer>
      <FooterContent>
        <FooterColumn>
          <h3>{t('footer.company')}</h3>
          <ul>
            <li><a href="#">{t('footer.about')}</a></li>
            <li><a href="#">{t('footer.careers')}</a></li>
            <li><a href="#">{t('footer.press')}</a></li>
            <li><a href="#">{t('footer.contact')}</a></li>
          </ul>
        </FooterColumn>
        
        <FooterColumn>
          <h3>{t('footer.services')}</h3>
          <ul>
            <li><a href="#">{t('footer.financing')}</a></li>
            <li><a href="#">{t('footer.insurance')}</a></li>
            <li><a href="#">{t('footer.maintenance')}</a></li>
            <li><a href="#">{t('footer.warranty')}</a></li>
          </ul>
        </FooterColumn>
        
        <FooterColumn>
          <h3>{t('footer.legal')}</h3>
          <ul>
            <li><a href="#">{t('footer.terms')}</a></li>
            <li><a href="#">{t('footer.privacy')}</a></li>
            <li><a href="#">{t('footer.cookies')}</a></li>
            <li><a href="#">{t('footer.compliance')}</a></li>
          </ul>
        </FooterColumn>
        
        <FooterColumn>
          <h3>{t('footer.newsletter')}</h3>
          <p>{t('footer.newsletterDesc')}</p>
          <div style={{ display: 'flex', marginTop: 10 }}>
            <input 
              type="email" 
              placeholder={t('footer.email')}
              style={{ padding: '8px', flex: 1, border: 'none', borderRadius: '4px 0 0 4px' }}
            />
            <button style={{
              padding: '8px 16px',
              background: '#3498db',
              color: 'white',
              border: 'none',
              borderRadius: '0 4px 4px 0',
              cursor: 'pointer',
            }}>
              {t('footer.subscribe')}
            </button>
          </div>
        </FooterColumn>
      </FooterContent>
      
      <Copyright>
        © {new Date().getFullYear()} AutoFinance AI. {t('footer.rights')}
      </Copyright>
    </FooterContainer>
  );
};

export default Footer;