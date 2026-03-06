import React from 'react';
import './SkeletonLoader.css';

interface SkeletonLoaderProps {
    type?: 'card' | 'text' | 'avatar' | 'title' | 'stat';
    count?: number;
    className?: string;
    style?: React.CSSProperties;
}

export const SkeletonLoader: React.FC<SkeletonLoaderProps> = ({ type = 'text', count = 1, className = '', style }) => {
    const renderSkeleton = (i: number) => {
        switch (type) {
            case 'card':
                return (
                    <div key={i} className={`skeleton-item skeleton-card ${className}`} style={style}>
                        <div className="skeleton-title" style={{ width: '40%' }}></div>
                        <div className="skeleton-text"></div>
                        <div className="skeleton-text" style={{ width: '80%' }}></div>
                    </div>
                );
            case 'stat':
                return (
                    <div key={i} className={`skeleton-item skeleton-stat ${className}`} style={style}>
                        <div className="skeleton-avatar"></div>
                        <div style={{ flex: 1 }}>
                            <div className="skeleton-title" style={{ width: '30%' }}></div>
                            <div className="skeleton-title" style={{ width: '50%', height: '2rem', marginTop: '0.5rem' }}></div>
                        </div>
                    </div>
                );
            case 'avatar':
                return <div key={i} className={`skeleton-item skeleton-avatar ${className}`} style={style}></div>;
            case 'title':
                return <div key={i} className={`skeleton-item skeleton-title ${className}`} style={style}></div>;
            case 'text':
            default:
                return <div key={i} className={`skeleton-item skeleton-text ${className}`} style={style}></div>;
        }
    };

    return (
        <div className="skeleton-wrapper" aria-hidden="true" data-testid="skeleton-loader">
            {Array.from({ length: count }, (_, i) => renderSkeleton(i))}
        </div>
    );
};
