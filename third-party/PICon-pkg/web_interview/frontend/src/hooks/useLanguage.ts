/**
 * Custom hook for managing language state
 */

import { useState, useEffect } from 'react';
import { Language } from '@/types/consent';
import { getLanguage, setLanguage as saveLanguage } from '@/lib/storage';
import { getTranslation } from '@/lib/translations';

export function useLanguage() {
  const [language, setLanguageState] = useState<Language>('en');

  // Load language from sessionStorage on mount
  useEffect(() => {
    const storedLanguage = getLanguage();
    setLanguageState(storedLanguage);
  }, []);

  // Set language and persist to sessionStorage
  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
    saveLanguage(lang);
  };

  // Get translations for current language
  const t = getTranslation(language);

  return {
    language,
    setLanguage,
    t,
  };
}
