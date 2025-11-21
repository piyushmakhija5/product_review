'use client';

import { useState, useEffect } from 'react';

export function FlickeringLogo() {
  const [showBlack, setShowBlack] = useState(false);
  const [isFlickering, setIsFlickering] = useState(false);

  useEffect(() => {
    // Start with "Hack" (default state)
    setShowBlack(false);

    // Flicker to "Black" every 10 seconds, stay for 5 seconds, then flicker back
    const flickerCycle = () => {
      setIsFlickering(true);

      // Slower tube light flicker sequence (more visible to humans)
      const flickerToBlack = [
        { delay: 0, show: false },     // Hack (start)
        { delay: 150, show: true },    // Black (flash)
        { delay: 200, show: false },   // Hack (quick)
        { delay: 350, show: true },    // Black (flash)
        { delay: 420, show: false },   // Hack (quick)
        { delay: 600, show: true },    // Black (STAYS for 5s)
      ];

      // Flicker to Black
      flickerToBlack.forEach(({ delay, show }) => {
        setTimeout(() => {
          setShowBlack(show);
        }, delay);
      });

      // End flickering state
      setTimeout(() => {
        setIsFlickering(false);
      }, 700);

      // After 5 seconds on "Black", flicker back to "Hack"
      setTimeout(() => {
        setIsFlickering(true);

        const flickerToHack = [
          { delay: 0, show: true },      // Black (start)
          { delay: 150, show: false },   // Hack (flash)
          { delay: 200, show: true },    // Black (quick)
          { delay: 350, show: false },   // Hack (flash)
          { delay: 420, show: true },    // Black (quick)
          { delay: 600, show: false },   // Hack (STAYS)
        ];

        flickerToHack.forEach(({ delay, show }) => {
          setTimeout(() => {
            setShowBlack(show);
          }, delay);
        });

        setTimeout(() => {
          setIsFlickering(false);
        }, 700);
      }, 5000); // Stay on "Black" for 5 seconds
    };

    // Run the cycle every 15 seconds (10s on Hack + 5s on Black)
    const interval = setInterval(flickerCycle, 15000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex items-center space-x-3">
      <div className="relative">
        {/* Ultra-premium logo with different fonts */}
        <div className="relative overflow-hidden">
          <span
            className={`inline-block text-4xl tracking-tight ${
              isFlickering ? 'animate-pulse' : ''
            }`}
            style={{
              fontFamily: showBlack
                ? "'Courier New', Courier, monospace" // Hackerish monospace for "Black"
                : "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif", // Premium system font for "Hack"
              fontWeight: showBlack ? '700' : '600', // Bold for Black, semibold for Hack
              letterSpacing: showBlack ? '0.05em' : '-0.02em',
              color: showBlack ? '#1D1D1F' : '#1D1D1F', // Deep charcoal
              textShadow: isFlickering
                ? '0 0 20px rgba(29, 29, 31, 0.3)'
                : showBlack
                  ? '0 2px 8px rgba(29, 29, 31, 0.12)'
                  : '0 2px 12px rgba(29, 29, 31, 0.08)',
              filter: isFlickering ? 'brightness(0.9) contrast(1.05)' : 'none',
              transition: isFlickering ? 'none' : 'all 0.3s ease',
            }}
          >
            {showBlack ? 'Black' : 'Hack'}
          </span>
        </div>
      </div>
      <span
        className="text-4xl tracking-tight"
        style={{
          fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
          fontWeight: '600',
          letterSpacing: '-0.02em',
          color: '#1D1D1F',
          textShadow: '0 2px 12px rgba(29, 29, 31, 0.08)',
        }}
      >
        Friday
      </span>
    </div>
  );
}
