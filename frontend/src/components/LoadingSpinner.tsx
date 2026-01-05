import React from 'react';
import './LoadingSpinner.css';

interface LoadingSpinnerProps {
    size?: 'small' | 'medium' | 'large';
    message?: string;
    fullPage?: boolean;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
    size = 'medium',
    message,
    fullPage = false
}) => {
    const content = (
        <div className={`loading-spinner-content size-${size}`}>
            <div className="spinner"></div>
            {message && <p className="loading-message">{message}</p>}
        </div>
    );

    if (fullPage) {
        return (
            <div className="loading-spinner-overlay">
                {content}
            </div>
        );
    }

    return content;
};

export default LoadingSpinner;
