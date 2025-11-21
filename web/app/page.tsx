'use client';

import { FlickeringLogo } from '@/components/FlickeringLogo';
import { ClaudiaChat } from '@/components/ClaudiaChat';

export default function Home() {
  return (
    <main className="min-h-screen relative overflow-hidden" style={{ backgroundColor: '#FAFAFA' }}>
      {/* Ultra-Premium Apple Store Background */}
      <div className="absolute inset-0 -z-10">
        {/* Warm gradient mesh - barely perceptible */}
        <div
          className="absolute inset-0"
          style={{
            background: 'linear-gradient(135deg, #FAFAFA 0%, #F5F5F7 50%, #FAFAFA 100%)',
          }}
        />

        {/* Soft lighting effect - like premium product photography */}
        <div
          className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[800px] rounded-full opacity-30"
          style={{
            background: 'radial-gradient(circle, rgba(255,255,255,0.8) 0%, transparent 70%)',
            filter: 'blur(80px)',
          }}
        />

        {/* Subtle warm accent glow - very faint */}
        <div
          className="absolute bottom-0 right-1/4 w-[600px] h-[600px] rounded-full opacity-10"
          style={{
            background: 'radial-gradient(circle, rgba(207,172,134,0.3) 0%, transparent 70%)',
            filter: 'blur(100px)',
          }}
        />

        {/* Ultra-subtle grid pattern for depth */}
        <div
          className="absolute inset-0 opacity-[0.015]"
          style={{
            backgroundImage: `
              linear-gradient(rgba(29,29,31,0.1) 1px, transparent 1px),
              linear-gradient(90deg, rgba(29,29,31,0.1) 1px, transparent 1px)
            `,
            backgroundSize: '60px 60px',
          }}
        />
      </div>

      {/* Ultra-Premium Glass Header */}
      <header
        className="fixed top-0 left-0 right-0 z-50 backdrop-blur-xl border-b"
        style={{
          backgroundColor: 'rgba(250, 250, 250, 0.8)',
          borderBottomColor: 'rgba(29, 29, 31, 0.08)',
          boxShadow: '0 1px 3px rgba(29, 29, 31, 0.04), 0 1px 2px rgba(29, 29, 31, 0.03)',
        }}
      >
        <div className="max-w-7xl mx-auto px-8 sm:px-12 lg:px-16 h-24 flex items-center justify-center">
          <FlickeringLogo />
        </div>
      </header>

      {/* Main Content */}
      <div className="pt-32 pb-20 px-6 sm:px-8 lg:px-12 min-h-screen flex items-start justify-center">
        <div className="max-w-3xl w-full">
          <ClaudiaChat />
        </div>
      </div>
    </main>
  );
}
