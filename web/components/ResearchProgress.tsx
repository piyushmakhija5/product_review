'use client';

import { useState, useEffect } from 'react';

interface Props {
  phase: 'researching' | 'analyzing';
  searchQueries?: string[];
}

// Helper function to paraphrase/shorten search queries for user-friendly display
function paraphraseQuery(query: string): string {
  // Remove common prefixes and make more conversational
  let paraphrased = query
    .replace(/^(best|top|good|cheap|affordable)\s+/i, '')
    .replace(/\s+(2024|2025|current|latest|new)\s*/gi, '')
    .replace(/\s+(amazon|best buy|walmart|target)\s*/gi, '')
    .replace(/\s+(deals?|sales?|discounts?|price)\s*/gi, '')
    .replace(/\s+under\s+\$?\d+/gi, '')
    .trim();

  // Capitalize first letter
  paraphrased = paraphrased.charAt(0).toUpperCase() + paraphrased.slice(1);

  // Truncate if too long
  if (paraphrased.length > 60) {
    paraphrased = paraphrased.substring(0, 57) + '...';
  }

  return paraphrased;
}

export function ResearchProgress({ phase, searchQueries = [] }: Props) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [currentQueryIndex, setCurrentQueryIndex] = useState(0);

  // Simulate progress through queries
  useEffect(() => {
    if (phase === 'researching' && searchQueries.length > 0) {
      const interval = setInterval(() => {
        setCurrentQueryIndex(prev => {
          if (prev < searchQueries.length - 1) {
            return prev + 1;
          }
          return prev;
        });
      }, 3000); // Progress every 3 seconds

      return () => clearInterval(interval);
    }
  }, [phase, searchQueries]);

  // Build steps from actual search queries
  const researchSteps = searchQueries.length > 0
    ? searchQueries.map((query, index) => ({
        label: `Searching: ${paraphraseQuery(query)}`,
        status: index < currentQueryIndex ? 'complete' : index === currentQueryIndex ? 'active' : 'pending',
      }))
    : [
        { label: 'Searching retailers for options', status: 'active' },
        { label: 'Reading customer reviews', status: 'pending' },
        { label: 'Checking current prices', status: 'pending' },
      ];

  const analysisSteps = [
    { label: 'Comparing features against your needs', status: 'complete' },
    { label: 'Analyzing value for money', status: 'active' },
    { label: 'Evaluating quality and reliability', status: 'pending' },
    { label: 'Identifying key considerations', status: 'pending' },
  ];

  const steps = phase === 'researching' ? researchSteps : analysisSteps;
  const mainMessage = phase === 'researching'
    ? "I'm checking multiple retailers for you..."
    : "Let me analyze what I found...";

  return (
    <div
      className="relative rounded-2xl overflow-hidden"
      style={{
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        border: '1px solid rgba(29, 29, 31, 0.08)',
        boxShadow: '0 4px 12px rgba(29, 29, 31, 0.06), 0 2px 6px rgba(29, 29, 31, 0.03)',
      }}
    >
      {/* Ultra-subtle background pattern */}
      <div className="absolute inset-0 opacity-[0.02]">
        <div className="absolute inset-0" style={{
          backgroundImage: 'radial-gradient(circle at 2px 2px, rgba(29, 29, 31, 0.5) 1px, transparent 0)',
          backgroundSize: '24px 24px'
        }} />
      </div>

      {/* Header - Always Visible */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="relative w-full p-5 text-left hover:bg-opacity-50 transition-all"
      >
        <div className="flex items-start space-x-4">
          <div className="flex-shrink-0">
            <div
              className="w-12 h-12 rounded-xl flex items-center justify-center"
              style={{
                background: 'linear-gradient(135deg, #CFAC86 0%, #C49A6C 100%)',
                boxShadow: '0 4px 12px rgba(196, 154, 108, 0.25), 0 2px 6px rgba(196, 154, 108, 0.15)',
              }}
            >
              <svg
                className="w-6 h-6 animate-spin"
                fill="none"
                viewBox="0 0 24 24"
                style={{ color: '#FFFFFF' }}
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
            </div>
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-base" style={{ color: '#1D1D1F' }}>
                {mainMessage}
              </h3>
              <svg
                className={`w-5 h-5 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                style={{ color: '#86868B' }}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </div>
            <p className="text-sm mt-1 leading-relaxed" style={{ color: '#86868B' }}>
              {phase === 'researching'
                ? "Working with my network of retailers to find the best deals"
                : "Curating the perfect options based on what you're looking for"}
            </p>
          </div>
        </div>
      </button>

      {/* Collapsible Details */}
      {isExpanded && (
        <div
          className="px-5 pb-5 space-y-2.5 animate-in slide-in-from-top-2"
          style={{
            borderTop: '1px solid rgba(29, 29, 31, 0.06)',
            paddingTop: '16px',
            marginTop: '-4px',
          }}
        >
          {steps.map((step, index) => (
            <div key={index} className="flex items-start space-x-3">
              <div className="flex-shrink-0 mt-1">
                {step.status === 'complete' && (
                  <svg className="w-4 h-4" style={{ color: '#34C759' }} fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                )}
                {step.status === 'active' && (
                  <div className="w-4 h-4 rounded-full border-2 border-t-transparent animate-spin" style={{ borderColor: '#CFAC86', borderTopColor: 'transparent' }} />
                )}
                {step.status === 'pending' && (
                  <div className="w-4 h-4 rounded-full border-2" style={{ borderColor: '#E8E8E8' }} />
                )}
              </div>
              <p
                className="text-sm leading-relaxed"
                style={{
                  color: step.status === 'pending' ? '#C7C7CC' : '#86868B',
                  fontWeight: step.status === 'active' ? 500 : 400,
                }}
              >
                {step.label}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
