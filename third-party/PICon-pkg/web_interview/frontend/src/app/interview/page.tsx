'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { getRecoverableSessionId, setRecoverableSessionId, clearRecoverableSessionId } from '@/lib/storage';

interface Message {
  id: string;
  type: 'system' | 'user';
  content: string;
  timestamp: Date;
}

interface Progress {
  current: number;
  total: number;
  phase: string;
  predefined_complete: number;
  predefined_total: number;
  main_complete: number;
  main_total: number;
  repeat_complete: number;
  repeat_total: number;
}

interface SessionData {
  sessionId: string;
  instruction: string;
  currentQuestion: string;
  phase: string;
  progress: Progress;
  name: string;
}

interface ConversationMessage {
  question: string;
  answer: string;
}

interface RecoverResponse {
  session_id: string;
  recovered: boolean;
  current_question: string | null;
  phase: string;
  progress: Progress;
  is_complete: boolean;
  message: string;
  conversation_history: ConversationMessage[];
  name: string | null;
}

// Helper function to detect URLs and render them as clickable links
function renderMessageContent(content: string) {
  // URL regex pattern - captures URL and any trailing punctuation separately
  const urlPattern = /(https?:\/\/[^\s<>"{}|\\^`\[\]]+)/g;
  const parts = content.split(urlPattern);

  return parts.map((part, index) => {
    if (urlPattern.test(part)) {
      // Reset regex lastIndex since we're reusing it
      urlPattern.lastIndex = 0;

      // Strip trailing punctuation that's likely not part of the URL
      const trailingPunctuation = /[)?\]!.,;:]+$/;
      const match = part.match(trailingPunctuation);
      const url = match ? part.slice(0, -match[0].length) : part;
      const trailing = match ? match[0] : '';

      return (
        <span key={index}>
          <a
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-400 underline hover:text-blue-300 break-all"
          >
            {url}
          </a>
          {trailing}
        </span>
      );
    }
    return part;
  });
}

