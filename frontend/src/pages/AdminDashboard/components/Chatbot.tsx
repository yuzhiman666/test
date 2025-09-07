import React, { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { 
  SendOutlined, 
  CloseOutlined, 
  MinusOutlined,
  RobotOutlined,
  UserOutlined,
  LoadingOutlined
} from '@ant-design/icons';
import { Input, Button, Avatar, Tooltip } from 'antd'; // 移除ScrollArea导入
import styles from './Chatbot.module.css';
import { adminChatQuery } from '../../../services/adminService.ts';

const Chatbot: React.FC = () => {
  const { t } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState<Array<{
    text: string;
    sender: 'user' | 'bot';
    timestamp: Date;
  }>>([
    {
      text: t('chatbot.welcome'),
      sender: 'bot',
      timestamp: new Date()
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  
  // 自动滚动到最新消息
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // 发送消息
  const sendMessage = async () => {
    if (!inputText.trim() || loading) return;
    
    // 添加用户消息
    const userMessage = {
      text: inputText.trim(),
      sender: 'user' as const,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setLoading(true);
    
    try {
      // 调用API获取机器人回复
      const response = await adminChatQuery(inputText.trim());
      const botMessage = {
        text: response.data.reply || t('chatbot.defaultReply'),
        sender: 'bot' as const,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Chatbot API error:', error);
      const errorMessage = {
        text: t('chatbot.errorReply'),
        sender: 'bot' as const,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  // 处理输入框按键
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // 切换聊天窗口显示状态
  const toggleChat = () => {
    setIsOpen(!isOpen);
    setIsMinimized(false);
  };

  // 最小化聊天窗口
  const minimizeChat = () => {
    setIsMinimized(true);
  };

  // 恢复聊天窗口
  const restoreChat = () => {
    setIsMinimized(false);
  };

  return (
    <div className={styles.chatbotContainer}>
      {/* 聊天窗口头部（始终可见） */}
      <div className={`${styles.chatHeader} ${isOpen ? styles.open : ''}`}>
        <div className={styles.headerContent} onClick={isMinimized ? restoreChat : toggleChat}>
          <RobotOutlined className={styles.botIcon} />
          <span className={styles.headerTitle}>{t('chatbot.title')}</span>
        </div>
        
        {isOpen && !isMinimized && (
          <div className={styles.headerActions}>
            <Tooltip title={t('chatbot.minimize')}>
              <Button 
                icon={<MinusOutlined />} 
                size="small" 
                onClick={minimizeChat}
                className={styles.headerButton}
              />
            </Tooltip>
            <Tooltip title={t('chatbot.close')}>
              <Button 
                icon={<CloseOutlined />} 
                size="small" 
                onClick={toggleChat}
                className={styles.headerButton}
              />
            </Tooltip>
          </div>
        )}
      </div>
      
      {/* 聊天窗口内容 */}
      {isOpen && !isMinimized && (
        <div className={styles.chatContent}>
          {/* 消息区域：用div替代ScrollArea，通过CSS实现滚动 */}
          <div 
            ref={messagesContainerRef}
            className={styles.messagesContainer} // 关键：通过CSS设置高度和滚动
          >
            <div className={styles.messagesList}>
              {messages.map((msg, index) => (
                <div 
                  key={index} 
                  className={`${styles.message} ${msg.sender === 'user' ? styles.userMessage : styles.botMessage}`}
                >
                  <Avatar className={styles.avatar}>
                    {msg.sender === 'user' ? <UserOutlined /> : <RobotOutlined />}
                  </Avatar>
                  <div className={styles.messageBubble}>
                    <p className={styles.messageText}>{msg.text}</p>
                    <span className={styles.timestamp}>
                      {msg.timestamp.toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
          </div>
          
          {/* 输入区域 */}
          <div className={styles.inputArea}>
            <Input
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={t('chatbot.placeholder')}
              className={styles.inputField}
              disabled={loading}
            />
            <Button 
              type="primary" 
              icon={loading ? <LoadingOutlined spin /> : <SendOutlined />} 
              onClick={sendMessage}
              disabled={!inputText.trim() || loading}
              className={styles.sendButton}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default Chatbot;