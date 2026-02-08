import React, { useState, useEffect, useCallback } from 'react';
import { useOutletContext } from 'react-router-dom';
import { getUserDailyTasks, completeTask, getTasks, getUserTransactions } from '../../api';
import type { TaskInstance, Task, User, Transaction, TransactionFilters } from '../../types';
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
    const [transactions, setTransactions] = useState<Transaction[]>([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<'tasks' | 'history'>('tasks');
    const [completingId, setCompletingId] = useState<number | null>(null);
    const { toasts, removeToast, success, error: showError } = useToast();

    const [filters, setFilters] = useState<TransactionFilters>({});

    const fetchData = useCallback(async () => {
        setLoading(true);

        try {
            if (activeTab === 'tasks') {
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
            } else if (activeTab === 'history') {
                const transactionsRes = await getUserTransactions(currentUser.id, { limit: 50, ...filters });
                setTransactions(transactionsRes.data);
            }
        } catch (err) {
            console.error('Failed to fetch data', err);
            showError('Failed to load dashboard data. Please try again.');
        } finally {
            setLoading(false);
        }
    }, [currentUser.id, activeTab, filters, showError]);

    useEffect(() => {
        if (currentUser) {
            fetchData();
        }
    }, [fetchData, currentUser]);

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

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' });
    };

    if (!currentUser) return <LoadingSpinner fullPage message="Loading..." />;

    const pendingTasks = tasks.filter(t => t.status === 'PENDING');
    // const completedTasks = tasks.filter(t => t.status === 'COMPLETED'); // Keep logic for now but unused

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
                <h1 className="page-title">My Dashboard</h1>
                <p className="page-subtitle">Welcome, <span className="highlight-text">{currentUser.nickname}</span>! You have {currentUser.current_points} points.</p>
            </header>

            <div className="tabs">
                <button
                    className={`tab-btn ${activeTab === 'tasks' ? 'active' : ''}`}
                    onClick={() => setActiveTab('tasks')}
                >
                    📝 My Tasks
                </button>
                <button
                    className={`tab-btn ${activeTab === 'history' ? 'active' : ''}`}
                    onClick={() => setActiveTab('history')}
                >
                    📜 History
                </button>
            </div>

            {loading ? (
                <LoadingSpinner message={activeTab === 'tasks' ? "Loading tasks..." : "Loading history..."} />
            ) : (
                <div className="dashboard-content">
                    {activeTab === 'tasks' && (
                        <div className="dashboard-sections">
                            <div className="section glass-panel">
                                <h2>📅 Today's To-Do</h2>
                                {pendingTasks.length === 0 ? (
                                    <div className="empty-state">
                                        <p>No pending tasks for today. Great job! 🌟</p>
                                    </div>
                                ) : (
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
                                )}
                            </div>
                        </div>
                    )}

                    {activeTab === 'history' && (
                        <div className="section glass-panel full-width">
                            <h2>📜 Transaction History</h2>

                            {/* Filters */}
                            <div className="filters-bar">
                                <select
                                    onChange={(e) => setFilters((prev: TransactionFilters) => ({ ...prev, type: e.target.value as 'EARN' | 'REDEEM' | undefined || undefined }))}
                                    className="filter-select"
                                    value={filters.type || ''}
                                >
                                    <option value="">All Activity</option>
                                    <option value="EARN">Earned</option>
                                    <option value="REDEEM">Redeemed</option>
                                </select>

                                <input
                                    type="text"
                                    placeholder="Search description..."
                                    onChange={(e) => setFilters((prev: TransactionFilters) => ({ ...prev, search: e.target.value || undefined }))}
                                    className="filter-input"
                                    value={filters.search || ''}
                                />
                            </div>

                            {transactions.length === 0 ? (
                                <div className="empty-state">
                                    <p>No transactions found matching your filters.</p>
                                </div>
                            ) : (
                                <div className="transaction-list table-container">
                                    <table className="data-table">
                                        <thead>
                                            <tr>
                                                <th>Date</th>
                                                <th>Type</th>
                                                <th>Points</th>
                                                <th>Details</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {transactions.map(tx => (
                                                <tr key={tx.id}>
                                                    <td>{formatDate(tx.timestamp)}</td>
                                                    <td>
                                                        <span className={`badge ${tx.type === 'EARN' ? 'badge-success' : 'badge-warning'}`}>
                                                            {tx.type}
                                                        </span>
                                                    </td>
                                                    <td className={tx.awarded_points >= 0 ? 'text-success' : 'text-danger'}>
                                                        {tx.awarded_points > 0 ? '+' : ''}{tx.awarded_points}
                                                    </td>
                                                    <td>
                                                        {tx.description || (tx.type === 'EARN' ? 'Completed task' : 'Redeemed reward')}
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default UserDashboard;

