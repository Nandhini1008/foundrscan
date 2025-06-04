import React from 'react';
import { CheckCircle2, XCircle } from 'lucide-react';
import GlassmorphicCard from '../common/GlassmorphicCard';
import GradientText from '../common/GradientText';

const ComparisonSection: React.FC = () => {
  const traditionalApproach = [
    'Months of manual market research',
    'Limited competitor insights',
    'Biased validation from friends',
    'High risk of building unwanted products',
    'No clear revenue model validation'
  ];

  const aiApproach = [
    'Instant market demand analysis',
    'Comprehensive competitor mapping',
    'Data-driven validation',
    'Risk assessment before building',
    'AI-suggested revenue models'
  ];

  return (
    <section className="py-20 relative overflow-hidden">
      <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>
      
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Why <GradientText>AI-Powered</GradientText> Validation?
          </h2>
          <p className="text-gray-300 text-xl max-w-2xl mx-auto">
            90% of startups fail. Not because they lacked effort, but because they worked on the wrong idea.
          </p>
        </div>
        
        <div className="grid md:grid-cols-2 gap-8 max-w-6xl mx-auto">
          <GlassmorphicCard 
            className="p-6 transform hover:scale-105 transition-transform duration-300"
            glowColor="rgba(239, 68, 68, 0.3)"
          >
            <div className="flex items-center mb-6">
              <div className="w-12 h-12 rounded-lg bg-red-500/20 flex items-center justify-center mr-4">
                <XCircle className="w-8 h-8 text-red-500" />
              </div>
              <h3 className="text-2xl font-bold text-red-400">Traditional Approach</h3>
            </div>
            <ul className="space-y-4">
              {traditionalApproach.map((item, index) => (
                <li key={index} className="flex items-center text-gray-300">
                  <XCircle className="w-5 h-5 text-red-500 mr-3 flex-shrink-0" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </GlassmorphicCard>
          
          <GlassmorphicCard 
            className="p-6 transform hover:scale-105 transition-transform duration-300"
            glowColor="rgba(16, 185, 129, 0.3)"
          >
            <div className="flex items-center mb-6">
              <div className="w-12 h-12 rounded-lg bg-green-500/20 flex items-center justify-center mr-4">
                <CheckCircle2 className="w-8 h-8 text-green-500" />
              </div>
              <h3 className="text-2xl font-bold text-green-400">AI-Powered Approach</h3>
            </div>
            <ul className="space-y-4">
              {aiApproach.map((item, index) => (
                <li key={index} className="flex items-center text-gray-300">
                  <CheckCircle2 className="w-5 h-5 text-green-500 mr-3 flex-shrink-0" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </GlassmorphicCard>
        </div>
        
        <div className="mt-12 text-center">
          <p className="text-gray-300 text-lg max-w-3xl mx-auto">
            Don't let your startup become another failure statistic. With AI-driven insights, 
            founders can avoid years of wasted effort and invest only in ideas that have a real shot at success.
          </p>
        </div>
      </div>
    </section>
  );
};

export default ComparisonSection;