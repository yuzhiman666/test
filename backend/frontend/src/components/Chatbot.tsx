import { useState, useRef, useEffect } from 'react';
import { 
  Box, Paper, Typography, TextField, Button, IconButton, 
  List, ListItem, ListItemText, Divider 
} from '@mui/material';
import { Send, Close, Message } from '@mui/icons-material';
import { useStore } from '../store';
import { sendChatMessage } from '../services/api';
import type { ChatMessage } from '../types';
import React from 'react';

const Chatbot = () => {
  const { chatMessages, addChatMessage, clearChatMessages } = useStore();
  const [isOpen, setIsOpen] = useState(false);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // 自动滚动到最新消息
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);
  
  // 发送消息
  const handleSendMessage = async () => {
    if (!message.trim() || loading) return;
    
    // 添加用户消息
    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      content: message.trim(),
      sender: 'user',
      timestamp: new Date()
    };
    addChatMessage(userMessage);
    
    setLoading(true);
    setMessage('');
    
    try {
      // 调用API获取机器人回复
      const botResponse = await sendChatMessage(message.trim());
      
      // 添加机器人回复
      const botMessage: ChatMessage = {
        id: `bot-${Date.now()}`,
        content: botResponse,
        sender: 'bot',
        timestamp: new Date()
      };
      addChatMessage(botMessage);
    } catch (error) {
      console.error('Failed to send message:', error);
      
      // 添加错误消息
      const errorMessage: ChatMessage = {
        id: `error-${Date.now()}`,
        content: '抱歉，无法获取回复，请稍后再试',
        sender: 'bot',
        timestamp: new Date()
      };
      addChatMessage(errorMessage);
    } finally {
      setLoading(false);
    }
  };
  
  // 处理回车发送消息
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };
  
  return (
    <Box 
      sx={{ 
        position: 'fixed', 
        bottom: 20, 
        right: 20, 
        width: isOpen ? 400 : 'auto', 
        height: isOpen ? 500 : 'auto',
        zIndex: 1000
      }}
    >
      {isOpen ? (
        <Paper elevation={3} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
          {/* 聊天头部 */}
          <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">管理员助手</Typography>
            <IconButton size="small" onClick={() => setIsOpen(false)}>
              <Close fontSize="small" />
            </IconButton>
          </Box>
          
          {/* 聊天消息区域（用Box替代ScrollArea） */}
          <Box sx={{ flexGrow: 1, p: 2, overflow: 'auto' }}>
            <List disablePadding>
              {chatMessages.length === 0 ? (
                <ListItem>
                  <ListItemText primary="请输入您的问题，我会为您提供帮助" />
                </ListItem>
              ) : (
                chatMessages.map((msg) => (
                  <React.Fragment key={msg.id}>
                    <ListItem 
                      sx={{ 
                        justifyContent: msg.sender === 'user' ? 'flex-end' : 'flex-start',
                        py: 1
                      }}
                    >
                      <Box 
                        sx={{ 
                          maxWidth: '70%', 
                          p: 1.5, 
                          borderRadius: 2,
                          backgroundColor: msg.sender === 'user' ? 'primary.main' : 'background.paper',
                          color: msg.sender === 'user' ? 'white' : 'text.primary',
                          boxShadow: 1
                        }}
                      >
                        <Typography variant="body1">
                          {msg.content}
                        </Typography>
                      </Box>
                    </ListItem>
                    <Divider variant="inset" component="li" />
                  </React.Fragment>
                ))
              )}
              <div ref={messagesEndRef} />
            </List>
          </Box>
          
          {/* 输入区域 */}
          <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider', display: 'flex' }}>
            <TextField
              fullWidth
              variant="outlined"
              placeholder="输入消息..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={loading}
              multiline
              rows={2}
              sx={{ mr: 1 }}
            />
            <Button 
              variant="contained" 
              color="primary" 
              onClick={handleSendMessage}
              disabled={!message.trim() || loading}
              sx={{ alignSelf: 'flex-end' }}
            >
              <Send fontSize="small" />
            </Button>
          </Box>
        </Paper>
      ) : (
        <Paper elevation={3} sx={{ borderRadius: '50%', p: 2, cursor: 'pointer' }}>
          <IconButton onClick={() => setIsOpen(true)}>  {/* 添加点击事件 */}
            <Message fontSize="large" color="primary" />
          </IconButton>
        </Paper>
      )}
    </Box>
  );
};

export default Chatbot;