export default function InterviewPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionData, setSessionData] = useState<SessionData | null>(null);
  const [isComplete, setIsComplete] = useState(false);
  const [progress, setProgress] = useState<Progress | null>(null);
  const [isAwaitingConfirmation, setIsAwaitingConfirmation] = useState(false);
  const [isRecovering, setIsRecovering] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  useEffect(() => {
    const initSession = async () => {
      // First, check if there's a stored session to recover
      const storedSessionId = getRecoverableSessionId();
      
      if (storedSessionId) {
        setIsRecovering(true);
        try {
          const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/recover/${storedSessionId}`);
          if (response.ok) {
            const data: RecoverResponse = await response.json();
            
            if (data.recovered && data.current_question) {
              // Successfully recovered - restore session
              const recoveredSession: SessionData = {
                sessionId: data.session_id,
                instruction: '', // Not needed for recovery
                currentQuestion: data.current_question,
                phase: data.phase,
                progress: data.progress,
                name: data.name || '', // Use recovered name
              };
              
              setSessionData(recoveredSession);
              setProgress(data.progress);
              setIsComplete(data.is_complete);
              
              // Build message history from conversation_history
              const recoveredMessages: Message[] = [
                {
                  id: 'recovery',
                  type: 'system',
                  content: `🔄 Session recovered! ${data.message}`,
                  timestamp: new Date(),
                },
              ];
              
              // Add previous Q&A pairs
              data.conversation_history.forEach((qa, index) => {
                recoveredMessages.push({
                  id: `q-history-${index}`,
                  type: 'system',
                  content: qa.question,
                  timestamp: new Date(),
                });
                recoveredMessages.push({
                  id: `a-history-${index}`,
                  type: 'user',
                  content: qa.answer,
                  timestamp: new Date(),
                });
              });
              
              // Add current pending question
              recoveredMessages.push({
                id: 'q-recovered',
                type: 'system',
                content: data.current_question,
                timestamp: new Date(),
              });
              
              setMessages(recoveredMessages);
              
              setIsRecovering(false);
              return; // Don't fall through to normal init
            }
          }
        } catch (err) {
          console.error('Recovery failed:', err);
        }
        
        // Recovery failed - clear stored session and continue to normal flow
        clearRecoverableSessionId();
        setIsRecovering(false);
      }
      
      // Normal flow: load from sessionStorage
      const stored = sessionStorage.getItem('interviewSession');
      if (!stored) {
        router.push('/');
        return;
      }

      const data: SessionData = JSON.parse(stored);
      setSessionData(data);
      setProgress(data.progress);
      
      // Store session ID for recovery
      setRecoverableSessionId(data.sessionId);

      // Initialize messages with first question
      setMessages([
        {
          id: 'q-0',
          type: 'system',
          content: data.currentQuestion,
          timestamp: new Date(),
        },
      ]);
    };
    
    initSession();
  }, [router]);

  useEffect(() => {
    // Prevent browser back button from leaving the interview page
    window.history.pushState(null, '', window.location.pathname);
    const handlePopState = () => {
      window.history.pushState(null, '', window.location.pathname);
    };
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  useEffect(() => {
    // Scroll to bottom when messages change
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    // Keep focus on input when not loading
    if (!isLoading && !isComplete) {
      inputRef.current?.focus();
    }
  }, [isLoading, isComplete, messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading || !sessionData) return;

    const userMessage = input.trim();
    setInput('');
    setIsLoading(true);

    // Add user message
    const userMsgId = `user-${Date.now()}`;
    setMessages((prev) => [
      ...prev,
      {
        id: userMsgId,
        type: 'user',
        content: userMessage,
        timestamp: new Date(),
      },
    ]);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/respond`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionData.sessionId,
          response: userMessage,
          is_confirmation: isAwaitingConfirmation,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to submit response');
      }

      const data = await response.json();
      setProgress(data.progress);

      if (data.is_complete) {
        setIsComplete(true);
        setIsAwaitingConfirmation(false);
        setMessages((prev) => [
          ...prev,
          {
            id: 'complete',
            type: 'system',
            content: '🎉 Thank you for completing the interview! Please wait while we save your responses...',
            timestamp: new Date(),
          },
        ]);
        
        // Save results to backend
        try {
          // Use AbortController with a reasonable timeout (1 minute)
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), 60000); // 1 minute timeout
          
          const resultsResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/results/${sessionData.sessionId}`, {
            signal: controller.signal,
          });
          clearTimeout(timeoutId);
          
          if (resultsResponse.ok) {
            // Clear stored session ID since interview is complete
            clearRecoverableSessionId();
            
            setMessages((prev) => [
              ...prev,
              {
                id: 'saved',
                type: 'system',
                content: '✅ Your responses have been saved successfully. You may now close this page.',
                timestamp: new Date(),
              },
            ]);
          } else {
            const errorData = await resultsResponse.json().catch(() => ({}));
            console.error('Failed to save results:', errorData);
            setMessages((prev) => [
              ...prev,
              {
                id: 'save-error',
                type: 'system',
                content: '⚠️ There was an issue saving your responses. Please contact the administrator.',
                timestamp: new Date(),
              },
            ]);
          }
        } catch (saveErr) {
          console.error('Error saving results:', saveErr);
          const errorMessage = saveErr instanceof Error && saveErr.name === 'AbortError'
            ? '⏱️ The save is taking longer than expected. Your responses may still be saved. Please contact the administrator if you do not receive confirmation.'
            : '⚠️ There was an issue saving your responses. Please contact the administrator.';
          setMessages((prev) => [
            ...prev,
            {
              id: 'save-error',
              type: 'system',
              content: errorMessage,
              timestamp: new Date(),
            },
          ]);
        }
      } else if (data.confirmation_question && !data.next_question) {
        // Only confirmation question returned - user needs to respond to it first
        setIsAwaitingConfirmation(true);
        setMessages((prev) => [
          ...prev,
          {
            id: `q-${Date.now()}`,
            type: 'system',
            content: data.confirmation_question,
            timestamp: new Date(),
          },
        ]);
      } else if (data.next_question) {
        // Regular next question (confirmation already handled or no confirmation)
        setIsAwaitingConfirmation(false);
        setMessages((prev) => [
          ...prev,
          {
            id: `q-${Date.now()}`,
            type: 'system',
            content: data.next_question,
            timestamp: new Date(),
          },
        ]);
      }
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        {
          id: `error-${Date.now()}`,
          type: 'system',
          content: '⚠️ Error submitting response. Please try again.',
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const getPhaseLabel = (phase: string) => {
    switch (phase) {
      case 'predefined':
        return 'Part 1: Getting to Know You';
      case 'main':
        return 'Part 2: Follow-up Questions';
      case 'repeat':
        return 'Part 3: Clarification';
      case 'complete':
        return 'Complete';
      default:
        return phase;
    }
  };

  if (!sessionData) {
    return (
      <div className="flex min-h-screen items-center justify-center flex-col gap-4">
        <div className="animate-spin h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full"></div>
        {isRecovering && (
          <p className="text-gray-600 text-sm">Recovering your session...</p>
        )}
      </div>
    );
  }

  return (
    <main className="flex flex-col h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm px-4 py-3 flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold text-gray-800">Human Interview</h1>
          <p className="text-sm text-gray-500">Participant: {sessionData.name}</p>
        </div>
        {progress && (
          <div className="text-right">
            <p className="text-sm font-medium text-blue-600">{getPhaseLabel(progress.phase)}</p>
            <p className="text-xs text-gray-500">
              Question {progress.current + 1} of ~{progress.total}
            </p>
          </div>
        )}
      </header>

      {/* Progress bar */}
      {progress && (
        <div className="bg-gray-200 h-1">
          <div
            className="bg-blue-600 h-1 transition-all duration-300"
            style={{ width: `${(progress.current / progress.total) * 100}%` }}
          />
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg px-4 py-2 ${
                msg.type === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white shadow text-gray-800'
              }`}
            >
              <p className="whitespace-pre-wrap text-sm">{renderMessageContent(msg.content)}</p>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white shadow rounded-lg px-4 py-2">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      {!isComplete && (
        <form onSubmit={handleSubmit} className="bg-white border-t px-4 py-3">
          <div className="flex space-x-2">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your response..."
              disabled={isLoading}
              autoFocus
              className="flex-1 px-4 py-2 border border-gray-300 rounded-full focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition disabled:bg-gray-100"
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="bg-blue-600 text-white px-6 py-2 rounded-full hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Send
            </button>
          </div>
          <p className="text-xs text-gray-400 mt-2 text-center">
            Press Enter to send your response.
          </p>
        </form>
      )}

      {isComplete && (
        <div className="bg-green-50 border-t border-green-200 px-4 py-4 text-center">
          <p className="text-green-700 font-medium">Interview Complete! 🎉</p>
          <p className="text-sm text-green-600 mt-1">
            Thank you for your participation. Please do not close this page until you see a confirmation message.
          </p>
        </div>
      )}
    </main>
  );
}
