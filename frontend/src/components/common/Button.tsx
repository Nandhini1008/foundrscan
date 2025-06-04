import React from 'react';

interface ButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  onClick?: () => void;
  disabled?: boolean;
  type?: 'button' | 'submit' | 'reset';
  fullWidth?: boolean;
}

const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  className = '',
  onClick,
  disabled = false,
  type = 'button',
  fullWidth = false,
}) => {
  const baseClasses = 'relative rounded-md font-medium transition-all focus:outline-none inline-flex items-center justify-center';
  
  const variantClasses = {
    primary: 'bg-gradient-to-r from-purple-600 to-pink-500 text-white shadow-lg shadow-purple-500/20 hover:shadow-purple-500/40 hover:scale-105',
    secondary: 'bg-blue-500 bg-opacity-20 text-blue-400 border border-blue-500/30 hover:bg-blue-500/30 hover:border-blue-500/50',
    outline: 'bg-transparent border border-gray-700 text-gray-300 hover:bg-gray-800 hover:text-white',
    ghost: 'bg-transparent text-gray-300 hover:bg-gray-800 hover:text-white',
  };
  
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-xs',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base',
  };
  
  const disabledClasses = disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer';
  const widthClass = fullWidth ? 'w-full' : '';
  
  return (
    <button
      type={type}
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${disabledClasses} ${widthClass} ${className}`}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
      <div className={`absolute inset-0 rounded-md ${variant === 'primary' ? 'bg-gradient-to-r from-purple-600/10 to-pink-500/10' : ''} opacity-0 hover:opacity-100 transition-opacity`}></div>
    </button>
  );
};

export default Button;