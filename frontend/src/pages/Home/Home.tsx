import { useTranslation } from 'react-i18next';
import ModelViewer from '../../components/3d/ModelViewer/ModelViewer.tsx';
import styled from 'styled-components';

// 新增：箭头样式组件
const DownArrow = styled.div`
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  cursor: pointer;
  z-index: 10;
  
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  
  // 箭头图标样式（模拟箭头.png红框内容）
  &::after {
    content: '';
    width: 20px;
    height: 20px;
    border-bottom: 3px solid #3498db;
    border-right: 3px solid #3498db;
    transform: rotate(45deg);
  }
  
  &:hover {
    background-color: white;
    transform: translateX(-50%) scale(1.1);
    transition: all 0.3s ease;
  }
`;

// 首页样式组件
const HeroSection = styled.section`
  position: relative; // 确保箭头可以绝对定位
  width: 100%;
  height: 80vh;  // 与ModelViewer高度一致
`;

const HeroContent = styled.div`
  position: absolute;
  top: 5%;
  left: 5%;
  max-width: 500px;
  z-index: 10;
  
  h1 {
    font-size: 3rem;
    margin-bottom: 1rem;
    color: #2c3e50;
  }
  
  p {
    font-size: 1.2rem;
    margin-bottom: 2rem;
    color: #34495e;
  }
  
  button {
    padding: 1rem 2rem;
    font-size: 1rem;
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.3s;
    
    &:hover {
      background-color: #2980b9;
    }
  }
`;

const Section = styled.section`
  padding: 5rem 5%;
  text-align: center;
`;

const SectionTitle = styled.h2`
  font-size: 2.5rem;
  margin-bottom: 3rem;
  color: #2c3e50;
`;

const FeaturesGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-top: 3rem;
`;

const FeatureCard = styled.div`
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  transition: transform 0.3s;
  
  &:hover {
    transform: translateY(-5px);
  }
  
  i {
    font-size: 2.5rem;
    color: #3498db;
    margin-bottom: 1.5rem;
  }
  
  h3 {
    font-size: 1.5rem;
    margin-bottom: 1rem;
    color: #2c3e50;
  }
  
  p {
    color: #7f8c8d;
    line-height: 1.6;
  }
`;

const CarModelsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 3rem;
  margin-top: 3rem;
`;

const CarModelCard = styled.div`
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  
  img {
    width: 100%;
    height: 200px;
    object-fit: cover;
  }
  
  .car-info {
    padding: 1.5rem;
    text-align: left;
    
    h3 {
      font-size: 1.5rem;
      margin-bottom: 0.5rem;
      color: #2c3e50;
    }
    
    .price {
      color: #3498db;
      font-size: 1.2rem;
      font-weight: bold;
      margin-bottom: 1rem;
    }
    
    button {
      width: 100%;
      padding: 0.8rem;
      background-color: #f5f5f5;
      color: #34495e;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      transition: background-color 0.3s;
      
      &:hover {
        background-color: #e0e0e0;
      }
    }
  }
`;

const FinanceSection = styled(Section)`
  background-color: #f9f9f9;
`;

const FinanceContent = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 3rem;
  align-items: center;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
  
  .text-content {
    text-align: left;
    
    p {
      font-size: 1.1rem;
      line-height: 1.8;
      color: #34495e;
      margin-bottom: 1.5rem;
    }
  }
`;

const CalculatorCard = styled.div`
  background-color: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  
  h3 {
    font-size: 1.5rem;
    margin-bottom: 1.5rem;
    color: #2c3e50;
  }
  
  .input-group {
    margin-bottom: 1rem;
    text-align: left;
    
    label {
      display: block;
      margin-bottom: 0.5rem;
      color: #34495e;
    }
    
    input {
      width: 100%;
      padding: 0.8rem;
      border: 1px solid #ddd;
      border-radius: 4px;
    }
  }
  
  .result {
    margin: 1.5rem 0;
    padding: 1rem;
    background-color: #f5f5f5;
    border-radius: 4px;
    
    p {
      font-weight: bold;
      color: #2c3e50;
    }
  }
  
  button {
    width: 100%;
    padding: 0.8rem;
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.3s;
    
    &:hover {
      background-color: #2980b9;
    }
  }
`;

const TestimonialsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-top: 3rem;
`;

const TestimonialCard = styled.div`
  padding: 2rem;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  
  .stars {
    color: #f1c40f;
    margin-bottom: 1rem;
  }
  
  p {
    font-style: italic;
    color: #3498db;
    margin-bottom: 1.5rem;
    line-height: 1.6;
  }
  
  .author {
    display: flex;
    align-items: center;
    gap: 1rem;
    
    img {
      width: 50px;
      height: 50px;
      border-radius: 50%;
      object-fit: cover;
    }
    
    .author-info {
      text-align: left;
      
      h4 {
        font-weight: bold;
        color: #2c3e50;
      }
      
      p {
        font-size: 0.9rem;
        color: #7f8c8d;
        margin: 0;
        font-style: normal;
      }
    }
  }
`;

