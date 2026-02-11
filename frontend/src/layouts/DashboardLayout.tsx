import React from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import type { User } from '../types';
import './DashboardLayout.css';

interface DashboardLayoutProps {
    currentUser: User;
    onLogout: () => void;
}

const DashboardLayout: React.FC<DashboardLayoutProps> = ({ currentUser, onLogout }) => {
    const navigate = useNavigate();
    const location = useLocation();
    const { t } = useTranslation();

    const isAdmin = currentUser.role.name === 'Admin';

    const isActive = (path: string) => location.pathname === path;

    return (
        <div className="dashboard-container">
            <aside className="sidebar glass-panel">
                <div className="sidebar-header">
                    <h1 className="app-title">ChoreSpec</h1>
                    <div className="user-profile">
                        <div className="avatar">{currentUser.nickname[0]}</div>
                        <div className="user-info">
                            <span className="user-name">{currentUser.nickname}</span>
                            <span className="user-role">{currentUser.role.name}</span>
                        </div>
                    </div>
                </div>

                <nav className="sidebar-nav">
                    {isAdmin && (
                        <>
                            <div className="nav-section-title">{t('navigation.admin')}</div>
                            <button
                                className={`nav-item ${isActive('/admin') ? 'active' : ''}`}
                                onClick={() => navigate('/admin')}
                            >
                                📊 {t('navigation.dashboard')}
                            </button>
                            <button
                                className={`nav-item ${isActive('/admin/users') ? 'active' : ''}`}
                                onClick={() => navigate('/admin/users')}
                            >
                                👥 {t('navigation.users')}
                            </button>
                            <button
                                className={`nav-item ${isActive('/admin/tasks') ? 'active' : ''}`}
                                onClick={() => navigate('/admin/tasks')}
                            >
                                📋 {t('navigation.tasks')}
                            </button>
                            <button
                                className={`nav-item ${isActive('/admin/roles') ? 'active' : ''}`}
                                onClick={() => navigate('/admin/roles')}
                            >
                                ⚙️ {t('navigation.roles')}
                            </button>
                            <button
                                className={`nav-item ${isActive('/analytics') ? 'active' : ''}`}
                                onClick={() => navigate('/analytics')}
                            >
                                📈 {t('analytics.title')}
                            </button>
                        </>
                    )}

                    <div className="nav-section-title">MY CHORES</div>
                    <button
                        className={`nav-item ${isActive('/dashboard') ? 'active' : ''}`}
                        onClick={() => navigate('/dashboard')}
                    >
                        ✅ {t('navigation.tasks')}
                    </button>
                    <button
                        className={`nav-item ${isActive('/rewards') ? 'active' : ''}`}
                        onClick={() => navigate('/rewards')}
                    >
                        🎁 {t('navigation.rewards')}
                    </button>
                    <button
                        className={`nav-item ${isActive('/settings') ? 'active' : ''}`}
                        onClick={() => navigate('/settings')}
                    >
                        🔧 {t('navigation.settings')}
                    </button>
                </nav>

                <div className="sidebar-footer">
                    <div className="points-display">
                        <span className="points-label">{t('common.points')}</span>
                        <span className="points-value">{currentUser.current_points}</span>
                    </div>
                    <button className="btn btn-secondary btn-logout" onClick={onLogout}>
                        {t('navigation.logout')}
                    </button>
                </div>
            </aside>

            <main className="main-content">
                <Outlet context={{ currentUser }} />
            </main>
        </div>
    );
};

export default DashboardLayout;
