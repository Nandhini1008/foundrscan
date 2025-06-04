import React, { useState, useEffect, useRef } from 'react';
import GlassmorphicCard from '../common/GlassmorphicCard';
import GradientText from '../common/GradientText';
import { Testimonial } from '../../types';

const Testimonials: React.FC = () => {
  const testimonials: Testimonial[] = [
    {
      id: 1,
      name: 'Sarah Johnson',
      role: 'Founder',
      company: 'TechNova',
      avatar: 'https://images.pexels.com/photos/774909/pexels-photo-774909.jpeg?auto=compress&cs=tinysrgb&w=150',
      content: 'Founder Scan saved us months of research and helped us pivot early. Our Series A investors were impressed by the depth of market analysis we had.'
    },
    {
      id: 2,
      name: 'Michael Chen',
      role: 'CEO',
      company: 'DataFlow',
      avatar: 'https://images.pexels.com/photos/614810/pexels-photo-614810.jpeg?auto=compress&cs=tinysrgb&w=150',
      content: 'The competitor intelligence we got from Founder Scan was eye-opening. We discovered gaps in the market that we leveraged to gain traction quickly.'
    },
    {
      id: 3,
      name: 'Elena Rodriguez',
      role: 'Co-founder',
      company: 'GreenSpark',
      avatar: 'https://images.pexels.com/photos/1239291/pexels-photo-1239291.jpeg?auto=compress&cs=tinysrgb&w=150',
      content: 'As a non-technical founder, I was amazed at how quickly Founder Scan helped me validate my SaaS idea and identify the right target market.'
    },
    {
      id: 4,
      name: 'David Kim',
      role: 'Founder',
      company: 'FinEdge',
      avatar: 'https://images.pexels.com/photos/220453/pexels-photo-220453.jpeg?auto=compress&cs=tinysrgb&w=150',
      content: 'The risk assessment saved us from a critical mistake in our go-to-market strategy. Worth every penny for the insights we gained.'
    },
    {
      id: 5,
      name: 'Olivia Thompson',
      role: 'CEO',
      company: 'HealthPulse',
      avatar: 'https://images.pexels.com/photos/1065084/pexels-photo-1065084.jpeg?auto=compress&cs=tinysrgb&w=150',
      content: 'We were matched with our lead investor through Founder Scan\'s VC matching feature. The AI knew exactly which investors were interested in healthtech.'
    }
  ];
  
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    const scrollContainer = scrollContainerRef.current;
    if (!scrollContainer) return;
    
    let scrollAmount = 0;
    const speed = 0.2;
    const gap = 32; // Gap between cards in pixels
    
    const scroll = () => {
      scrollContainer.scrollLeft += speed;
      scrollAmount += speed;
      
      // Reset scroll position when we've scrolled through one full item
      if (scrollAmount >= scrollContainer.children[0].clientWidth + gap) {
        scrollContainer.scrollLeft = 0;
        scrollAmount = 0;
      }
      
      requestAnimationFrame(scroll);
    };
    
    let animationId = requestAnimationFrame(scroll);
    
    // Pause scrolling when hovering
    const handleMouseEnter = () => {
      cancelAnimationFrame(animationId);
    };
    
    const handleMouseLeave = () => {
      animationId = requestAnimationFrame(scroll);
    };
    
    scrollContainer.addEventListener('mouseenter', handleMouseEnter);
    scrollContainer.addEventListener('mouseleave', handleMouseLeave);
    
    return () => {
      cancelAnimationFrame(animationId);
      scrollContainer.removeEventListener('mouseenter', handleMouseEnter);
      scrollContainer.removeEventListener('mouseleave', handleMouseLeave);
    };
  }, []);

  return (
    <section id="testimonials" className="py-20 relative bg-gray-950">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Trusted by <GradientText>Innovative</GradientText> Founders
          </h2>
          <p className="text-gray-300 text-xl max-w-2xl mx-auto">
            See how Founder Scan is helping startups validate their ideas and succeed
          </p>
        </div>
        
        <div 
          ref={scrollContainerRef}
          className="flex overflow-x-hidden space-x-8 pb-8"
        >
          {testimonials.map((testimonial) => (
            <GlassmorphicCard 
              key={testimonial.id} 
              className="flex-shrink-0 w-full md:w-[350px] p-6"
              hoverable
            >
              <div className="mb-6">
                <p className="text-gray-300 italic">"{testimonial.content}"</p>
              </div>
              <div className="flex items-center">
                <img 
                  src={testimonial.avatar} 
                  alt={testimonial.name} 
                  className="w-12 h-12 rounded-full object-cover mr-4 border-2 border-purple-500"
                />
                <div>
                  <h4 className="font-medium text-white">{testimonial.name}</h4>
                  <p className="text-sm text-gray-400">
                    {testimonial.role}, {testimonial.company}
                  </p>
                </div>
              </div>
            </GlassmorphicCard>
          ))}
          
          {/* Duplicate the first few testimonials to create the infinite scroll effect */}
          {testimonials.slice(0, 3).map((testimonial) => (
            <GlassmorphicCard 
              key={`duplicate-${testimonial.id}`}
              className="flex-shrink-0 w-full md:w-[350px] p-6"
              hoverable
            >
              <div className="mb-6">
                <p className="text-gray-300 italic">"{testimonial.content}"</p>
              </div>
              <div className="flex items-center">
                <img 
                  src={testimonial.avatar} 
                  alt={testimonial.name} 
                  className="w-12 h-12 rounded-full object-cover mr-4 border-2 border-purple-500"
                />
                <div>
                  <h4 className="font-medium text-white">{testimonial.name}</h4>
                  <p className="text-sm text-gray-400">
                    {testimonial.role}, {testimonial.company}
                  </p>
                </div>
              </div>
            </GlassmorphicCard>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Testimonials;