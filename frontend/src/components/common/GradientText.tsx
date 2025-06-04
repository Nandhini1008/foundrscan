import React from 'react';

interface GradientTextProps {
  children: React.ReactNode;
  className?: string;
  from?: string;
  to?: string;
}

const GradientText: React.FC<GradientTextProps> = ({
  children,
  className = '',
  from = 'from-purple-400',
  to = 'to-pink-500'
}) => {
  return (
    <span className={`bg-clip-text text-transparent bg-gradient-to-r ${from} ${to} ${className}`}>
      {children}
    </span>
  );
};

export default GradientText;