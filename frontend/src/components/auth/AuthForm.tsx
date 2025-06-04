import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, User, Eye, EyeOff } from 'lucide-react';
import Input from '../common/Input';
import Button from '../common/Button';
import GlassmorphicCard from '../common/GlassmorphicCard';
import GradientText from '../common/GradientText';

interface AuthFormProps {
  type: 'login' | 'signup';
}

const AuthForm: React.FC<AuthFormProps> = ({ type }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // In a real app, you would handle authentication here
    // For demo purposes, we'll just navigate to the chat page
    navigate('/chat');
  };
  
  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 relative">
      <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>
      
      {/* Animated background elements */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-10 animate-blob"></div>
        <div className="absolute top-3/4 right-1/4 w-72 h-72 bg-blue-500 rounded-full mix-blend-multiply filter blur-3xl opacity-10 animate-blob animation-delay-2000"></div>
      </div>
      
      <GlassmorphicCard className="w-full max-w-md p-8">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold">
            {type === 'login' ? (
              <>Welcome <GradientText>Back</GradientText></>
            ) : (
              <>Join <GradientText>Founder Scan</GradientText></>
            )}
          </h2>
          <p className="text-gray-400 mt-2">
            {type === 'login' 
              ? 'Log in to continue validating your startup idea' 
              : 'Create an account to start validating your startup idea'}
          </p>
        </div>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          {type === 'signup' && (
            <Input
              label="Full Name"
              type="text"
              placeholder="Enter your name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              icon={<User className="h-5 w-5 text-gray-500" />}
            />
          )}
          
          <Input
            label="Email Address"
            type="email"
            placeholder="Enter your email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            icon={<Mail className="h-5 w-5 text-gray-500" />}
          />
          
          <div className="relative">
            <Input
              label="Password"
              type={showPassword ? 'text' : 'password'}
              placeholder={type === 'login' ? 'Enter your password' : 'Create a password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              icon={<Lock className="h-5 w-5 text-gray-500" />}
            />
            <button
              type="button"
              className="absolute right-3 top-[38px] text-gray-500 hover:text-white transition-colors"
              onClick={() => setShowPassword(!showPassword)}
            >
              {showPassword ? (
                <EyeOff className="h-5 w-5" />
              ) : (
                <Eye className="h-5 w-5" />
              )}
            </button>
          </div>
          
          {type === 'login' && (
            <div className="flex justify-end">
              <a href="#" className="text-sm text-purple-400 hover:text-purple-300 transition-colors">
                Forgot password?
              </a>
            </div>
          )}
          
          <Button type="submit" variant="primary" fullWidth>
            {type === 'login' ? 'Log In' : 'Create Account'}
          </Button>
        </form>
        
        <div className="mt-6">
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-700"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-gray-900 text-gray-400">Or continue with</span>
            </div>
          </div>
          
          <div className="mt-6 grid grid-cols-1 gap-3">
            <button className="group relative flex justify-center py-2 px-4 border border-gray-700 rounded-md bg-gray-800/50 hover:bg-gray-800 transition-colors">
              <span className="text-gray-300 text-sm">Google</span>
            </button>
          </div>
        </div>
        
        <div className="mt-6 text-center text-sm">
          <p className="text-gray-400">
            {type === 'login' ? "Don't have an account? " : "Already have an account? "}
            <Link
              to={type === 'login' ? '/signup' : '/login'}
              className="text-purple-400 hover:text-purple-300 font-medium transition-colors"
            >
              {type === 'login' ? 'Sign up' : 'Log in'}
            </Link>
          </p>
        </div>
      </GlassmorphicCard>
      
      <style jsx>{`
        @keyframes blob {
          0% {
            transform: translate(0px, 0px) scale(1);
          }
          33% {
            transform: translate(30px, -50px) scale(1.1);
          }
          66% {
            transform: translate(-20px, 20px) scale(0.9);
          }
          100% {
            transform: translate(0px, 0px) scale(1);
          }
        }
        .animate-blob {
          animation: blob 7s infinite;
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        .bg-grid-pattern {
          background-image: 
            linear-gradient(rgba(30, 41, 59, 0.3) 1px, transparent 1px),
            linear-gradient(90deg, rgba(30, 41, 59, 0.3) 1px, transparent 1px);
          background-size: 40px 40px;
        }
      `}</style>
    </div>
  );
};

export default AuthForm;