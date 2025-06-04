import React from 'react';
import Navbar from '../components/common/Navbar';
import ChatInterface from '../components/chat/ChatInterface';

const ChatPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <Navbar />
      <ChatInterface />
    </div>
  );
};

export default ChatPage;