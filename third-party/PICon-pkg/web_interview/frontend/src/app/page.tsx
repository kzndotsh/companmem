'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useLanguage } from '@/hooks/useLanguage';
import { Language } from '@/types/consent';
import { setConsentState, getRecoverableSessionId, clearAllSessionData } from '@/lib/storage';

export default function Home() {
  const router = useRouter();
  const { language, setLanguage, t } = useLanguage();
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const [hasExistingSession, setHasExistingSession] = useState(false);

  useEffect(() => {
    setHasExistingSession(!!getRecoverableSessionId());
  }, []);

  const handleStart = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      setError(t.home.errorName);
      return;
    }

    setConsentState({
      language,
      name: name.trim(),
      currentStep: 0,
      consentsGiven: Array(6).fill(false),
      timestamp: new Date().toISOString(),
    });

    router.push('/consent');
  };

  const handleStartNew = () => {
    clearAllSessionData();
    setHasExistingSession(false);
  };

  if (hasExistingSession) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center p-8 bg-gradient-to-b from-gray-50 to-gray-100">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-2xl font-bold text-center mb-6 text-gray-800">
            {t.home.title}
          </h1>

          <div className="mb-6 p-4 bg-amber-50 border border-amber-200 rounded-md">
            <p className="font-medium text-amber-800 mb-1">{t.home.existingSessionTitle}</p>
            <p className="text-sm text-amber-700">{t.home.existingSessionDescription}</p>
          </div>

          <div className="space-y-3">
            <button
              onClick={() => router.push('/interview')}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition"
            >
              {t.home.continueSession}
            </button>
            <button
              onClick={handleStartNew}
              className="w-full bg-white text-gray-700 py-2 px-4 rounded-md border border-gray-300 hover:bg-gray-50 transition"
            >
              {t.home.startNewInterview}
            </button>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8 bg-gradient-to-b from-gray-50 to-gray-100">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
        <h1 className="text-2xl font-bold text-center mb-6 text-gray-800">
          {t.home.title}
        </h1>

        <p className="text-gray-600 mb-6 text-sm">
          {t.home.description}
        </p>

        <form onSubmit={handleStart} className="space-y-4">
          {/* Language Selection */}
          <div>
            <label htmlFor="language" className="block text-sm font-medium text-gray-700 mb-1">
              {t.common.language}
            </label>
            <select
              id="language"
              value={language}
              onChange={(e) => setLanguage(e.target.value as Language)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition bg-white"
            >
              <option value="en">English</option>
              <option value="ko">한국어 (Korean)</option>
            </select>
          </div>

          {/* Name Input */}
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
              {t.home.nameLabel}
            </label>
            <input
              type="text"
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition"
              placeholder={t.home.namePlaceholder}
            />
          </div>

          {error && (
            <p className="text-red-500 text-sm">{error}</p>
          )}

          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {t.home.continueButton}
          </button>
        </form>

        <p className="mt-6 text-xs text-gray-500 text-center">
          {t.home.privacyNote}
        </p>
      </div>
    </main>
  );
}
