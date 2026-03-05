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
            success('Settings saved successfully!');
        } catch (err) {
            console.error('Failed to save settings', err);
            showError('Failed to save settings. Please try again.');
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
                    <h3>🔔 Notifications</h3>
                    <p style={{ color: 'var(--text-secondary)', marginBottom: '1rem' }}>Configure how you receive updates and reminders.</p>

                    <div className="form-group" style={{ marginTop: '1rem' }}>
                        <label>Email Address</label>
                        <input
                            type="email"
                            className="filter-input"
                            style={{ width: '100%', maxWidth: '400px', display: 'block', marginTop: '5px' }}
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="Enter your email"
                        />
                    </div>

                    <div className="form-group" style={{ marginTop: '15px' }}>
                        <label style={{ display: 'flex', alignItems: 'center', gap: '10px', cursor: 'pointer' }}>
                            <input
                                type="checkbox"
                                checked={notificationsEnabled}
                                onChange={(e) => setNotificationsEnabled(e.target.checked)}
                            />
                            Enable Email Notifications
                        </label>
                        <small style={{ display: 'block', marginTop: '5px', color: 'var(--text-secondary)' }}>Receive daily reminders and approval requests.</small>
                    </div>

                    {isPushSupported ? (
                        <div style={{ marginTop: '1.5rem', paddingTop: '1.5rem', borderTop: '1px solid rgba(255,255,255,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                            <div>
                                <h4>Push Notifications</h4>
                                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9em' }}>
                                    {pushSubscribed
                                        ? "Notifications are enabled for this device."
                                        : "Enable notifications to stay updated on chores and rewards."}
                                </p>
                            </div>
                            <button
                                className={`btn ${pushSubscribed ? 'btn-secondary' : 'btn-primary'}`}
                                onClick={() => pushSubscribed ? unsubscribeFromPush() : subscribeToPush()}
                            >
                                {pushSubscribed ? 'Disable' : 'Enable'}
                            </button>
                        </div>
                    ) : (
                        <p style={{ color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
                            Push notifications are not supported by this browser.
                        </p>
                    )}

                    <button
                        className="btn btn-primary"
                        style={{ marginTop: '20px' }}
                        onClick={handleSaveSettings}
                        disabled={isSavingSettings}
                    >
                        {isSavingSettings ? 'Saving...' : 'Save Settings'}
                    </button>
                </div>

                <div className="section glass-panel" style={{ marginTop: '2rem' }}>
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
