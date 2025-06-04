import React, { useEffect, useRef } from 'react';
import { Brain, LineChart, Users, AlertTriangle, DollarSign } from 'lucide-react';
import AgentCard from './AgentCard';
import GradientText from '../common/GradientText';
import { AgentCard as AgentCardType } from '../../types';

const Dashboard: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  
  const agents: AgentCardType[] = [
    {
      id: '1',
      title: 'Idea Agent',
      icon: 'Brain',
      description: 'Analyzing your startup concept and refining it based on market trends and opportunities.',
      status: 'active',
      color: 'blue',
      progress: 100,
      insights: [
        'Concept has strong technical innovation potential',
        'Value proposition is clear and compelling',
        'Similar ideas have attracted recent funding'
      ]
    },
    {
      id: '2',
      title: 'Market Analysis',
      icon: 'LineChart',
      description: 'Evaluating market size, growth potential, and entry barriers.',
      status: 'active',
      color: 'green',
      progress: 85,
      insights: [
        'Total addressable market: $3.2B with 23% YoY growth',
        'Low regulatory barriers in target markets',
        'Emerging demand in enterprise segment'
      ]
    },
    {
      id: '3',
      title: 'Competitor Intelligence',
      icon: 'Users',
      description: 'Identifying key competitors, their strengths, weaknesses, and market positioning.',
      status: 'processing',
      color: 'red',
      progress: 60,
      insights: [
        'Three direct competitors identified',
        'Main differentiator: user experience and pricing model',
        'Competitor X recently raised $12M Series A'
      ]
    },
    {
      id: '4',
      title: 'Risk Assessment',
      icon: 'AlertTriangle',
      description: 'Uncovering potential pitfalls and challenges that could impact your startup success.',
      status: 'processing',
      color: 'yellow',
      progress: 40,
      insights: [
        'Regulatory changes expected in Q3',
        'Customer acquisition costs higher than industry average',
        'Technical implementation complexity: moderate'
      ]
    },
    {
      id: '5',
      title: 'VC Matching',
      icon: 'DollarSign',
      description: 'Finding investors who are most likely to be interested in your specific startup.',
      status: 'idle',
      color: 'purple',
      progress: 10
    }
  ];
  
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    
    // Create connection lines between agents
    const drawConnections = () => {
      const agentElements = document.querySelectorAll('.agent-card');
      if (agentElements.length < 2) return;
      
      const agentPositions: Array<{ x: number; y: number; color: string }> = [];
      
      agentElements.forEach((el, index) => {
        const rect = el.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;
        
        agentPositions.push({
          x: centerX,
          y: centerY,
          color: agents[index].color
        });
      });
      
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      // Draw lines between agents
      for (let i = 0; i < agentPositions.length - 1; i++) {
        const start = agentPositions[i];
        const end = agentPositions[i + 1];
        
        const gradient = ctx.createLinearGradient(start.x, start.y, end.x, end.y);
        
        gradient.addColorStop(0, getColorRGBA(start.color, 0.5));
        gradient.addColorStop(1, getColorRGBA(end.color, 0.5));
        
        ctx.beginPath();
        ctx.moveTo(start.x, start.y);
        ctx.lineTo(end.x, end.y);
        ctx.strokeStyle = gradient;
        ctx.lineWidth = 2;
        ctx.stroke();
        
        // Add data particles moving along the lines
        const particleCount = Math.floor(Math.random() * 2) + 1; // 1-2 particles per line
        
        for (let j = 0; j < particleCount; j++) {
          const progress = (Date.now() / 1000) % 1; // 0-1 based on time
          
          const particleX = start.x + (end.x - start.x) * progress;
          const particleY = start.y + (end.y - start.y) * progress;
          
          ctx.beginPath();
          ctx.arc(particleX, particleY, 3, 0, Math.PI * 2);
          ctx.fillStyle = getColorRGBA(end.color, 0.8);
          ctx.fill();
        }
      }
    };
    
    const getColorRGBA = (color: string, alpha: number) => {
      switch (color) {
        case 'blue':
          return `rgba(59, 130, 246, ${alpha})`;
        case 'green':
          return `rgba(16, 185, 129, ${alpha})`;
        case 'red':
          return `rgba(239, 68, 68, ${alpha})`;
        case 'yellow':
          return `rgba(245, 158, 11, ${alpha})`;
        case 'purple':
          return `rgba(139, 92, 246, ${alpha})`;
        default:
          return `rgba(255, 255, 255, ${alpha})`;
      }
    };
    
    const animate = () => {
      drawConnections();
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
  }, [agents]);

  return (
    <div className="min-h-screen bg-gray-950 pt-16">
      <canvas
        ref={canvasRef}
        className="fixed inset-0 z-0 pointer-events-none"
      />
      
      <div className="container mx-auto px-4 py-8 relative z-10">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">
            Startup Validation <GradientText>Dashboard</GradientText>
          </h1>
          <p className="text-gray-400">
            Real-time analysis and insights for your startup idea
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {agents.map((agent) => (
            <div key={agent.id} className="agent-card">
              <AgentCard agent={agent} />
            </div>
          ))}
        </div>
        
        <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="lg:col-span-2">
            <div className="bg-gray-900/40 backdrop-blur-lg border border-gray-800 rounded-xl p-6 shadow-xl">
              <h2 className="text-xl font-bold mb-4">Executive Summary</h2>
              <div className="space-y-4">
                <p className="text-gray-300">
                  Your startup idea shows strong promise with a clear value proposition and growing market. 
                  The total addressable market is substantial at $3.2B with 23% YoY growth, offering significant room for expansion.
                </p>
                <p className="text-gray-300">
                  While competition exists, your unique approach to user experience and pricing provides a meaningful differentiation.
                  Be mindful of upcoming regulatory changes and higher than average customer acquisition costs.
                </p>
                <div className="mt-6 pt-6 border-t border-gray-700">
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="text-gray-400 text-sm">Overall Confidence Score</span>
                      <div className="text-2xl font-bold text-white">76<span className="text-gray-400 text-lg">/100</span></div>
                    </div>
                    <div className="w-24 h-24 relative">
                      <svg className="w-full h-full" viewBox="0 0 100 100">
                        <circle 
                          cx="50" 
                          cy="50" 
                          r="40" 
                          fill="none" 
                          stroke="#1f2937" 
                          strokeWidth="10" 
                        />
                        <circle 
                          cx="50" 
                          cy="50" 
                          r="40" 
                          fill="none" 
                          stroke="#8b5cf6" 
                          strokeWidth="10" 
                          strokeDasharray="251.2" 
                          strokeDashoffset={251.2 - (251.2 * 76 / 100)}
                          transform="rotate(-90 50 50)" 
                        />
                      </svg>
                      <div className="absolute inset-0 flex items-center justify-center">
                        <div className="text-sm font-bold text-white">76%</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;