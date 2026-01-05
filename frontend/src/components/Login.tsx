import { useState } from 'react';
import { login } from '../api';
import type { User } from '../types';
import './Login.css';

interface LoginProps {
    onLogin: (user: User) => void;
}

export default function Login({ onLogin }: LoginProps) {
    const [nickname, setNickname] = useState('');
    const [pin, setPin] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const response = await login(nickname, pin);
            onLogin(response.data);
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Login failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="login-container">
            <div className="login-card glass-card">
                <div className="login-header">
                    <h1 className="login-title">🎮 ChoreSpec</h1>
                    <p className="login-subtitle">Transform chores into achievements</p>
                </div>

                <form onSubmit={handleSubmit} className="login-form">
                    <div className="form-group">
                        <label htmlFor="nickname">Nickname</label>
                        <input
                            id="nickname"
                            type="text"
                            className="input"
                            value={nickname}
                            onChange={(e) => setNickname(e.target.value)}
                            placeholder="Enter your nickname"
                            required
                            autoFocus
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="pin">PIN</label>
                        <input
                            id="pin"
                            type="password"
                            className="input"
                            value={pin}
                            onChange={(e) => setPin(e.target.value)}
                            placeholder="4-digit PIN"
                            maxLength={4}
                            pattern="[0-9]{4}"
                            required
                        />
                    </div>

                    {error && <div className="error-message">{error}</div>}

                    <button
                        type="submit"
                        className="btn btn-primary btn-block"
                        disabled={loading}
                    >
                        {loading ? 'Logging in...' : 'Login'}
                    </button>
                </form>

                <div className="login-footer">
                    <p className="text-muted text-center">
                        Default Admin: nickname "Admin", PIN "1234"
                    </p>
                </div>
            </div>
        </div>
    );
}
