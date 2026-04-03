import { useTranslation } from 'react-i18next';
import type { Task, Role } from '../../../types';
import TaskCard from './TaskCard';

interface TaskRoleGroupProps {
    title: string;
    titleColor: string;
    titleEmoji: string;
    badgeBackground: string;
    tasks: Task[];
    roles: Role[];
    subtitle?: string;
    getScheduleInfo: (type: string) => { icon: string; label: string; color: string };
    onEdit: (task: Task) => void;
    onCopy: (task: Task) => void;
    onDelete: (task: Task) => void;
}

export default function TaskRoleGroup({
    title,
    titleColor,
    titleEmoji,
    badgeBackground,
    tasks,
    roles,
    subtitle,
    getScheduleInfo,
    onEdit,
    onCopy,
    onDelete,
}: TaskRoleGroupProps) {
    const { t } = useTranslation();

    if (tasks.length === 0) return null;

    return (
        <div className="role-group" style={{ marginBottom: '2rem' }}>
            <h3 style={{
                color: titleColor,
                marginBottom: '1rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem'
            }}>
                {titleEmoji} {title}
                <span style={{
                    background: badgeBackground,
                    padding: '0.25rem 0.75rem',
                    borderRadius: '12px',
                    fontSize: '0.875rem'
                }}>
                    {tasks.length} {t('common.tasks', 'tasks')}{subtitle ? ` • ${subtitle}` : ''}
                </span>
            </h3>
            <div className="tasks-grid">
                {tasks.map(task => (
                    <TaskCard
                        key={task.id}
                        task={task}
                        roles={roles}
                        getScheduleInfo={getScheduleInfo}
                        onEdit={onEdit}
                        onCopy={onCopy}
                        onDelete={onDelete}
                    />
                ))}
            </div>
        </div>
    );
}
