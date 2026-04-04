import { useTranslation } from 'react-i18next';
import Modal from '../Modal';
import type { User } from '../../types';

export interface ClaimModalProps {
    taskName: string;
    users: User[];
    onSelectUser: (userId: number) => void;
    onClose: () => void;
}

export default function ClaimModal({ taskName, users, onSelectUser, onClose }: ClaimModalProps) {
    const { t } = useTranslation();
    return (
        <Modal isOpen={true} onClose={onClose} title={t('dashboard.whoDidIt')}>
            <p>{t('dashboard.completing')} <strong>{taskName}</strong></p>

            <div className="user-grid">
                {users.map(user => (
                    <button
                        key={user.id}
                        className="user-select-card"
                        onClick={() => onSelectUser(user.id)}
                    >
                        <div className="user-avatar" aria-hidden="true">
                            {user.nickname.charAt(0).toUpperCase()}
                        </div>
                        <div className="user-name">{user.nickname}</div>
                    </button>
                ))}
            </div>

            <button className="btn btn-secondary modal-close-btn" onClick={onClose}>
                {t('common.cancel')}
            </button>
        </Modal>
    );
}
