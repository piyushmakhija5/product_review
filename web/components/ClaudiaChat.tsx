'use client';

import { useState, useEffect, useRef } from 'react';
import { ClaudiaMessage } from './ClaudiaMessage';
import { ChatInput } from './ChatInput';
import { ResearchProgress } from './ResearchProgress';

interface Message {
  id: string;
  role: 'claudia' | 'user';
  content: string;
  timestamp: Date;
}

type Phase = 'welcome' | 'planning' | 'researching' | 'analyzing' | 'complete';

export function ClaudiaChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [phase, setPhase] = useState<Phase>('welcome');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  const [searchQueries, setSearchQueries] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initial welcome message from Claudia - concise and inviting
  useEffect(() => {
    // Clear any existing messages to prevent duplicates
    console.log('🎯 Initializing ClaudiaChat with welcome message');

    const welcomeMessage: Message = {
      id: '1',
      role: 'claudia',
      content: "Hey! I'm Claudia, your shopping concierge. What are you looking for today?",
      timestamp: new Date(),
    };

    setMessages([welcomeMessage]);
    setPhase('planning');
  }, []);

  const handleAutoContinue = async (currentPhase: Phase) => {
    console.log('⚡ Auto-continuing phase:', currentPhase);
    setIsLoading(true);

    try {
      // Auto-trigger the next phase without user input
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: '[AUTO_CONTINUE]', phase: currentPhase, sessionId }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      console.log('✅ Auto-continue response:', data);

      // Store search queries if provided
      if (data.searchQueries && data.searchQueries.length > 0) {
        setSearchQueries(data.searchQueries);
      }

      // Add Claudia's response
      const claudiaMessage: Message = {
        id: Date.now().toString(),
        role: 'claudia',
        content: data.response,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, claudiaMessage]);

      // Update phase if needed
      if (data.phase) {
        console.log('🔄 Phase updated to:', data.phase);
        setPhase(data.phase);

        // Continue auto-continuing if still in research/analysis
        if (data.phase === 'researching' || data.phase === 'analyzing') {
          console.log('🤖 Continuing to next phase:', data.phase);
          setTimeout(() => {
            handleAutoContinue(data.phase);
          }, 1000);
        }
      }
    } catch (error) {
      console.error('❌ Auto-continue error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (content: string) => {
    console.log('📨 User sending message:', content);

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date(),
    };

    setMessages(prev => {
      console.log('💬 Current messages count:', prev.length);
      return [...prev, userMessage];
    });
    setIsLoading(true);

    try {
      console.log('🌐 Calling API with phase:', phase);

      // Call API to process message
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: content, phase, sessionId }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      console.log('✅ API response:', data);

      // Store search queries if provided
      if (data.searchQueries && data.searchQueries.length > 0) {
        setSearchQueries(data.searchQueries);
      }

      // Add Claudia's response
      const claudiaMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'claudia',
        content: data.response,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, claudiaMessage]);

      // Update phase if needed
      if (data.phase) {
        console.log('🔄 Phase updated to:', data.phase);
        setPhase(data.phase);

        // Auto-continue for research and analysis phases
        if (data.phase === 'researching' || data.phase === 'analyzing') {
          console.log('🤖 Auto-continuing to next phase:', data.phase);

          // Small delay to show Claudia's message first
          setTimeout(() => {
            handleAutoContinue(data.phase);
          }, 800);
        }
      }
    } catch (error) {
      console.error('❌ Error sending message:', error);

      // Error message
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'claudia',
        content: "Oops! Something went wrong. Let's try that again?",
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div
      className="backdrop-blur-xl rounded-3xl overflow-hidden"
      style={{
        backgroundColor: 'rgba(255, 255, 255, 0.92)',
        border: '1px solid rgba(29, 29, 31, 0.08)',
        boxShadow: `
          0 20px 40px rgba(29, 29, 31, 0.08),
          0 10px 20px rgba(29, 29, 31, 0.04),
          0 2px 4px rgba(29, 29, 31, 0.02)
        `,
      }}
    >
      {/* Ultra-Premium Chat Header with Avatar */}
      <div
        className="relative px-6 py-5"
        style={{
          backgroundColor: 'rgba(250, 250, 250, 0.98)',
          borderBottom: '1px solid rgba(29, 29, 31, 0.08)',
        }}
      >
        <div className="relative flex items-center space-x-4">
          {/* Professional Avatar */}
          <div className="relative">
            <div
              className="w-14 h-14 rounded-2xl overflow-hidden"
              style={{
                boxShadow: '0 4px 12px rgba(29, 29, 31, 0.1), 0 2px 6px rgba(29, 29, 31, 0.06)',
              }}
            >
              <div
                className="w-full h-full flex items-center justify-center"
                style={{
                  background: 'linear-gradient(135deg, #F5F5F7 0%, #E8E8E8 100%)',
                }}
              >
                <svg className="w-8 h-8" style={{ color: '#1D1D1F' }} fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/>
                </svg>
              </div>
            </div>
            {/* Online indicator */}
            <div
              className="absolute bottom-0 right-0 w-4 h-4 rounded-full"
              style={{
                backgroundColor: '#34C759',
                border: '2.5px solid rgba(255, 255, 255, 0.98)',
                boxShadow: '0 2px 4px rgba(52, 199, 89, 0.3)',
              }}
            />
          </div>

          <div>
            <h2
              className="font-semibold text-lg"
              style={{
                color: '#1D1D1F',
                letterSpacing: '-0.01em',
              }}
            >
              Claudia
            </h2>
            <div className="flex items-center space-x-2 mt-0.5" style={{ color: '#86868B' }}>
              <span className="text-xs">Shopping Concierge</span>
              <span className="text-xs">•</span>
              <span className="text-xs flex items-center">
                <span className="w-1.5 h-1.5 rounded-full mr-1.5 animate-pulse" style={{ backgroundColor: '#34C759' }} />
                Online
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Messages Container */}
      <div
        className="h-[480px] overflow-y-auto p-6 space-y-4"
        style={{
          backgroundColor: 'rgba(250, 250, 250, 0.5)',
        }}
      >
        {messages.map(message => (
          <ClaudiaMessage key={message.id} message={message} />
        ))}

        {/* Research Progress Indicator */}
        {(phase === 'researching' || phase === 'analyzing') && (
          <ResearchProgress phase={phase} searchQueries={searchQueries} />
        )}

        {isLoading && (
          <div className="flex items-center space-x-2" style={{ color: '#86868B' }}>
            <div className="w-2 h-2 rounded-full animate-bounce" style={{ backgroundColor: '#86868B', animationDelay: '0ms' }} />
            <div className="w-2 h-2 rounded-full animate-bounce" style={{ backgroundColor: '#86868B', animationDelay: '150ms' }} />
            <div className="w-2 h-2 rounded-full animate-bounce" style={{ backgroundColor: '#86868B', animationDelay: '300ms' }} />
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Ultra-Premium Input Area */}
      <div
        className="p-5"
        style={{
          backgroundColor: 'rgba(255, 255, 255, 0.98)',
          borderTop: '1px solid rgba(29, 29, 31, 0.08)',
        }}
      >
        <ChatInput
          onSend={handleSendMessage}
          disabled={isLoading}
          placeholder={
            phase === 'researching'
              ? 'Searching the web...'
              : phase === 'analyzing'
              ? 'Analyzing results...'
              : "Type your message..."
          }
        />
      </div>
    </div>
  );
}
