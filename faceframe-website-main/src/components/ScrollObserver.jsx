'use client';
import { useEffect } from 'react';

export default function ScrollObserver() {
  useEffect(() => {
    const startObserver = () => {
      const observer = new IntersectionObserver(
        (entries, obs) => {
          entries.forEach(entry => {
            if (entry.isIntersecting) {
              entry.target.classList.add('active');
              obs.unobserve(entry.target);
            }
          });
        },
        { threshold: 0.6 }
      );

      const elements = document.querySelectorAll('.reveal, .reveal-lg, .reveal-sm, .reveal-btn, .reveal-left, .reveal-right');
      elements.forEach(el => observer.observe(el));
    };

    // attach observer after load for performance 
    if (document.readyState === 'complete') {
      startObserver();
    } else {
      window.addEventListener('load', startObserver);
    }

    return () => window.removeEventListener('load', startObserver);
  }, []);

  return null;
}
