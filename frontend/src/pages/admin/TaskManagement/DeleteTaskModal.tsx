import { useTranslation } from 'react-i18next';
import Modal from '../../../components/Modal';
import type { Task } from '../../../types';

interface DeleteTaskModalProps {
    task: Task | null;
    onClose: () => void;
    onConfirm: (task: Task) => Promise<void>;
}

export default function DeleteTaskModal({ task, onClose, onConfirm }: DeleteTaskModalProps) {
    const { t } = useTranslation();

    return (
        <Modal
            isOpen={!!task}
            onClose={onClose}
            title={t('tasks.confirmDeletion', 'Confirm Deletion')}
        >
            <div>
                <p style={{ color: '#333' }}>
                    {t('tasks.deleteConfirmMessage', {
                        defaultValue: `Are you sure you want to delete "${task?.name}"?`,
                        name: task?.name
                    })}
                </p>
                <p style={{ color: '#c53030', marginTop: '0.5rem', fontSize: '0.9rem' }}>
                    {t('tasks.deleteWarning', 'This will also delete all related task instances and cannot be undone.')}
                </p>
                <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem', justifyContent: 'flex-end' }}>
                    <button className="btn btn-secondary" onClick={onClose}>
                        {t('common.cancel', 'Cancel')}
                    </button>
                    <button
                        className="btn"
                        style={{ backgroundColor: '#ef4444', color: 'white' }}
                        onClick={() => task && onConfirm(task)}
                    >
                        {t('tasks.deleteTaskButton', 'Delete Task')}
                    </button>
                </div>
            </div>
        </Modal>
    );
}
