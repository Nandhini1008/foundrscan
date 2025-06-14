import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { storeUserOutput, getUserOutput } from '../utils/firestore';
import Navbar from '../components/common/Navbar';
import Button from '../components/common/Button';
import Input from '../components/common/Input';

interface ChatMessage {
  id: string;
  content: string;
  sender: 'user' | 'ai';
  timestamp: Date;
}

const welcomeMessage: ChatMessage = {
  id: '1',
  content: "Hi there! I'm the Founder Scan AI. Tell me about your startup idea, and I'll help validate it across market trends, competition, and investor potential.",
  sender: 'ai',
  timestamp: new Date(),
};

const ChatPage: React.FC = () => {
  const { user } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([welcomeMessage]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);

  // Load previous chat history when component mounts
  useEffect(() => {
    const loadChatHistory = async () => {
      if (user) {
        console.log('Loading chat history for user:', user.uid);
        try {
          const data = await getUserOutput(user);
          console.log('Loaded chat history:', data);
          if (data?.output?.messages) {
            setMessages(data.output.messages as ChatMessage[]);
          }
        } catch (error) {
          console.error('Error loading chat history:', error);
        }
      }
    };

    loadChatHistory();
  }, [user]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !user) return;

    setLoading(true);
    try {
      // Add user message
      const userMessage: ChatMessage = {
        id: Date.now().toString(),
        content: input,
        sender: 'user',
        timestamp: new Date(),
      };
      const newMessages = [...messages, userMessage];
      setMessages(newMessages);
      setInput('');

      // Call the real API
      const res = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({
          message: input,
          session_id: sessionId,
        }),
      });

      if (!res.ok) {
        throw new Error(`API Error: ${res.status}`);
      }

      const data = await res.json();
      if (data.session_id && !sessionId) {
        setSessionId(data.session_id);
      }

      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: data.response || '⚠️ No response received from API.',
        sender: 'ai',
        timestamp: new Date(),
      };
      const updatedMessages = [...newMessages, aiMessage];
      setMessages(updatedMessages);
      await storeUserOutput(user, {
        messages: updatedMessages,
        lastUpdated: new Date()
      });
    } catch (error) {
      console.error('Error in chat:', error);
      const errorMessage: ChatMessage = {
        id: (Date.now() + 2).toString(),
        content: `⚠️ API Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        sender: 'ai',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900">
      <Navbar />
      
      <div className="max-w-4xl mx-auto pt-20 px-4">
        <div className="bg-gray-800 rounded-lg shadow-xl p-6 mb-4">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-4">
            <div className="text-lg font-semibold text-white">Chat</div>
            <button
              className="bg-purple-600 hover:bg-purple-700 text-white font-semibold px-4 py-2 rounded shadow transition-colors border border-white"
              onClick={() => {
                setMessages([{
                  id: '1',
                  content: "Hi there! I'm the Founder Scan AI. Tell me about your startup idea, and I'll help validate it across market trends, competition, and investor potential.",
                  sender: 'ai',
                  timestamp: new Date(),
                }]);
                setSessionId(null);
                localStorage.removeItem('chatSessionId');
              }}
              title="Start a new chat session"
            >
              New Chat
            </button>
          </div>
          <div className="space-y-4 h-[60vh] overflow-y-auto mb-4">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${
                  message.sender === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                <div
                  className={`max-w-[80%] rounded-lg p-4 ${
                    message.sender === 'user'
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-700 text-gray-200'
                  }`}
                >
                  {message.content}
                </div>
              </div>
            ))}
          </div>

          <form onSubmit={handleSubmit} className="flex gap-2">
            <Input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
              className="flex-1"
            />
            <Button
              type="submit"
              variant="primary"
              disabled={loading || !input.trim()}
            >
              {loading ? 'Sending...' : 'Send'}
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;