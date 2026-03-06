import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import LanguageSwitcher from '../components/LanguageSwitcher';
import { useOutletContext } from 'react-router-dom';
import { useNotifications } from '../context/NotificationContext';
import { updateUser } from '../api';
import Toast from '../components/Toast';
import { useToast } from '../hooks/useToast';
import type { User } from '../types';
import './admin/Dashboard.css'; // Reuse dashboard styles

interface ContextType {
    currentUser: User | null;
}

const SettingsPage: React.FC = () => {
    const { t } = useTranslation();
    const { currentUser } = useOutletContext<ContextType>();
    const { isPushSupported, pushSubscribed, subscribeToPush, unsubscribeFromPush } = useNotifications();
    const { toasts, removeToast, success, error: showError } = useToast();

    const [email, setEmail] = useState(currentUser?.email || '');
    const [notificationsEnabled, setNotificationsEnabled] = useState(currentUser?.notifications_enabled ?? true);
    const [isSavingSettings, setIsSavingSettings] = useState(false);

    useEffect(() => {
        if (currentUser) {
            setEmail(currentUser.email || '');
            setNotificationsEnabled(currentUser.notifications_enabled ?? true);
        }
    }, [currentUser]);

    const handleSaveSettings = async () => {
        if (!currentUser) return;
        setIsSavingSettings(true);
        try {
            await updateUser(currentUser.id, {
                email: email || null,
                notifications_enabled: notificationsEnabled
            });
            success(t('settings.settingsSavedSuccess', 'Settings saved successfully!'));
        } catch (err) {
            console.error('Failed to save settings', err);
            showError(t('settings.settingsSavedError', 'Failed to save settings. Please try again.'));
        } finally {
            setIsSavingSettings(false);
        }
    };

    return (
        <div className="page-container fade-in">
            {/* Toast notifications */}
            <div className="toast-container">
                {toasts.map(toast => (
                    <Toast
                        key={toast.id}
                        message={toast.message}
                        type={toast.type}
                        duration={toast.duration}
                        onClose={() => removeToast(toast.id)}
                    />
                ))}
            </div>

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
                    <h3>🔔 {t('settings.notifications', 'Notifications')}</h3>
                    <p className="text-secondary mb-3">{t('settings.notificationsDesc', 'Configure how you receive updates and reminders.')}</p>

                    <div className="form-group mt-3">
                        <label>{t('settings.emailAddress', 'Email Address')}</label>
                        <input
                            type="email"
                            className="filter-input w-full max-w-sm block mt-1"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder={t('settings.enterEmail', 'Enter your email')}
                        />
                    </div>

                    <div className="form-group mt-3">
                        <label className="flex-center gap-1 cursor-pointer">
                            <input
                                type="checkbox"
                                checked={notificationsEnabled}
                                onChange={(e) => setNotificationsEnabled(e.target.checked)}
                            />
                            {t('settings.enableEmailNotifications', 'Enable Email Notifications')}
                        </label>
                        <small className="block mt-1 text-secondary">{t('settings.emailNotificationsDesc', 'Receive daily reminders and approval requests.')}</small>
                    </div>

                    {isPushSupported ? (
                        <div className="mt-4 pt-4 border-t flex-between">
                            <div>
                                <h4>{t('settings.pushNotifications', 'Push Notifications')}</h4>
                                <p className="text-secondary text-sm">
                                    {pushSubscribed
                                        ? t('settings.pushNotificationsEnabled', "Notifications are enabled for this device.")
                                        : t('settings.pushNotificationsDisabled', "Enable notifications to stay updated on chores and rewards.")}
                                </p>
                            </div>
                            <button
                                className={`btn ${pushSubscribed ? 'btn-secondary' : 'btn-primary'}`}
                                onClick={() => pushSubscribed ? unsubscribeFromPush() : subscribeToPush()}
                            >
                                {pushSubscribed ? t('common.disable', 'Disable') : t('common.enable', 'Enable')}
                            </button>
                        </div>
                    ) : (
                        <p className="text-secondary mt-2">
                            {t('settings.pushNotSupported', 'Push notifications are not supported by this browser.')}
                        </p>
                    )}

                    <button
                        className="btn btn-primary mt-4"
                        onClick={handleSaveSettings}
                        disabled={isSavingSettings}
                    >
                        {isSavingSettings ? t('common.saving', 'Saving...') : t('settings.saveSettings', 'Save Settings')}
                    </button>
                </div>

                <div className="section glass-panel mt-5">
                    <h3>{t('settings.moreSettings')}</h3>
                    <p className="text-secondary mt-2">
                        {t('settings.moreSettingsDesc')}
                    </p>
                </div>
            </div>
        </div>
    );
};

export default SettingsPage;
