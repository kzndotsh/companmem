'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useLanguage } from '@/hooks/useLanguage';
import { getConsentState, setConsentState, clearConsentState } from '@/lib/storage';
import ProgressIndicator from '@/components/consent/ProgressIndicator';
import ConsentStep from '@/components/consent/ConsentStep';

export default function ConsentPage() {
  const router = useRouter();
  const { language, t } = useLanguage();
  const [currentStep, setCurrentStep] = useState(0);
  const [consents, setConsents] = useState<boolean[]>(Array(6).fill(false));
  const [name, setName] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  // Load consent state from sessionStorage on mount
  useEffect(() => {
    const state = getConsentState();

    if (!state || !state.name) {
      // No name found - redirect to home
      router.push('/');
      return;
    }

    setName(state.name);
    setCurrentStep(state.currentStep || 0);
    setConsents(state.consentsGiven || Array(6).fill(false));
  }, [router]);

  // Save state to sessionStorage whenever it changes
  useEffect(() => {
    if (name) {
      setConsentState({
        language,
        name,
        currentStep,
        consentsGiven: consents,
        timestamp: new Date().toISOString(),
      });
    }
  }, [currentStep, consents, name, language]);

  const handleCheckboxChange = (checked: boolean) => {
    const newConsents = [...consents];
    newConsents[currentStep] = checked;
    setConsents(newConsents);
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleNext = async () => {
    const isLastStep = currentStep === 5;

    if (isLastStep) {
      // All consents completed - start interview
      await startInterview();
    } else {
      // Move to next step
      setCurrentStep(currentStep + 1);
    }
  };

  const startInterview = async () => {
    setIsLoading(true);
    setError('');

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name,
          question_seed: 42,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to start interview');
      }

      const data = await response.json();

      // Store interview session data
      sessionStorage.setItem(
        'interviewSession',
        JSON.stringify({
          sessionId: data.session_id,
          instruction: data.instruction,
          currentQuestion: data.first_question,
          phase: data.phase,
          progress: data.progress,
          name,
        })
      );

      // Clear consent state (no longer needed)
      clearConsentState();

      // Navigate to interview
      router.push('/interview');
    } catch (err) {
      console.error(err);
      setError(t.home.errorStart);
    } finally {
      setIsLoading(false);
    }
  };

  const canProceed = consents[currentStep];
  const isLastStep = currentStep === 5;
  const totalSteps = t.consent.steps.length;

  // Progress label with proper formatting
  const progressLabel = t.consent.progressLabel
    .replace('{current}', String(currentStep + 1))
    .replace('{total}', String(totalSteps));

  if (!name) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="animate-spin h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full"></div>
      </div>
    );
  }

  return (
    <main className="flex flex-col min-h-screen bg-gray-50 py-8 px-4">
      {/* Header */}
      <div className="max-w-3xl mx-auto w-full mb-6">
        <h1 className="text-3xl font-bold text-center text-gray-800 mb-2">
          {t.consent.title}
        </h1>
        <p className="text-center text-gray-600">
          {name}
        </p>
      </div>

      {/* Warning Banner */}
      <div className="max-w-3xl mx-auto w-full mb-6">
        <div className="bg-amber-50 border border-amber-300 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <span className="text-amber-600 text-xl flex-shrink-0">⚠️</span>
            <p
              className="text-amber-800 text-sm leading-relaxed"
              dangerouslySetInnerHTML={{
                __html: t.consent.warning.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
              }}
            />
          </div>
        </div>
      </div>

      {/* Progress Indicator */}
      <ProgressIndicator
        currentStep={currentStep}
        totalSteps={totalSteps}
        label={progressLabel}
      />

      {/* Current Step */}
      <div className="flex-1 mb-8">
        <ConsentStep
          stepNumber={currentStep + 1}
          content={t.consent.steps[currentStep]}
          isChecked={consents[currentStep]}
          onCheck={handleCheckboxChange}
        />
      </div>

      {/* Error Message */}
      {error && (
        <div className="max-w-3xl mx-auto w-full mb-4">
          <p className="text-red-600 text-sm text-center bg-red-50 border border-red-200 rounded-lg py-2 px-4">
            {error}
          </p>
        </div>
      )}

      {/* Navigation Buttons */}
      <div className="max-w-3xl mx-auto w-full flex justify-between items-center gap-4">
        <button
          onClick={handlePrevious}
          disabled={currentStep === 0}
          className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {t.common.previous}
        </button>

        <button
          onClick={handleNext}
          disabled={!canProceed || isLoading}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          {isLoading && (
            <svg
              className="animate-spin h-4 w-4"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              ></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
          )}
          {isLastStep ? t.consent.startInterview : t.common.next}
        </button>
      </div>
    </main>
  );
}
