import React from 'react';
import { Brain, LineChart, Users, AlertTriangle, DollarSign } from 'lucide-react';
import GlassmorphicCard from '../common/GlassmorphicCard';
import GradientText from '../common/GradientText';
import { Feature } from '../../types';

const Features: React.FC = () => {
  const features: Feature[] = [
    {
      icon: 'Brain',
      title: 'Idea Agent',
      description: 'Analyze your startup concept and refine it based on market trends and opportunities.',
      color: 'blue',
    },
    {
      icon: 'LineChart',
      title: 'Market Analysis',
      description: 'Get deep insights into market size, growth potential, and entry barriers.',
      color: 'green',
    },
    {
      icon: 'Users',
      title: 'Competitor Intelligence',
      description: 'Identify key competitors, their strengths, weaknesses, and market positioning.',
      color: 'red',
    },
    {
      icon: 'AlertTriangle',
      title: 'Risk Assessment',
      description: 'Uncover potential pitfalls and challenges that could impact your startup success.',
      color: 'yellow',
    },
    {
      icon: 'DollarSign',
      title: 'VC Matching',
      description: 'Find investors who are most likely to be interested in your specific startup.',
      color: 'purple',
    },
  ];

  const getIcon = (iconName: string, color: string) => {
    const iconProps = {
      className: `h-8 w-8 text-${color}-400`,
    };

    switch (iconName) {
      case 'Brain':
        return <Brain {...iconProps} />;
      case 'LineChart':
        return <LineChart {...iconProps} />;
      case 'Users':
        return <Users {...iconProps} />;
      case 'AlertTriangle':
        return <AlertTriangle {...iconProps} />;
      case 'DollarSign':
        return <DollarSign {...iconProps} />;
      default:
        return <Brain {...iconProps} />;
    }
  };

  return (
    <section id="features" className="py-20 bg-gray-900 relative">
      <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>
      
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            <GradientText>Supercharged</GradientText> Validation Toolkit
          </h2>
          <p className="text-gray-300 text-xl max-w-2xl mx-auto">
            Our AI agents work in parallel to validate every aspect of your startup idea
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <GlassmorphicCard 
              key={index} 
              className="p-6 transition-transform hover:scale-105"
              glowColor={`rgba(${feature.color === 'blue' ? '59, 130, 246' : 
                            feature.color === 'green' ? '16, 185, 129' : 
                            feature.color === 'red' ? '239, 68, 68' : 
                            feature.color === 'yellow' ? '245, 158, 11' : 
                            '139, 92, 246'}, 0.3)`}
              hoverable
            >
              <div className={`w-14 h-14 rounded-lg bg-${feature.color}-500 bg-opacity-20 flex items-center justify-center mb-4`}>
                {getIcon(feature.icon, feature.color)}
              </div>
              <h3 className={`text-xl font-bold mb-3 text-${feature.color}-400`}>{feature.title}</h3>
              <p className="text-gray-300">{feature.description}</p>
            </GlassmorphicCard>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Features;