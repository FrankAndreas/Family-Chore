import React from 'react';
import { useTranslation } from 'react-i18next';
import LanguageSwitcher from '../components/LanguageSwitcher';
import { useOutletContext } from 'react-router-dom';
import type { User } from '../types';
import './admin/Dashboard.css'; // Reuse dashboard styles

interface ContextType {
    currentUser: User | null;
}

const SettingsPage: React.FC = () => {
    const { t } = useTranslation();
    const { currentUser } = useOutletContext<ContextType>();

    return (
        <div className="page-container fade-in">
            <header className="page-header">
                <div className="header-content">
                    <div>
                        <h1 className="page-title">{t('settings.title')}</h1>
                        <p className="page-subtitle">{t('settings.subtitle')}</p>
                    </div>
                </div>
            </header>

            <div className="dashboard-sections">
                <div className="section">
                    <LanguageSwitcher
                        userId={currentUser?.id}
                        isAdmin={currentUser?.role.name === 'Admin'}
                    />
                </div>

                <div className="section glass-panel">
                    <h3>🚧 More Settings Coming Soon</h3>
                    <p style={{ color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
                        Profile customization, notification preferences, and more.
                    </p>
                </div>
            </div>
        </div>
    );
};

export default SettingsPage;
