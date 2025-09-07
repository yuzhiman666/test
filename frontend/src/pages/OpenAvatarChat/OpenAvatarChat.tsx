import axios from 'axios';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';

const ChatContainer = styled.div`
  max-width: 800px;
  margin: 2rem auto;
  padding: 0 1rem;
`;

const ChatWindow = styled.div`
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
`;

const ChatHeader = styled.div`
  background-color: #3498db;
  color: white;
  padding: 1rem;
  text-align: center;
  font-size: 1.2rem;
  font-weight: bold;
`;

const MessagesContainer = styled.div`
  height: 500px;
  overflow-y: auto;
  padding: 1rem;
  background-color: #f9f9f9;
`;

const Message = styled.div`
  margin-bottom: 1rem;
  max-width: 70%;
  
  &.avatar {
    margin-right: auto;
    .message-content {
      background-color: white;
      border: 1px solid #e0e0e0;
    }
  }
  
  &.user {
    margin-left: auto;
    .message-content {
      background-color: #3498db;
      color: white;
    }
  }
  
  .message-content {
    padding: 0.8rem 1rem;
    border-radius: 18px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  }
`;

const InputArea = styled.div`
  display: flex;
  padding: 1rem;
  background-color: white;
  border-top: 1px solid #e0e0e0;
  
  input {
    flex: 1;
    padding: 0.8rem 1rem;
    border: 1px solid #e0e0e0;
    border-radius: 20px;
    outline: none;
    
    &:focus {
      border-color: #3498db;
    }
  }
  
  button {
    margin-left: 0.5rem;
    padding: 0.8rem 1.5rem;
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 20px;
    cursor: pointer;
    transition: background-color 0.3s;
    
    &:hover {
      background-color: #2980b9;
    }
  }
`;

const OpenAvatarChat = () => {
  const { t } = useTranslation();
  const [messages, setMessages] = useState([
    { sender: 'avatar', text: t('avatar.greeting') }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  // 模拟数字人回复（实际项目中替换为真实API调用）
  const handleSend = async () => {
    if (!input.trim() || isLoading) return;
    
    // 添加用户消息
    const userMessage = { sender: 'user', text: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    
    // 模拟API延迟（1秒后返回回复）
    // setTimeout(() => {
    //   const replies = [
    //     "您可以选择我们的0首付方案，最长分期60个月，年利率仅3%",
    //     "智能轿车目前有1万元购车补贴，贷款审批最快1小时完成",
    //     "如果您是教师或医护人员，还可以额外享受500元优惠",
    //     "需要我帮您计算具体车型的月供吗？请告诉我您心仪的车型和预算"
    //   ];
    //   const randomReply = replies[Math.floor(Math.random() * replies.length)];
    //   setMessages(prev => [...prev, { sender: 'avatar', text: randomReply }]);
    //   setIsLoading(false);
    // }, 1000);

    // 改为真实API调用（示例）
    try {
      const response = await axios.post('/api/avatar/chat', { message: input });
      setMessages(prev => [...prev, { sender: 'avatar', text: response.data.reply }]);
    } catch (err) {
      console.error('Chat error:', err);
    } finally {
      setIsLoading(false);
    }
  };
  
  // 按Enter发送消息
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleSend();
  };
  
  // 自动滚动到最新消息
  useEffect(() => {
    const container = document.getElementById('messages-container');
    if (container) container.scrollTop = container.scrollHeight;
  }, [messages]);
  
  return (
    <ChatContainer>
      <ChatWindow>
        <ChatHeader>{t('avatar.chatTitle')}</ChatHeader>
        <MessagesContainer id="messages-container">
          {messages.map((msg, idx) => (
            <Message key={idx} className={msg.sender}>
              <div className="message-content">{msg.text}</div>
            </Message>
          ))}
          {isLoading && (
            <Message className="avatar">
              <div className="message-content">{t('avatar.typing')}...</div>
            </Message>
          )}
        </MessagesContainer>
        <InputArea>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={t('avatar.placeholder')}
            disabled={isLoading}
          />
          <button onClick={handleSend} disabled={isLoading}>
            {t('avatar.send')}
          </button>
        </InputArea>
      </ChatWindow>
    </ChatContainer>
  );
};

export default OpenAvatarChat;