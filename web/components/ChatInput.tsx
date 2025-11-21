'use client';

import { useState, KeyboardEvent, useRef, useEffect } from 'react';

interface Props {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export function ChatInput({ onSend, disabled = false, placeholder = "Type your message..." }: Props) {
  const [input, setInput] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-focus on mount and when disabled changes
  useEffect(() => {
    if (!disabled && inputRef.current) {
      inputRef.current.focus();
    }
  }, [disabled]);

  const handleSend = () => {
    if (input.trim() && !disabled) {
      onSend(input.trim());
      setInput('');
      // Refocus after sending
      setTimeout(() => {
        inputRef.current?.focus();
      }, 0);
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex items-center space-x-3">
      <div className="flex-1 relative">
        <input
          ref={inputRef}
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          placeholder={placeholder}
          className="w-full px-5 py-3.5 rounded-full focus:outline-none disabled:cursor-not-allowed transition-all text-sm"
          style={{
            backgroundColor: 'rgba(245, 245, 247, 0.9)',
            border: '1px solid rgba(29, 29, 31, 0.1)',
            color: '#1D1D1F',
            boxShadow: '0 2px 6px rgba(29, 29, 31, 0.04)',
          }}
          onFocus={(e) => {
            e.target.style.backgroundColor = 'rgba(255, 255, 255, 0.98)';
            e.target.style.borderColor = 'rgba(207, 172, 134, 0.4)';
            e.target.style.boxShadow = '0 4px 12px rgba(207, 172, 134, 0.15), 0 2px 6px rgba(29, 29, 31, 0.04)';
          }}
          onBlur={(e) => {
            e.target.style.backgroundColor = 'rgba(245, 245, 247, 0.9)';
            e.target.style.borderColor = 'rgba(29, 29, 31, 0.1)';
            e.target.style.boxShadow = '0 2px 6px rgba(29, 29, 31, 0.04)';
          }}
        />
      </div>
      <button
        onClick={handleSend}
        disabled={!input.trim() || disabled}
        className="px-5 py-3.5 rounded-full font-semibold disabled:opacity-40 disabled:cursor-not-allowed transition-all transform hover:-translate-y-0.5"
        style={{
          background: 'linear-gradient(135deg, #CFAC86 0%, #C49A6C 100%)',
          color: '#FFFFFF',
          boxShadow: '0 4px 12px rgba(196, 154, 108, 0.25), 0 2px 6px rgba(196, 154, 108, 0.15)',
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.boxShadow = '0 6px 16px rgba(196, 154, 108, 0.35), 0 3px 8px rgba(196, 154, 108, 0.2)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.boxShadow = '0 4px 12px rgba(196, 154, 108, 0.25), 0 2px 6px rgba(196, 154, 108, 0.15)';
        }}
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
        </svg>
      </button>
    </div>
  );
}
