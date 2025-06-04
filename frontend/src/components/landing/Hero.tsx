import React, { useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Brain } from 'lucide-react';
import GlassmorphicCard from '../common/GlassmorphicCard';
import GradientText from '../common/GradientText';
import Button from '../common/Button';

const Hero: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    
    // Create particle system
    const particles: Array<{
      x: number;
      y: number;
      radius: number;
      color: string;
      speedX: number;
      speedY: number;
    }> = [];
    
    const colors = ['#9333ea', '#3b82f6', '#06b6d4', '#14b8a6'];
    
    for (let i = 0; i < 50; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        radius: Math.random() * 2 + 0.5,
        color: colors[Math.floor(Math.random() * colors.length)],
        speedX: (Math.random() - 0.5) * 0.3,
        speedY: (Math.random() - 0.5) * 0.3,
      });
    }
    
    // Draw grid
    const drawGrid = () => {
      ctx.strokeStyle = 'rgba(30, 41, 59, 0.3)';
      ctx.lineWidth = 0.5;
      
      const gridSize = 40;
      
      for (let x = 0; x < canvas.width; x += gridSize) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, canvas.height);
        ctx.stroke();
      }
      
      for (let y = 0; y < canvas.height; y += gridSize) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(canvas.width, y);
        ctx.stroke();
      }
    };
    
    // Animation loop
    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      // Draw grid
      drawGrid();
      
      // Update and draw particles
      for (const particle of particles) {
        particle.x += particle.speedX;
        particle.y += particle.speedY;
        
        // Wrap around edges
        if (particle.x < 0) particle.x = canvas.width;
        if (particle.x > canvas.width) particle.x = 0;
        if (particle.y < 0) particle.y = canvas.height;
        if (particle.y > canvas.height) particle.y = 0;
        
        ctx.beginPath();
        ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2);
        ctx.fillStyle = particle.color;
        ctx.fill();
      }
      
      requestAnimationFrame(animate);
    };
    
    animate();
    
    const handleResize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    
    window.addEventListener('resize', handleResize);
    
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  return (
    <div className="relative min-h-screen flex items-center justify-center overflow-hidden pt-16">
      <canvas
        ref={canvasRef}
        className="absolute inset-0 z-0"
      />
      
      <div className="relative z-10 container mx-auto px-4 py-16 md:py-24 flex flex-col lg:flex-row items-center justify-between">
        <div className="lg:w-1/2 lg:pr-12 mb-12 lg:mb-0 text-center lg:text-left">
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold leading-tight mb-6">
            Validate Your Startup Idea With <GradientText>AI-Powered</GradientText> Intelligence
          </h1>
          <p className="text-gray-300 text-xl mb-8 max-w-2xl mx-auto lg:mx-0">
            Get comprehensive market analysis, competitor insights, and risk assessment for your startup idea in minutes, not months.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center lg:justify-start space-y-4 sm:space-y-0 sm:space-x-4">
            <Link to="/signup">
              <Button variant="primary" size="lg" className="group">
                Start Validating My Idea
                <ArrowRight className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" />
              </Button>
            </Link>
            <Link to="/login">
              <Button variant="outline" size="lg">
                Log In
              </Button>
            </Link>
          </div>
        </div>
        
        <div className="lg:w-1/2 flex justify-center">
          <GlassmorphicCard className="w-full max-w-md p-6 md:p-8">
            <div className="flex justify-center mb-6">
              <div className="relative">
                <div className="absolute inset-0 rounded-full bg-purple-500 blur-2xl opacity-20 animate-pulse"></div>
                <div className="relative bg-gradient-to-br from-purple-500 to-blue-600 p-4 rounded-full">
                  <Brain className="h-12 w-12 text-white" />
                </div>
              </div>
            </div>
            <div className="space-y-4">
              <div className="h-2 bg-gradient-to-r from-blue-400 to-blue-600 rounded animate-pulse"></div>
              <div className="h-2 bg-gradient-to-r from-purple-400 to-purple-600 rounded animate-pulse delay-100"></div>
              <div className="h-2 bg-gradient-to-r from-green-400 to-green-600 rounded animate-pulse delay-200"></div>
              <div className="h-2 bg-gradient-to-r from-yellow-400 to-yellow-600 rounded animate-pulse delay-300"></div>
              <div className="h-2 bg-gradient-to-r from-red-400 to-red-600 rounded animate-pulse delay-400"></div>
            </div>
            <div className="mt-8 space-y-3">
              <div className="flex items-center">
                <div className="w-8 h-8 bg-blue-500 bg-opacity-20 rounded-full flex items-center justify-center mr-3">
                  <div className="w-4 h-4 bg-blue-500 rounded-full"></div>
                </div>
                <div className="flex-1">
                  <div className="h-2 bg-gray-700 rounded w-3/4"></div>
                </div>
              </div>
              <div className="flex items-center">
                <div className="w-8 h-8 bg-green-500 bg-opacity-20 rounded-full flex items-center justify-center mr-3">
                  <div className="w-4 h-4 bg-green-500 rounded-full"></div>
                </div>
                <div className="flex-1">
                  <div className="h-2 bg-gray-700 rounded w-5/6"></div>
                </div>
              </div>
              <div className="flex items-center">
                <div className="w-8 h-8 bg-red-500 bg-opacity-20 rounded-full flex items-center justify-center mr-3">
                  <div className="w-4 h-4 bg-red-500 rounded-full"></div>
                </div>
                <div className="flex-1">
                  <div className="h-2 bg-gray-700 rounded w-2/3"></div>
                </div>
              </div>
            </div>
          </GlassmorphicCard>
        </div>
      </div>
    </div>
  );
};

export default Hero;