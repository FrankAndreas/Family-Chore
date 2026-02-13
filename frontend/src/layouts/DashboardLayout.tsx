import React from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import type { User } from '../types';
import './DashboardLayout.css';
import { NotificationCenter } from '../components/NotificationCenter';

interface DashboardLayoutProps {
    currentUser: User;
    onLogout: () => void;
}

const DashboardLayout: React.FC<DashboardLayoutProps> = ({ currentUser, onLogout }) => {
    const navigate = useNavigate();
    const location = useLocation();
    const { t } = useTranslation();
    const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);

    // Sidebar Resizing Logic
    const [sidebarWidth, setSidebarWidth] = React.useState(280);
    const [isResizing, setIsResizing] = React.useState(false);

    const startResizing = React.useCallback(() => {
        setIsResizing(true);
    }, []);

    const stopResizing = React.useCallback(() => {
        setIsResizing(false);
    }, []);

    const resize = React.useCallback((mouseMoveEvent: MouseEvent) => {
        if (isResizing) {
            const newWidth = mouseMoveEvent.clientX;
            if (newWidth > 200 && newWidth < 480) { // Min/Max constraints
                setSidebarWidth(newWidth);
            }
        }
    }, [isResizing]);

    React.useEffect(() => {
        window.addEventListener('mousemove', resize);
        window.addEventListener('mouseup', stopResizing);
        return () => {
            window.removeEventListener('mousemove', resize);
            window.removeEventListener('mouseup', stopResizing);
        };
    }, [resize, stopResizing]);

    const isAdmin = currentUser.role.name === 'Admin';

    const isActive = (path: string) => location.pathname === path;

    const handleNavigation = (path: string) => {
        navigate(path);
        setMobileMenuOpen(false);
    };

    return (
        <div className="dashboard-container">
            <aside
                className={`sidebar glass-panel ${mobileMenuOpen ? 'mobile-open' : ''}`}
                style={{ width: mobileMenuOpen ? '100%' : `${sidebarWidth}px` }}
            >
                <div className="sidebar-header">
                    <div className="header-top">
                        <h1 className="app-title">ChoreSpec</h1>
                        <button
                            className="mobile-menu-toggle"
                            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                            aria-label="Toggle menu"
                        >
                            {mobileMenuOpen ? '✕' : '☰'}
                        </button>
                    </div>
                    <div className="user-profile">
                        <div className="avatar">{currentUser.nickname[0]}</div>
                        <div className="user-info">
                            <span className="user-name">{currentUser.nickname}</span>
                            <span className="user-role">{currentUser.role.name}</span>
                        </div>
                        <NotificationCenter />
                    </div>
                </div>
                <nav className={`sidebar-nav ${mobileMenuOpen ? 'show' : ''}`}>
                    {isAdmin && (
                        <>
                            <div className="nav-section-title">{t('navigation.admin')}</div>
                            <button
                                className={`nav-item ${isActive('/admin') ? 'active' : ''}`}
                                onClick={() => handleNavigation('/admin')}
                            >
                                📊 {t('navigation.dashboard')}
                            </button>
                            <button
                                className={`nav-item ${isActive('/admin/users') ? 'active' : ''}`}
                                onClick={() => handleNavigation('/admin/users')}
                            >
                                👥 {t('navigation.users')}
                            </button>
                            <button
                                className={`nav-item ${isActive('/admin/tasks') ? 'active' : ''}`}
                                onClick={() => handleNavigation('/admin/tasks')}
                            >
                                📋 {t('navigation.tasks')}
                            </button>
                            <button
                                className={`nav-item ${isActive('/admin/roles') ? 'active' : ''}`}
                                onClick={() => handleNavigation('/admin/roles')}
                            >
                                ⚙️ {t('navigation.roles')}
                            </button>
                            <button
                                className={`nav-item ${isActive('/analytics') ? 'active' : ''}`}
                                onClick={() => handleNavigation('/analytics')}
                            >
                                📈 {t('analytics.title')}
                            </button>
                        </>
                    )}

                    <div className="nav-section-title">MY CHORES</div>
                    <button
                        className={`nav-item ${isActive('/dashboard') ? 'active' : ''}`}
                        onClick={() => handleNavigation('/dashboard')}
                    >
                        ✅ {t('navigation.tasks')}
                    </button>
                    <button
                        className={`nav-item ${isActive('/rewards') ? 'active' : ''}`}
                        onClick={() => handleNavigation('/rewards')}
                    >
                        🎁 {t('navigation.rewards')}
                    </button>
                    <button
                        className={`nav-item ${isActive('/settings') ? 'active' : ''}`}
                        onClick={() => handleNavigation('/settings')}
                    >
                        🔧 {t('navigation.settings')}
                    </button>

                    <div className="mobile-footer">
                        <div className="points-display">
                            <span className="points-label">{t('common.points')}</span>
                            <span className="points-value">{currentUser.current_points}</span>
                        </div>
                        <button className="btn btn-secondary btn-logout" onClick={onLogout}>
                            {t('navigation.logout')}
                        </button>
                    </div>
                </nav>

                <div className="sidebar-footer desktop-footer">
                    <div className="points-display">
                        <span className="points-label">{t('common.points')}</span>
                        <span className="points-value">{currentUser.current_points}</span>
                    </div>
                    <button className="btn btn-secondary btn-logout" onClick={onLogout}>
                        {t('navigation.logout')}
                    </button>
                </div>

                {/* Resizer Handle */}
                <div
                    className="sidebar-resizer"
                    onMouseDown={startResizing}
                />
            </aside >

            <main className="main-content">
                <Outlet context={{ currentUser }} />
            </main>
        </div >
    );
};

export default DashboardLayout;
