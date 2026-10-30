import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';

interface NoAccessProps {
    // The family hub (or the NAS) doesn't answer, rather than "not given this app"
    hubDown: boolean;
    onRetry: () => void;
    onLogout: () => void;
}

// Logged in at the family hub, but the chores app isn't ticked for this person; or the hub doesn't answer
export default function NoAccess({ hubDown, onRetry, onLogout }: NoAccessProps) {
    const { t } = useTranslation();
    return (
        <div className="page-container fade-in" style={{ maxWidth: '32rem', paddingTop: '3rem' }}>
            <div className="glass-panel" style={{ padding: '1.5rem' }}>
                <h1 className="page-title">{hubDown ? t('access.hubDownTitle') : t('access.noAccessTitle')}</h1>
                <p className="text-secondary mb-3">{hubDown ? t('access.hubDown') : t('access.noAccess')}</p>
                {hubDown ? (
                    <button type="button" className="btn btn-primary" onClick={onRetry}>{t('access.retry')}</button>
                ) : (
                    <button type="button" className="btn btn-primary" onClick={onLogout}>{t('access.otherPerson')}</button>
                )}
                <p className="mt-3">
                    <Link to="/family-dashboard">{t('login.familyDashboard')}</Link>
                </p>
            </div>
        </div>
    );
}
