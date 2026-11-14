"use client";

import { useEffect } from 'react';
import gsap from 'gsap';
import ScrollTrigger from 'gsap/ScrollTrigger';
import { ScanEye, TimerIcon, SearchCheck, Compass } from 'lucide-react'

const icons = {
    ScanEye,
    TimerIcon,
    SearchCheck,
    Compass,
  };

gsap.registerPlugin(ScrollTrigger);

const FeatureCards = ({ featureList }) => {
  useEffect(() => {
    if (typeof window === 'undefined' || window.innerWidth >= 768) return;

    const cards = gsap.utils.toArray('.feature-card');

    cards.forEach((card) => {
      gsap.fromTo(
        card,
        { scale: 0.7, opacity: 0.7 },
        {
          scale: 1,
          opacity: 1,
          ease: 'power2.out',
          scrollTrigger: {
            trigger: card,
            start: 'top 90%',
            end: 'bottom 10%',
            scrub: true,
            toggleActions: 'play reverse play reverse',
          },
        }
      );
    });

    return () => {
      ScrollTrigger.getAll().forEach(trigger => trigger.kill());
    };
  }, []);

  return (
    <div className="flex flex-wrap flex-col md:flex-row gap-8 justify-center">
    {featureList.map((card, index) => {
      const Icon = icons[card.icon];

      return (
        <div
            className="feature-card w-full md:max-w-[18rem] flex flex-col flex-grow"
            key={index}
            >
            <div className="card bg-white border border-gray-300 rounded-[20px] w-full h-full md:hover:scale-105 transition duration-300 flex flex-col">
                <div className="p-10 flex-grow flex flex-col">
                <Icon className="text-secondary-blue size-12 md:size-14 mx-auto mb-4 md:mb-6" />
                <h3 className="font-semibold text-2xl md:text-xl  mb-2">{card.name}</h3>
                <p className="text-base md:text-lg leading-[1.45] flex-grow">{card.description}</p>
                </div>
            </div>
            </div>

      );
    })}
  </div>
  );
};

export default FeatureCards;
