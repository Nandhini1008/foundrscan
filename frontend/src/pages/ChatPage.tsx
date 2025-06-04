import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { storeUserOutput, getUserOutput } from '../utils/firestore';
import Navbar from '../components/common/Navbar';
import Button from '../components/common/Button';
import Input from '../components/common/Input';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

const ChatPage: React.FC = () => {
  const { user } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  // Load previous chat history when component mounts
  useEffect(() => {
    const loadChatHistory = async () => {
      if (user) {
        console.log('Loading chat history for user:', user.uid);
        try {
          const data = await getUserOutput(user);
          console.log('Loaded chat history:', data);
          if (data?.output?.messages) {
            setMessages(data.output.messages);
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

    console.log('Sending message:', input);
    setLoading(true);
    try {
      // Add user message
      const newMessages = [...messages, { role: 'user', content: input }];
      setMessages(newMessages);
      setInput('');

      // TODO: Add your AI processing logic here
      // For now, we'll just simulate a response
      const aiResponse = "This is a simulated AI response.";
      console.log('AI response:', aiResponse);
      
      // Add AI response
      const updatedMessages = [...newMessages, { role: 'assistant', content: aiResponse }];
      setMessages(updatedMessages);

      // Save to Firestore
      console.log('Saving to Firestore...');
      await storeUserOutput(user, {
        messages: updatedMessages,
        lastUpdated: new Date()
      });
      console.log('Successfully saved to Firestore');
    } catch (error) {
      console.error('Error in chat:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900">
      <Navbar />
      
      <div className="max-w-4xl mx-auto pt-20 px-4">
        <div className="bg-gray-800 rounded-lg shadow-xl p-6 mb-4">
          <div className="space-y-4 h-[60vh] overflow-y-auto mb-4">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                <div
                  className={`max-w-[80%] rounded-lg p-4 ${
                    message.role === 'user'
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