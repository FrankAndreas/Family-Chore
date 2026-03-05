import React, { useEffect } from 'react';
import './Toast.css';

export type ToastType = 'success' | 'error' | 'info' | 'warning';

interface ToastProps {
    message: string;
    type?: ToastType;
    duration?: number;
    onClose: () => void;
}

const Toast: React.FC<ToastProps> = ({
    message,
    type = 'info',
    duration = 3000,
    onClose
}) => {
    useEffect(() => {
        if (duration > 0) {
            const timer = setTimeout(() => {
                onClose();
            }, duration);

            return () => clearTimeout(timer);
        }
    }, [duration, onClose]);

    const getIcon = () => {
        switch (type) {
            case 'success': return '✅';
            case 'error': return '❌';
            case 'warning': return '⚠️';
            case 'info': return 'ℹ️';
            default: return 'ℹ️';
        }
    };

    const ariaRole = type === 'error' || type === 'warning' ? 'alert' : 'status';
    const ariaLive = type === 'error' || type === 'warning' ? 'assertive' : 'polite';

    return (
        <div className={`toast toast-${type} fade-in`} role={ariaRole} aria-live={ariaLive}>
            <span className="toast-icon" aria-hidden="true">{getIcon()}</span>
            <span className="toast-message">{message}</span>
            <button className="toast-close" onClick={onClose} aria-label="Close">
                ✕
            </button>
        </div>
    );
};

export default Toast;
