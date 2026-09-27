/**
 * TypeScript types for consent flow
 */

export type Language = 'en' | 'ko';

export interface ConsentStepContent {
  title: string;
  description: string;
  checkboxLabel: string;
  details?: string[];
}

export interface ConsentState {
  language: Language;
  name: string;
  currentStep: number;
  consentsGiven: boolean[];
  timestamp?: string;
}

export interface SessionData {
  name: string;
  language: Language;
  consentTimestamp: string;
}
