import React from 'react';
import { Brain, LineChart, Users, AlertTriangle, DollarSign } from 'lucide-react';
import GlassmorphicCard from '../common/GlassmorphicCard';
import { AgentCard as AgentCardType } from '../../types';

interface AgentCardProps {
  agent: AgentCardType;
}

const AgentCard: React.FC<AgentCardProps> = ({ agent }) => {
  const getIcon = () => {
    switch (agent.icon) {
      case 'Brain':
        return <Brain className={`h-6 w-6 text-${agent.color}-400`} />;
      case 'LineChart':
        return <LineChart className={`h-6 w-6 text-${agent.color}-400`} />;
      case 'Users':
        return <Users className={`h-6 w-6 text-${agent.color}-400`} />;
      case 'AlertTriangle':
        return <AlertTriangle className={`h-6 w-6 text-${agent.color}-400`} />;
      case 'DollarSign':
        return <DollarSign className={`h-6 w-6 text-${agent.color}-400`} />;
      default:
        return <Brain className={`h-6 w-6 text-${agent.color}-400`} />;
    }
  };

  return (
    <GlassmorphicCard 
      className="p-6 h-full flex flex-col"
      glowColor={`rgba(${agent.color === 'blue' ? '59, 130, 246' : 
                 agent.color === 'green' ? '16, 185, 129' : 
                 agent.color === 'red' ? '239, 68, 68' : 
                 agent.color === 'yellow' ? '245, 158, 11' : 
                 '139, 92, 246'}, 0.3)`}
      hoverable
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center">
          <div className={`w-10 h-10 rounded-lg bg-${agent.color}-500 bg-opacity-20 flex items-center justify-center mr-3`}>
            {getIcon()}
          </div>
          <h3 className={`text-lg font-bold text-${agent.color}-400`}>{agent.title}</h3>
        </div>
        
        <div className={`px-2 py-1 rounded-full text-xs font-medium ${
          agent.status === 'active' 
            ? 'bg-green-500/20 text-green-400' 
            : agent.status === 'processing'
            ? 'bg-blue-500/20 text-blue-400 animate-pulse'
            : 'bg-gray-500/20 text-gray-400'
        }`}>
          {agent.status === 'active' ? 'Active' : agent.status === 'processing' ? 'Processing' : 'Idle'}
        </div>
      </div>
      
      <p className="text-gray-300 text-sm mb-4">{agent.description}</p>
      
      <div className="mb-4 mt-auto">
        <div className="flex justify-between text-xs text-gray-400 mb-1">
          <span>Progress</span>
          <span>{agent.progress}%</span>
        </div>
        <div className="w-full h-2 bg-gray-800 rounded-full overflow-hidden">
          <div 
            className={`h-full bg-${agent.color}-500 rounded-full`}
            style={{ width: `${agent.progress}%` }}
          ></div>
        </div>
      </div>
      
      {agent.insights && agent.insights.length > 0 && (
        <div className="mt-4">
          <h4 className="text-sm font-medium text-white mb-2">Key Insights:</h4>
          <ul className="space-y-2">
            {agent.insights.map((insight, index) => (
              <li key={index} className="flex items-start">
                <div className={`w-2 h-2 rounded-full bg-${agent.color}-400 mt-1.5 mr-2`}></div>
                <span className="text-xs text-gray-300">{insight}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </GlassmorphicCard>
  );
};

export default AgentCard;