import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

import enTranslations from './locales/en.json';
import deTranslations from './locales/de.json';

// Initialize i18next
i18n
    .use(LanguageDetector) // Detect user language
    .use(initReactI18next) // Pass i18n instance to react-i18next
    .init({
        resources: {
            en: {
                translation: enTranslations
            },
            de: {
                translation: deTranslations
            }
        },
        fallbackLng: 'en', // Fallback language
        debug: false, // Set to true for debugging

        interpolation: {
            escapeValue: false // React already escapes values
        },

        // Detection options
        detection: {
            order: ['localStorage', 'navigator'],
            caches: ['localStorage'],
            lookupLocalStorage: 'chorespec_language'
        }
    });

export default i18n;
