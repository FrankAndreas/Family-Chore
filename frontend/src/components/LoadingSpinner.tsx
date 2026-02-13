import React from 'react';

interface LoadingSpinnerProps {
    fullPage?: boolean;
    message?: string;
    size?: 'sm' | 'md' | 'lg';
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
    fullPage = false,
    message = 'Loading...',
    size = 'md'
}) => {
    const sizeClasses = {
        sm: 'w-5 h-5 border-2',
        md: 'w-10 h-10 border-4',
        lg: 'w-16 h-16 border-4'
    };

    const spinner = (
        <div className="flex flex-col items-center gap-4">
            <div
                className={`
                    ${sizeClasses[size]} 
                    rounded-full 
                    border-indigo-200 
                    border-t-indigo-600 
                    animate-spin 
                    ease-in-out
                `}
                role="status"
                aria-label="loading"
            />
            {message && (
                <p className="text-gray-500 font-medium animate-pulse">
                    {message}
                </p>
            )}
        </div>
    );

    if (fullPage) {
        return (
            <div className="fixed inset-0 bg-white/50 backdrop-blur-sm z-50 flex items-center justify-center">
                {spinner}
            </div>
        );
    }

    return (
        <div className="flex items-center justify-center p-4">
            {spinner}
        </div>
    );
};

export default LoadingSpinner;
