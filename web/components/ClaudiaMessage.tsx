'use client';

import ReactMarkdown from 'react-markdown';

interface Message {
  id: string;
  role: 'claudia' | 'user';
  content: string;
  timestamp: Date;
}

interface Props {
  message: Message;
}

export function ClaudiaMessage({ message }: Props) {
  const isClaudia = message.role === 'claudia';

  return (
    <div className={`flex ${isClaudia ? 'justify-start' : 'justify-end'} items-start space-x-3`}>
      {isClaudia && (
        <div
          className="flex-shrink-0 w-9 h-9 rounded-xl flex items-center justify-center"
          style={{
            background: 'linear-gradient(135deg, #F5F5F7 0%, #E8E8E8 100%)',
            boxShadow: '0 2px 6px rgba(29, 29, 31, 0.08)',
          }}
        >
          <svg className="w-5 h-5" style={{ color: '#1D1D1F' }} fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/>
          </svg>
        </div>
      )}

      <div className="max-w-[75%]">
        <div
          className="rounded-2xl px-5 py-3.5"
          style={
            isClaudia
              ? {
                  backgroundColor: 'rgba(255, 255, 255, 0.95)',
                  border: '1px solid rgba(29, 29, 31, 0.08)',
                  boxShadow: '0 4px 12px rgba(29, 29, 31, 0.06), 0 2px 6px rgba(29, 29, 31, 0.03)',
                  borderTopLeftRadius: '0.5rem',
                }
              : {
                  background: 'linear-gradient(135deg, #CFAC86 0%, #C49A6C 100%)', // Soft gold/bronze
                  boxShadow: '0 4px 12px rgba(196, 154, 108, 0.25), 0 2px 6px rgba(196, 154, 108, 0.15)',
                  borderTopRightRadius: '0.5rem',
                }
          }
        >
          {isClaudia ? (
            <div
              className="prose prose-sm max-w-none prose-p:my-1 prose-p:leading-relaxed prose-headings:my-2"
              style={{ color: '#1D1D1F' }}
            >
              <ReactMarkdown>{message.content}</ReactMarkdown>
            </div>
          ) : (
            <p className="text-base leading-relaxed" style={{ color: '#FFFFFF' }}>
              {message.content}
            </p>
          )}

          {/* Timestamp */}
          <div
            className="text-xs mt-2"
            style={{ color: isClaudia ? '#86868B' : 'rgba(255, 255, 255, 0.8)' }}
          >
            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </div>
        </div>
      </div>
    </div>
  );
}
