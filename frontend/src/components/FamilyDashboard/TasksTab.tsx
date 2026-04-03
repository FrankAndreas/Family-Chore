import React from 'react';
import { useTranslation } from 'react-i18next';
import type { TaskInstance, User } from '../../types';

export interface TasksTabProps {
    users: User[];
    groupedTasks: Record<number, TaskInstance[]>;
    unknownTasks: TaskInstance[];
    tasks: TaskInstance[];
    collapsedUsers: Set<number>;
    setCollapsedUsers: React.Dispatch<React.SetStateAction<Set<number>>>;
    handleCompleteClick: (task: TaskInstance) => void;
}

export default function TasksTab({
    users,
    groupedTasks,
    unknownTasks,
    tasks,
    collapsedUsers,
    setCollapsedUsers,
    handleCompleteClick,
}: TasksTabProps) {
    const { t } = useTranslation();

    return (
        <div className="tab-content fade-in">
            {users.map(user => {
                const userTasks = groupedTasks[user.id] || [];
                if (userTasks.length === 0) return null;
                const isCollapsed = collapsedUsers.has(user.id);

                return (
                    <div key={user.id} className="user-group">
                        <button
                            className="user-group-toggle user-group-header"
                            onClick={() => {
                                setCollapsedUsers(prev => {
                                    const next = new Set(prev);
                                    if (next.has(user.id)) {
                                        next.delete(user.id);
                                    } else {
                                        next.add(user.id);
                                    }
                                    return next;
                                });
                            }}
                            aria-expanded={!isCollapsed}
                            aria-controls={`user-tasks-${user.id}`}
                        >
                            <span
                                className={`collapse-chevron ${isCollapsed ? 'is-collapsed' : ''}`}
                                aria-hidden="true"
                            >
                                ▾
                            </span>
                            <h3 className="user-group-name">
                                {user.nickname}
                                <span className="user-group-count">
                                    ({userTasks.length})
                                </span>
                            </h3>
                        </button>
                        {!isCollapsed && (
                            <div className="tasks-grid" id={`user-tasks-${user.id}`}>
                                {userTasks.map(instance => (
                                    <div key={instance.id} className="task-card glass-card">
                                        <div>
                                            <h4>{instance.task?.name || `Task #${instance.task_id}`}</h4>
                                            <p className="task-desc">{instance.task?.description}</p>
                                            <div className="task-info">
                                                <span className="task-points">💎 {instance.task?.base_points} {t('common.pts', 'pts')}</span>
                                                <span>📅 {instance.due_time.split('T')[0]}</span>
                                            </div>
                                        </div>
                                        <button
                                            className="btn btn-primary btn-complete"
                                            onClick={() => handleCompleteClick(instance)}
                                        >
                                            {t('dashboard.doneAction', '✅ Done')}
                                        </button>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                );
            })}

            {unknownTasks.length > 0 && (
                <div className="user-group">
                    <h3>{t('dashboard.unassignedOther', 'Unassigned / Other')}</h3>
                    <div className="tasks-grid">
                        {unknownTasks.map(instance => (
                            <div key={instance.id} className="task-card glass-card">
                                <div>
                                    <h4>{instance.task?.name || `Task #${instance.task_id}`}</h4>
                                    <p className="task-desc">{instance.task?.description}</p>
                                    <div className="task-info">
                                        <span className="task-points">💎 {instance.task?.base_points} {t('common.pts')}</span>
                                        <span>📅 {instance.due_time.split('T')[0]}</span>
                                    </div>
                                </div>
                                <button
                                    className="btn btn-primary"
                                    onClick={() => handleCompleteClick(instance)}
                                >
                                    {t('dashboard.done', 'Done')}
                                </button>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {tasks.length === 0 && (
                <div className="empty-state">
                    <div className="empty-state-icon">🎉</div>
                    <h3>{t('dashboard.allCaughtUpTitle')}</h3>
                    <p>{t('tasks.noPendingTasks')}</p>
                </div>
            )}
        </div>
    );
}
