import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import api from '../api';

interface LanguageSwitcherProps {
    userId?: number | null;
    onLanguageChange?: (lang: string) => void;
    isAdmin?: boolean;
}

const LanguageSwitcher: React.FC<LanguageSwitcherProps> = ({ userId, onLanguageChange, isAdmin = false }) => {
    const { t, i18n } = useTranslation();
    const [mode] = useState<'default' | 'override'>('default');
    const [loading, setLoading] = useState(false);
    const [familyDefault, setFamilyDefault] = useState('en');

    // Load initial settings
    useEffect(() => {
        const loadSettings = async () => {
            try {
                // Get family default
                const res = await api.get('/settings/language/default');
                setFamilyDefault(res.data.value);

                // If user is logged in, check their preference
                if (userId) {
                    // We need to fetch user details to know their current preference
                    // Since we don't have a direct endpoint for just that, we might rely on props or context
                    // For now, let's assume if i18n.language matches family default, they are using default
                    // This logic might need refinement with proper user data fetching
                }
            } catch (err) {
                console.error('Failed to load language settings', err);
            }
        };
        loadSettings();
    }, [userId]);

    const handleLanguageChange = async (lang: string) => {
        setLoading(true);
        try {
            await i18n.changeLanguage(lang);
            localStorage.setItem('chorespec_language', lang);

            if (userId) {
                // Save user preference
                await api.put(`/users/${userId}/language`, { preferred_language: lang });
            }

            if (onLanguageChange) onLanguageChange(lang);
        } catch (err) {
            console.error('Failed to change language', err);
        } finally {
            setLoading(false);
        }
    };

    const handleFamilyDefaultChange = async (lang: string) => {
        if (!isAdmin) return;
        setLoading(true);
        try {
            await api.put('/settings/language/default', { key: 'default_language', value: lang });
            setFamilyDefault(lang);
            // If current user is using default, update their view
            if (mode === 'default') {
                i18n.changeLanguage(lang);
            }
        } catch (err) {
            console.error('Failed to update family default', err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="language-switcher glass-panel" style={{ padding: '1.5rem' }}>
            <h3>{t('settings.language.title')}</h3>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '1rem' }}>
                {t('settings.language.description')}
            </p>

            <div className="language-options" style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                <button
                    className={`btn ${i18n.language === 'en' ? 'btn-primary' : 'btn-secondary'}`}
                    onClick={() => handleLanguageChange('en')}
                    disabled={loading}
                >
                    🇺🇸 English
                </button>
                <button
                    className={`btn ${i18n.language === 'de' ? 'btn-primary' : 'btn-secondary'}`}
                    onClick={() => handleLanguageChange('de')}
                    disabled={loading}
                >
                    🇩🇪 Deutsch
                </button>
            </div>

            {isAdmin && (
                <div style={{ marginTop: '2rem', borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '1rem' }}>
                    <h4>👮 {t('settings.language.familyDefault')}</h4>
                    <div style={{ display: 'flex', gap: '1rem', marginTop: '0.5rem' }}>
                        <button
                            className={`btn btn-sm ${familyDefault === 'en' ? 'btn-primary' : 'btn-outline'}`}
                            onClick={() => handleFamilyDefaultChange('en')}
                        >
                            English
                        </button>
                        <button
                            className={`btn btn-sm ${familyDefault === 'de' ? 'btn-primary' : 'btn-outline'}`}
                            onClick={() => handleFamilyDefaultChange('de')}
                        >
                            Deutsch
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default LanguageSwitcher;
