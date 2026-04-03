import { useTranslation } from 'react-i18next';
import type { Task, Role } from '../../../types';

interface TaskCardProps {
    task: Task;
    roles: Role[];
    getScheduleInfo: (type: string) => { icon: string; label: string; color: string };
    onEdit: (task: Task) => void;
    onCopy: (task: Task) => void;
    onDelete: (task: Task) => void;
}

export default function TaskCard({ task, roles, getScheduleInfo, onEdit, onCopy, onDelete }: TaskCardProps) {
    const { t } = useTranslation();
    const role = task.assigned_role_id ? roles.find(r => r.id === task.assigned_role_id) : null;
    const assignedTo = role ? role.name : `🏠 ${t('tasks.allFamilyMembers', 'All Family Members')}`;
    const scheduleInfo = getScheduleInfo(task.schedule_type);

    return (
        <div className="task-card glass-panel">
            <div className="task-header">
                <div className="task-icon">{scheduleInfo.icon}</div>
                <div className="task-info">
                    <h3>{task.name}</h3>
                    <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginTop: '0.25rem' }}>
                        <span className="role-badge">{assignedTo}</span>
                        <span
                            className="schedule-badge"
                            style={{
                                background: `linear-gradient(135deg, ${scheduleInfo.color}22, ${scheduleInfo.color}11)`,
                                border: `1px solid ${scheduleInfo.color}44`,
                                color: scheduleInfo.color,
                                padding: '0.125rem 0.5rem',
                                borderRadius: '12px',
                                fontSize: '0.75rem',
                                fontWeight: '600'
                            }}
                        >
                            {scheduleInfo.icon} {scheduleInfo.label}
                        </span>
                    </div>
                </div>
                <div className="task-points">
                    <span className="points-value">{task.base_points}</span>
                    <span className="points-label">{t('common.pts', 'pts')}</span>
                </div>
            </div>
            <p className="task-description">{task.description}</p>
            <div className="task-footer">
                <div className="task-meta">
                    {task.schedule_type === 'daily' && (
                        <span>🕒 {t('tasks.dueAt', 'Due at')} {task.default_due_time}</span>
                    )}
                    {task.schedule_type === 'weekly' && (
                        <span>📅 {t('tasks.every', 'Every')} {task.default_due_time}</span>
                    )}
                    {task.schedule_type === 'recurring' && (
                        <span>⏳ {t('tasks.cooldown', 'Cooldown')}: {task.recurrence_min_days}-{task.recurrence_max_days} {t('common.days', 'days')}</span>
                    )}
                </div>
                <div className="task-actions" style={{ display: 'flex', gap: '0.5rem', marginLeft: 'auto' }}>
                    <button
                        className="btn btn-ghost btn-sm"
                        onClick={() => onCopy(task)}
                        title={t('tasks.copyTask', 'Copy Task')}
                    >
                        📋
                    </button>
                    <button
                        className="btn btn-ghost btn-sm"
                        onClick={() => onDelete(task)}
                        title={t('tasks.deleteTask', 'Delete Task')}
                        style={{ color: '#ef4444' }}
                    >
                        🗑️
                    </button>
                    <button
                        className="btn btn-secondary btn-sm"
                        onClick={() => onEdit(task)}
                    >
                        ✏️ {t('common.edit', 'Edit')}
                    </button>
                </div>
            </div>
        </div>
    );
}
