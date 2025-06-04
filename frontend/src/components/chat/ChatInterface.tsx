import React, { useState, useRef, useEffect } from 'react';
import { Send, Mic, MicOff, Brain } from 'lucide-react';
import FloatingOrb from '../common/FloatingOrb';
import Button from '../common/Button';
import GlassmorphicCard from '../common/GlassmorphicCard';
import { Message } from '../../types';

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: "Hi there! I'm the Founder Scan AI. Tell me about your startup idea, and I'll help validate it across market trends, competition, and investor potential.",
      sender: 'ai',
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isThinking, setIsThinking] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Auto-scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  const handleSendMessage = () => {
    if (!inputValue.trim()) return;
    
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      sender: 'user',
      timestamp: new Date(),
    };
    
    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsThinking(true);
    
    // Simulate AI thinking and responding
    setTimeout(() => {
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: '',
        sender: 'ai',
        timestamp: new Date(),
        isTyping: true,
      };
      
      setMessages((prev) => [...prev, aiMessage]);
      
      // Simulate typing effect
      let responseText = '';
      const responses = [
        "That's an interesting startup idea! Let me analyze it for you.",
        "Based on market research, I can see a growing trend in this space. The total addressable market is expanding at 23% year over year.",
        "I've identified 3 main competitors: CompanyX (Series B funded), CompanyY (bootstrapped), and CompanyZ (recently acquired). Your key differentiation could be in the area of user experience and pricing model.",
        "The primary risk factors I'm seeing relate to regulatory changes expected in Q3 and customer acquisition costs in this sector.",
        "Several VCs have recently invested in similar startups, including Sequoia, a16z, and Y Combinator. Would you like me to suggest some investors who might be interested in your specific focus area?"
      ];
      
      const selectedResponse = responses[Math.floor(Math.random() * responses.length)];
      const typingInterval = setInterval(() => {
        if (responseText.length < selectedResponse.length) {
          responseText += selectedResponse.charAt(responseText.length);
          setMessages((prev) => 
            prev.map((msg) => 
              msg.id === aiMessage.id ? { ...msg, content: responseText } : msg
            )
          );
        } else {
          clearInterval(typingInterval);
          setMessages((prev) => 
            prev.map((msg) => 
              msg.id === aiMessage.id ? { ...msg, isTyping: false } : msg
            )
          );
          setIsThinking(false);
        }
      }, 20);
    }, 1500);
  };
  
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };
  
  const toggleRecording = () => {
    setIsRecording(!isRecording);
    
    // Simulate voice recognition
    if (!isRecording) {
      setTimeout(() => {
        setInputValue('I have an idea for a B2B SaaS platform that helps e-commerce companies optimize their shipping logistics.');
        setIsRecording(false);
      }, 3000);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-950 pt-16">
      {/* Background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-0 right-0 h-64 bg-gradient-to-b from-purple-900/20 to-transparent"></div>
        <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>
      </div>
      
      <div className="flex-1 overflow-hidden flex flex-col relative">
        <div className="px-4 py-3 border-b border-gray-800 bg-gray-900/40 backdrop-blur-sm">
          <div className="flex items-center justify-center">
            <FloatingOrb size="sm" />
            <h1 className="text-xl font-semibold text-white ml-2">🧠 Idea Agent – Let's Understand Your Startup</h1>
          </div>
        </div>
        
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message) => (
            <div 
              key={message.id} 
              className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {message.sender === 'ai' && (
                <div className="mr-3 flex items-end">
                  <FloatingOrb size="sm\" isThinking={isThinking && messages[messages.length - 1].id === message.id} />
                </div>
              )}
              <GlassmorphicCard 
                className={`max-w-[75%] p-4 ${
                  message.sender === 'user' 
                    ? 'bg-purple-500/20 border-purple-500/30' 
                    : 'bg-gray-800/40 border-gray-700/50'
                }`}
              >
                <p className="text-gray-200">{message.content}</p>
                {message.isTyping && (
                  <div className="flex space-x-1 mt-2">
                    <div className="w-2 h-2 rounded-full bg-gray-400 animate-pulse"></div>
                    <div className="w-2 h-2 rounded-full bg-gray-400 animate-pulse delay-75"></div>
                    <div className="w-2 h-2 rounded-full bg-gray-400 animate-pulse delay-150"></div>
                  </div>
                )}
              </GlassmorphicCard>
              {message.sender === 'user' && (
                <div className="ml-3 flex items-end">
                  <div className="w-8 h-8 rounded-full bg-purple-500 flex items-center justify-center">
                    <User className="w-5 h-5 text-white" />
                  </div>
                </div>
              )}
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
        
        <div className="p-4">
          <GlassmorphicCard className="flex items-center p-2">
            <button 
              className={`p-2 rounded-full mr-2 transition-colors ${
                isRecording 
                  ? 'bg-red-500 text-white animate-pulse' 
                  : 'bg-gray-800 text-gray-400 hover:text-white hover:bg-gray-700'
              }`}
              onClick={toggleRecording}
            >
              {isRecording ? <MicOff className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
            </button>
            <textarea
              className="flex-1 bg-transparent border-none text-white placeholder-gray-500 resize-none max-h-32 focus:outline-none"
              placeholder={isRecording ? "Listening..." : "Type your message..."}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={1}
              disabled={isRecording}
            />
            <Button 
              variant="primary" 
              size="sm" 
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || isThinking}
              className="ml-2"
            >
              <Send className="h-4 w-4" />
            </Button>
          </GlassmorphicCard>
          
          {isRecording && (
            <div className="mt-4 flex justify-center">
              <div className="relative">
                <div className="absolute inset-0 bg-red-500 rounded-full animate-ping opacity-25"></div>
                <div className="relative flex items-center justify-center rounded-full h-16 w-16 bg-gradient-to-r from-red-500 to-purple-500">
                  <div className="wave-container">
                    {[...Array(5)].map((_, i) => (
                      <div key={i} className={`wave wave-${i}`}></div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
      
      <style jsx>{`
        .bg-grid-pattern {
          background-image: 
            linear-gradient(rgba(30, 41, 59, 0.3) 1px, transparent 1px),
            linear-gradient(90deg, rgba(30, 41, 59, 0.3) 1px, transparent 1px);
          background-size: 40px 40px;
        }
        
        .wave-container {
          position: relative;
          width: 100%;
          height: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        
        .wave {
          position: absolute;
          width: 100%;
          height: 100%;
          border: 2px solid white;
          border-radius: 50%;
          opacity: 0;
          animation: wave 2s infinite;
        }
        
        .wave-1 { animation-delay: 0.2s; }
        .wave-2 { animation-delay: 0.4s; }
        .wave-3 { animation-delay: 0.6s; }
        .wave-4 { animation-delay: 0.8s; }
        
        @keyframes wave {
          0% {
            transform: scale(0.5);
            opacity: 0.8;
          }
          100% {
            transform: scale(1.5);
            opacity: 0;
          }
        }
      `}</style>
    </div>
  );
};

// User Avatar Component
const User: React.FC<{ className?: string }> = ({ className = '' }) => {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M12 12C14.2091 12 16 10.2091 16 8C16 5.79086 14.2091 4 12 4C9.79086 4 8 5.79086 8 8C8 10.2091 9.79086 12 12 12Z"
        fill="currentColor"
      />
      <path
        d="M12 14C8.13401 14 5 17.134 5 21H19C19 17.134 15.866 14 12 14Z"
        fill="currentColor"
      />
    </svg>
  );
};

export default ChatInterface;