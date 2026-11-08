import React, { useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { UserContext } from '../context/UserContext';
import './NotFoundPage.css';

const NotFoundPage: React.FC = () => {
    const { t } = useTranslation();
    const navigate = useNavigate();
    // The app's user, not the dashboard layout's: an unknown address shows this page outside the layout (it crashed
    // there, reading the layout's context)
    const currentUser = useContext(UserContext)?.currentUser;

    const goHome = () => {
        if (currentUser?.role?.name === 'Admin') {
            navigate('/admin');
        } else {
            navigate('/dashboard');
        }
    };

    return (
        <main className="page-container fade-in not-found-page">
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
        </main>
    );
};

export default NotFoundPage;