const Home = () => {
  const { t } = useTranslation();

  // 新增：滚动到核心功能区域
  const scrollToFeatures = () => {
    document.getElementById('features')?.scrollIntoView({
      behavior: 'smooth'
    });
  };
  
  return (
    <>
      {/* 首页顶部：3D模型 + 文字宣传 */}
      <HeroSection>
        <HeroContent>
          <h1>{t('home.hero.title')}</h1>
          <p>{t('home.hero.subtitle')}</p>
          {/* <button>{t('home.hero.cta')}</button> */}
          <button 
            onClick={() => window.open('http://127.0.0.1:8282/ui', '_blank')}
          >
            {t('home.hero.cta')}
          </button>
        </HeroContent>
        <ModelViewer /> {/* 3D汽车+数字人模型 */}
        {/* 新增：下箭头锚点 */}
        <DownArrow onClick={scrollToFeatures} />
      </HeroSection>
      
      {/* 核心功能区 */}
      <Section id="features">
        <SectionTitle>{t('home.features.title')}</SectionTitle>
        <FeaturesGrid>
          <FeatureCard>
            <i className="fas fa-car"></i>
            <h3>{t('home.features.feature1.title')}</h3>
            <p>{t('home.features.feature1.desc')}</p>
          </FeatureCard>
          <FeatureCard>
            <i className="fas fa-hand-holding-usd"></i>
            <h3>{t('home.features.feature2.title')}</h3>
            <p>{t('home.features.feature2.desc')}</p>
          </FeatureCard>
          <FeatureCard>
            <i className="fas fa-robot"></i>
            <h3>{t('home.features.feature3.title')}</h3>
            <p>{t('home.features.feature3.desc')}</p>
          </FeatureCard>
        </FeaturesGrid>
      </Section>
      
      {/* 车型展示区 */}
      <Section id="models">
        <SectionTitle>{t('home.models.title')}</SectionTitle>
        <CarModelsGrid>
          <CarModelCard>
            <img src="https://picsum.photos/id/111/800/500" alt="智能轿车" />
            <div className="car-info">
              <h3>{t('home.models.model1.name')}</h3>
              <div className="price">{t('home.models.model1.price')}</div>
              <button>{t('home.models.learnMore')}</button>
            </div>
          </CarModelCard>
          <CarModelCard>
            <img src="https://picsum.photos/id/1072/800/500" alt="豪华SUV" />
            <div className="car-info">
              <h3>{t('home.models.model2.name')}</h3>
              <div className="price">{t('home.models.model2.price')}</div>
              <button>{t('home.models.learnMore')}</button>
            </div>
          </CarModelCard>
          <CarModelCard>
            <img src="https://picsum.photos/id/1071/800/500" alt="纯电动车" />
            <div className="car-info">
              <h3>{t('home.models.model3.name')}</h3>
              <div className="price">{t('home.models.model3.price')}</div>
              <button>{t('home.models.learnMore')}</button>
            </div>
          </CarModelCard>
        </CarModelsGrid>
      </Section>
      
      {/* 金融贷款区 */}
      <FinanceSection id="finance">
        <SectionTitle>{t('home.finance.title')}</SectionTitle>
        <FinanceContent>
          <div className="text-content">
            <p>{t('home.finance.desc1')}</p>
            <p>{t('home.finance.desc2')}</p>
            <p>{t('home.finance.desc3')}</p>
          </div>
          <CalculatorCard>
            <h3>{t('home.finance.calculator.title')}</h3>
            <div className="input-group">
              <label>{t('home.finance.calculator.carPrice')}</label>
              <input type="number" placeholder={t('home.finance.calculator.enterPrice')} />
            </div>
            <div className="input-group">
              <label>{t('home.finance.calculator.downPayment')} (%)</label>
              <input type="number" placeholder={t('home.finance.calculator.enterPercentage')} />
            </div>
            <div className="input-group">
              <label>{t('home.finance.calculator.loanTerm')} ({t('home.finance.calculator.months')})</label>
              <input type="number" placeholder={t('home.finance.calculator.enterTerm')} />
            </div>
            <div className="input-group">
              <label>{t('home.finance.calculator.interestRate')} (%)</label>
              <input type="number" placeholder={t('home.finance.calculator.enterRate')} />
            </div>
            <div className="result">
              <p>{t('home.finance.calculator.monthlyPayment')}: <span>--</span></p>
            </div>
            <button>{t('home.finance.calculator.calculate')}</button>
          </CalculatorCard>
        </FinanceContent>
      </FinanceSection>
      
      {/* 用户评价区 */}
      <Section id="testimonials">
        <SectionTitle>{t('home.testimonials.title')}</SectionTitle>
        <TestimonialsGrid>
          <TestimonialCard>
            <div className="stars">
              <i className="fas fa-star"></i>
              <i className="fas fa-star"></i>
              <i className="fas fa-star"></i>
              <i className="fas fa-star"></i>
              <i className="fas fa-star"></i>
            </div>
            <p>{t('home.testimonials.testimonial1.text')}</p>
            <div className="author">
              <img src="https://picsum.photos/id/1012/100/100" alt="张先生" />
              <div className="author-info">
                <h4>{t('home.testimonials.testimonial1.name')}</h4>
                <p>{t('home.testimonials.testimonial1.location')}</p>
              </div>
            </div>
          </TestimonialCard>
          <TestimonialCard>
            <div className="stars">
              <i className="fas fa-star"></i>
              <i className="fas fa-star"></i>
              <i className="fas fa-star"></i>
              <i className="fas fa-star"></i>
              <i className="fas fa-star"></i>
            </div>
            <p>{t('home.testimonials.testimonial2.text')}</p>
            <div className="author">
              <img src="https://picsum.photos/id/1027/100/100" alt="李女士" />
              <div className="author-info">
                <h4>{t('home.testimonials.testimonial2.name')}</h4>
                <p>{t('home.testimonials.testimonial2.location')}</p>
              </div>
            </div>
          </TestimonialCard>
        </TestimonialsGrid>
      </Section>
    </>
  );
};

export default Home;