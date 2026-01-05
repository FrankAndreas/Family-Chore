import React, { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import { getUserDailyTasks, completeTask, getTasks } from '../../api';
import type { TaskInstance, Task, User } from '../../types';
import LoadingSpinner from '../../components/LoadingSpinner';
import Toast from '../../components/Toast';
import { useToast } from '../../hooks/useToast';
import '../admin/Dashboard.css';

interface DashboardContext {
    currentUser: User;
}

// Extended TaskInstance with task details
interface TaskInstanceWithDetails extends TaskInstance {
    taskDetails?: Task;
}

const UserDashboard: React.FC = () => {
    const { currentUser } = useOutletContext<DashboardContext>();
    const [tasks, setTasks] = useState<TaskInstanceWithDetails[]>([]);
    const [loading, setLoading] = useState(true);
    const [completingId, setCompletingId] = useState<number | null>(null);
    const { toasts, removeToast, success, error: showError } = useToast();

    useEffect(() => {
        if (currentUser) {
            fetchData();
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [currentUser]);

    const fetchData = async () => {
        try {
            // Fetch both task instances and task templates
            const [instancesRes, templatesRes] = await Promise.all([
                getUserDailyTasks(currentUser.id),
                getTasks()
            ]);

            const instances: TaskInstance[] = instancesRes.data;
            const templates: Task[] = templatesRes.data;


            // Merge instances with their task details
            const instancesWithDetails = instances.map(instance => ({
                ...instance,
                taskDetails: templates.find(t => t.id === instance.task_id)
            }));

            setTasks(instancesWithDetails);
        } catch (err) {
            console.error('Failed to fetch tasks', err);
            showError('Failed to load tasks. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleComplete = async (instanceId: number) => {
        setCompletingId(instanceId);
        try {
            await completeTask(instanceId);
            success('Task completed! Points awarded. 🎉');
            fetchData(); // Refresh list to show updated status
        } catch (err) {
            console.error('Failed to complete task', err);
            showError('Failed to complete task. Please try again.');
        } finally {
            setCompletingId(null);
        }
    };

    if (loading) return <LoadingSpinner fullPage message="Loading your tasks..." />;

    const pendingTasks = tasks.filter(t => t.status === 'PENDING');
    const completedTasks = tasks.filter(t => t.status === 'COMPLETED');

    return (
        <div className="page-container fade-in">
            {/* Toast notifications */}
            <div className="toast-container">
                {toasts.map(toast => (
                    <Toast
                        key={toast.id}
                        message={toast.message}
                        type={toast.type}
                        duration={toast.duration}
                        onClose={() => removeToast(toast.id)}
                    />
                ))}
            </div>

            <header className="page-header">
                <h1 className="page-title">My Daily Tasks</h1>
                <p className="page-subtitle">Complete your chores to earn points!</p>
            </header>

            <div className="dashboard-sections">
                <div className="section glass-panel">
                    <h2>📅 Today's To-Do</h2>

                    {pendingTasks.length === 0 && (
                        <div className="empty-state">
                            <p>No pending tasks for today. Great job! 🌟</p>
                        </div>
                    )}

                    <div className="tasks-list">
                        {pendingTasks.map(instance => {
                            const task = instance.taskDetails;
                            const calculatedPoints = task ? Math.round(task.base_points * currentUser.role.multiplier_value) : 0;

                            return (
                                <div key={instance.id} className="task-item-card">
                                    <div className="task-item-content">
                                        <h3>{task?.name || `Task #${instance.task_id}`}</h3>
                                        <p className="task-description">{task?.description || 'No description'}</p>
                                        <div className="task-meta-info">
                                            <span className="due-time">
                                                🕒 Due: {new Date(instance.due_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                            </span>
                                            <span className="points-earn">
                                                💰 {calculatedPoints} points
                                            </span>
                                        </div>
                                    </div>
                                    <button
                                        className="btn btn-primary"
                                        onClick={() => handleComplete(instance.id)}
                                        disabled={completingId === instance.id}
                                    >
                                        {completingId === instance.id ? 'Completing...' : 'Mark Complete'}
                                    </button>
                                </div>
                            );
                        })}
                    </div>
                </div>

                <div className="section glass-panel">
                    <h2>✅ Completed Today</h2>

                    {completedTasks.length === 0 && (
                        <div className="empty-state">
                            <p>You haven't completed any tasks yet today.</p>
                        </div>
                    )}

                    <div className="tasks-list">
                        {completedTasks.map(instance => {
                            const task = instance.taskDetails;
                            const calculatedPoints = task ? Math.round(task.base_points * currentUser.role.multiplier_value) : 0;

                            return (
                                <div key={instance.id} className="task-item-card completed">
                                    <div className="task-item-content">
                                        <h3>{task?.name || `Task #${instance.task_id}`}</h3>
                                        <p className="task-description">{task?.description || 'No description'}</p>
                                        <div className="task-meta-info">
                                            <span className="completed-time">
                                                ✓ Done at: {instance.completed_at ? new Date(instance.completed_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '-'}
                                            </span>
                                            <span className="points-earned">
                                                +{calculatedPoints} pts
                                            </span>
                                        </div>
                                    </div>
                                    <div className="status-badge">Done ✓</div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default UserDashboard;
