import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { login } from '../api';
import type { User } from '../types';
import FamilyDashboardView from './FamilyDashboard';
import './Login.css';

interface LoginProps {
    onLogin: (user: User) => void;
}

export default function Login({ onLogin }: LoginProps) {
    const { t } = useTranslation();
    const [nickname, setNickname] = useState('');
    const [pin, setPin] = useState('');
    const [showPin, setShowPin] = useState(false);
    const [nicknameError, setNicknameError] = useState('');
    const [pinError, setPinError] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [showFamilyDash, setShowFamilyDash] = useState(false);
    // const [submitted, setSubmitted] = useState(false); // Commented out: planned for deferred blur validation (F1)

    if (showFamilyDash) {
        return <FamilyDashboardView onExit={() => setShowFamilyDash(false)} />;
    }

    const validate = () => {
        let valid = true;
        if (!nickname.trim()) {
            setNicknameError(t('login.error.nicknameRequired'));
            valid = false;
        } else {
            setNicknameError('');
        }

        if (!pin.trim()) {
            setPinError(t('login.error.pinRequired'));
            valid = false;
        } else if (!/^\d{4}$/.test(pin)) {
            setPinError(t('login.error.pinFormat'));
            valid = false;
        } else {
            setPinError('');
        }
        return valid;
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!validate()) return;

        setError('');
        setLoading(true);

        try {
            const response = await login(nickname, pin);
            localStorage.setItem('auth_token', response.data.access_token);
            onLogin(response.data.user);
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } catch (err: any) {
            setError(err.response?.data?.detail || t('login.error.loginFailed'));
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="login-container">
            <div className="login-card glass-card">
                <div className="login-header">
                    <h1 className="login-title">🎮 ChoreSpec</h1>
                    <p className="login-subtitle">{t('login.subtitle')}</p>
                </div>

                <form onSubmit={handleSubmit} className="login-form">
                    <div className="form-group">
                        <label htmlFor="nickname">{t('login.nickname')}</label>
                        <input
                            id="nickname"
                            type="text"
                            className={`input ${nicknameError ? 'input-error' : ''}`}
                            value={nickname}
                            onChange={(e) => {
                                setNickname(e.target.value);
                                if (nicknameError) setNicknameError('');
                            }}
                            onBlur={validate}
                            placeholder={t('login.nicknamePlaceholder')}
                            required
                            autoFocus
                        />
                        {nicknameError && <small className="error-text input-error-text">{nicknameError}</small>}
                    </div>

                    <div className="form-group">
                        <label htmlFor="pin">{t('login.pin')}</label>
                        <div className="pin-input-group">
                            <input
                                id="pin"
                                type={showPin ? "text" : "password"}
                                className={`input pin-input ${pinError ? 'input-error' : ''}`}
                                value={pin}
                                onChange={(e) => {
                                    setPin(e.target.value);
                                    if (pinError) setPinError('');
                                }}
                                onBlur={validate}
                                placeholder={t('login.pinPlaceholder')}
                                maxLength={4}
                                pattern="[0-9]{4}"
                                required
                            />
                            <button
                                type="button"
                                onClick={() => setShowPin(!showPin)}
                                aria-label={showPin ? t('login.hidePin') : t('login.showPin')}
                                className="pin-toggle-btn"
                            >
                                {showPin ? '🙈' : '👁️'}
                            </button>
                        </div>
                        {pinError && <small className="error-text input-error-text">{pinError}</small>}
                    </div>

                    {error && <div className="error-message" role="alert" aria-live="assertive">{error}</div>}

                    <button
                        type="submit"
                        className="btn btn-primary btn-block"
                        disabled={loading}
                    >
                        {loading ? t('login.loggingIn') : t('login.loginButton')}
                    </button>
                    <div className="login-family-dash">
                        <button
                            type="button"
                            className="btn btn-secondary btn-block"
                            onClick={() => setShowFamilyDash(true)}
                            title={t('login.familyDashboardHint')}
                        >
                            {t('login.familyDashboard')}
                        </button>
                        <p className="family-dash-hint">
                            {t('login.familyDashboardHint')}
                        </p>
                    </div>

                </form>
            </div>
        </div>
    );
}
