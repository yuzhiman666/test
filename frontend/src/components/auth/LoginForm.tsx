import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { UserRole, LoginFormData } from '../../types/auth.ts';
import { validateLoginForm } from '../../utils/validation.ts';

interface LoginFormProps {
  onSubmit: (data: LoginFormData) => void;
  isLoading: boolean;
}

const LoginForm = ({ onSubmit, isLoading }: LoginFormProps) => {
  const { t } = useTranslation();
  const [formData, setFormData] = useState<LoginFormData>({
    identifier: '',
    password: '',
    role: 'customer',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // 清除对应字段的错误
    if (errors[name]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const handleRoleChange = (role: UserRole) => {
    setFormData(prev => ({ ...prev, role }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // 表单验证
    const validationErrors = validateLoginForm(formData);
    if (validationErrors.length > 0) {
      const errorObj: Record<string, string> = {};
      validationErrors.forEach(err => {
        errorObj[err.field] = t(err.message) || err.message;
      });
      setErrors(errorObj);
      return;
    }
    
    onSubmit(formData);
  };

  return (
    <Form onSubmit={handleSubmit}>
      <RoleSelector>
        <RoleOption 
          $isSelected={formData.role === 'customer'}
          onClick={() => handleRoleChange('customer')}
        >
          {t('login.customer')}
        </RoleOption>
        <RoleOption 
          $isSelected={formData.role === 'admin'}
          onClick={() => handleRoleChange('admin')}
        >
          {t('login.admin')}
        </RoleOption>
      </RoleSelector>

      <FormGroup>
        <Label htmlFor="identifier">{t('login.identifier')}</Label>
        <Input
          type="text"
          id="identifier"
          name="identifier"
          value={formData.identifier}
          onChange={handleChange}
          placeholder={t('login.identifierPlaceholder')}
          $error={!!errors.identifier}
        />
        {errors.identifier && <ErrorText>{errors.identifier}</ErrorText>}
      </FormGroup>

      <FormGroup>
        <Label htmlFor="password">{t('login.password')}</Label>
        <Input
          type="password"
          id="password"
          name="password"
          value={formData.password}
          onChange={handleChange}
          placeholder={t('login.passwordPlaceholder')}
          $error={!!errors.password}
        />
        {errors.password && <ErrorText>{errors.password}</ErrorText>}
      </FormGroup>

      <ForgotPasswordLink href="#">{t('login.forgotPassword')}</ForgotPasswordLink>

      <SubmitButton type="submit" disabled={isLoading}>
        {isLoading ? t('login.loading') : t('login.submit')}
      </SubmitButton>
    </Form>
  );
};

// 样式组件
const Form = styled.form`
  width: 100%;
`;

const RoleSelector = styled.div`
  display: flex;
  margin-bottom: 1.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
`;

const RoleOption = styled.div<{ $isSelected: boolean }>`
  flex: 1;
  padding: 0.8rem;
  text-align: center;
  background-color: ${props => props.$isSelected ? '#3498db' : 'white'};
  color: ${props => props.$isSelected ? 'white' : '#333'};
  cursor: pointer;
  transition: all 0.3s;
  
  &:hover {
    background-color: ${props => props.$isSelected ? '#3498db' : '#f5f5f5'};
  }
`;

const FormGroup = styled.div`
  margin-bottom: 1rem;
`;

const Label = styled.label`
  display: block;
  margin-bottom: 0.5rem;
  color: #333;
  font-weight: 500;
`;

const Input = styled.input<{ $error: boolean; $isSelected: boolean }>`
  width: 100%;
  padding: 0.8rem;
  border: 1px solid ${props => props.$error ? 'red' : props.$isSelected ? 'blue' : '#ddd'};
  border-radius: 4px;
  font-size: 1rem;
  
  &:focus {
    outline: none;
    border-color: #3498db;
    box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
  }
`;

const ErrorText = styled.p`
  margin: 0.3rem 0 0 0;
  color: #e74c3c;
  font-size: 0.875rem;
`;

const ForgotPasswordLink = styled.a`
  display: block;
  text-align: right;
  color: #3498db;
  text-decoration: none;
  margin-bottom: 1.5rem;
  font-size: 0.9rem;
  
  &:hover {
    text-decoration: underline;
  }
`;

const SubmitButton = styled.button`
  width: 100%;
  padding: 0.8rem;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s;
  
  &:disabled {
    background-color: #95a5a6;
    cursor: not-allowed;
  }
  
  &:not(:disabled):hover {
    background-color: #2980b9;
  }
`;

export default LoginForm;