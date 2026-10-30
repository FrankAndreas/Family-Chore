import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import api from '../api';

interface LanguageSwitcherProps {
    userId?: number | null;
    isAdmin?: boolean;
}

const LanguageSwitcher: React.FC<LanguageSwitcherProps> = ({ userId, isAdmin = false }) => {
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

            <p>{t('settings.language.inHub')}</p>

            {isAdmin && (
                <div style={{ marginTop: '2rem', borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '1rem' }}>
                    <h4>👮 {t('settings.language.familyDefault')}</h4>
                    <div style={{ display: 'flex', gap: '1rem', marginTop: '0.5rem' }}>
                        <button
                            className={`btn btn-sm ${familyDefault === 'en' ? 'btn-primary' : 'btn-outline'}`}
                            onClick={() => handleFamilyDefaultChange('en')}
                            disabled={loading}
                        >
                            English
                        </button>
                        <button
                            className={`btn btn-sm ${familyDefault === 'de' ? 'btn-primary' : 'btn-outline'}`}
                            onClick={() => handleFamilyDefaultChange('de')}
                            disabled={loading}
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
