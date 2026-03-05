import React from 'react';
import { useNavigate, useOutletContext } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import type { User } from '../types';
import './NotFoundPage.css';

interface DashboardContext {
    currentUser: User;
}

const NotFoundPage: React.FC = () => {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const { currentUser } = useOutletContext<DashboardContext>();

    const goHome = () => {
        if (currentUser?.role?.name === 'Admin') {
            navigate('/admin');
        } else {
            navigate('/dashboard');
        }
    };

    return (
        <div className="page-container fade-in not-found-page">
            <div className="glass-panel not-found-content">
                <div className="not-found-icon" aria-hidden="true">🗺️</div>
                <h1 className="page-title">{t('common.not_found_title', '404 - Page Not Found')}</h1>
                <p className="page-subtitle">
                    {t('common.not_found_desc', "Oops! It looks like you've wandered off the map. This page doesn't exist.")}
                </p>
                <div style={{ marginTop: '30px' }}>
                    <button className="btn btn-primary" onClick={goHome}>
                        {t('common.back_to_home', 'Take Me Home 🏠')}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default NotFoundPage;
