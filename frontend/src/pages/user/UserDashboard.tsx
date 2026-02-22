import React, { useState, useEffect, useCallback } from 'react';
import { useOutletContext } from 'react-router-dom';
import { getUserDailyTasks, completeTask, getTasks, getUserTransactions, uploadTaskPhoto, updateUser } from '../../api';
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
    const [activeTab, setActiveTab] = useState<'tasks' | 'history' | 'settings'>('tasks');
    const [completingId, setCompletingId] = useState<number | null>(null);
    const [photoUrls, setPhotoUrls] = useState<Record<number, File | null>>({});
    const [email, setEmail] = useState('');
    const [notificationsEnabled, setNotificationsEnabled] = useState(true);
    const [isSavingSettings, setIsSavingSettings] = useState(false);
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
                // Only show PENDING or IN_REVIEW tasks on the dashboard actively
                setTasks(instancesWithDetails.filter(t => t.status === 'PENDING' || t.status === 'IN_REVIEW'));
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
            setEmail(currentUser.email || '');
            setNotificationsEnabled(currentUser.notifications_enabled ?? true);
            fetchData();
        }
    }, [fetchData, currentUser]);

    const handleSaveSettings = async () => {
        setIsSavingSettings(true);
        try {
            await updateUser(currentUser.id, {
                email: email || null,
                notifications_enabled: notificationsEnabled
            });
            success('Settings saved successfully!');
            // To be robust, we could reload currentUser info or rely on parent updates
        } catch (err) {
            console.error('Failed to save settings', err);
            showError('Failed to save settings. Please try again.');
        } finally {
            setIsSavingSettings(false);
        }
    };

    const handleComplete = async (instance: TaskInstanceWithDetails) => {
        setCompletingId(instance.id);
        try {
            const task = instance.taskDetails;
            if (task?.requires_photo_verification && !photoUrls[instance.id] && instance.status !== 'IN_REVIEW') {
                showError('Please provide a photo URL for this task.');
                setCompletingId(null);
                return;
            }

            if (task?.requires_photo_verification && photoUrls[instance.id] && instance.status !== 'IN_REVIEW') {
                // First upload photo, then call completeTask
                await uploadTaskPhoto(instance.id, photoUrls[instance.id]!);
            }

            const res = await completeTask(instance.id);
            if (res.data.status === 'IN_REVIEW') {
                success('Task submitted for review! 📸');
                setPhotoUrls(prev => { const next = { ...prev }; delete next[instance.id]; return next; });
            } else {
                success('Task completed! Points awarded. 🎉');
            }
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
                <div className="gamification-badges" style={{ display: 'flex', gap: '10px', marginTop: '10px', justifyContent: 'center' }}>
                    {currentUser.current_streak > 0 && (
                        <span className="badge badge-warning" style={{ fontSize: '1.1em', padding: '5px 10px' }}>
                            🔥 {currentUser.current_streak} Day Streak!
                        </span>
                    )}
                    {currentUser.last_task_date !== new Date().toISOString().split('T')[0] && (
                        <span className="badge badge-success" style={{ fontSize: '1.1em', padding: '5px 10px' }}>
                            🎁 +5 Daily Bonus Available!
                        </span>
                    )}
                </div>
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
                <button
                    className={`tab-btn ${activeTab === 'settings' ? 'active' : ''}`}
                    onClick={() => setActiveTab('settings')}
                >
                    ⚙️ Settings
                </button>
            </div>

            {loading ? (
                <LoadingSpinner message={activeTab === 'tasks' ? "Loading tasks..." : activeTab === 'history' ? "Loading history..." : "Loading settings..."} />
            ) : (
                <div className="dashboard-content">
                    {activeTab === 'tasks' && (
                        <div className="dashboard-sections">
                            <div className="section glass-panel">
                                <h2>📅 Today's To-Do</h2>
                                {tasks.length === 0 ? (
                                    <div className="empty-state">
                                        <div className="empty-state-icon">🏖️</div>
                                        <h3>You're All Caught Up!</h3>
                                        <p>No pending tasks for today. Enjoy your free time or check back later! 🌟</p>
                                    </div>
                                ) : (
                                    <div className="tasks-list">
                                        {tasks.map(instance => {
                                            const task = instance.taskDetails;
                                            const calculatedPoints = task ? Math.round(task.base_points * currentUser.role.multiplier_value) : 0;
                                            const isInReview = instance.status === 'IN_REVIEW';
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
                                                            {isInReview && (
                                                                <span className="badge badge-warning" style={{ marginLeft: '10px' }}>
                                                                    ⏳ In Review
                                                                </span>
                                                            )}
                                                        </div>
                                                        {task?.requires_photo_verification && !isInReview && (
                                                            <div className="photo-upload-section" style={{ marginTop: '10px' }}>
                                                                <input
                                                                    type="file"
                                                                    accept="image/*"
                                                                    capture="environment"
                                                                    onChange={(e) => {
                                                                        const file = e.target.files ? e.target.files[0] : null;
                                                                        setPhotoUrls(prev => ({ ...prev, [instance.id]: file }));
                                                                    }}
                                                                    onFocus={() => setCompletingId(instance.id)}
                                                                    className="filter-input"
                                                                    style={{ width: '100%', padding: '5px' }}
                                                                />
                                                                {photoUrls[instance.id] && (
                                                                    <div style={{ marginTop: '5px', borderRadius: '4px', overflow: 'hidden', maxWidth: '100px', maxHeight: '100px' }}>
                                                                        <img src={URL.createObjectURL(photoUrls[instance.id]!)} alt="Preview" style={{ width: '100%', height: 'auto', objectFit: 'cover' }} />
                                                                    </div>
                                                                )}
                                                                <small style={{ display: 'block', marginTop: '5px' }}>This task requires a photo verification.</small>
                                                            </div>
                                                        )}
                                                    </div>
                                                    <button
                                                        className={`btn ${isInReview ? 'btn-secondary' : 'btn-primary'}`}
                                                        onClick={() => handleComplete(instance)}
                                                        disabled={completingId === instance.id || isInReview}
                                                    >
                                                        {completingId === instance.id ? 'Submitting...' : (isInReview ? 'Pending Admin Review' : 'Mark Complete')}
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
                                    onChange={(e) => setFilters((prev: TransactionFilters) => ({ ...prev, txn_type: e.target.value as 'EARN' | 'REDEEM' | undefined || undefined }))}
                                    className="filter-select"
                                    value={filters.txn_type || ''}
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
                                <div className="table-container">
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

                    {activeTab === 'settings' && (
                        <div className="section glass-panel full-width">
                            <h2>⚙️ Notification Settings</h2>
                            <p>Configure how you receive updates and reminders.</p>

                            <div className="form-group" style={{ marginTop: '20px' }}>
                                <label>Email Address</label>
                                <input
                                    type="email"
                                    className="filter-input"
                                    style={{ width: '100%', maxWidth: '400px', display: 'block', marginTop: '5px' }}
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    placeholder="Enter your email"
                                />
                            </div>

                            <div className="form-group" style={{ marginTop: '15px' }}>
                                <label style={{ display: 'flex', alignItems: 'center', gap: '10px', cursor: 'pointer' }}>
                                    <input
                                        type="checkbox"
                                        checked={notificationsEnabled}
                                        onChange={(e) => setNotificationsEnabled(e.target.checked)}
                                    />
                                    Enable Email Notifications
                                </label>
                                <small style={{ display: 'block', marginTop: '5px', color: '#666' }}>Receive daily reminders and approval requests.</small>
                            </div>

                            <button
                                className="btn btn-primary"
                                style={{ marginTop: '20px' }}
                                onClick={handleSaveSettings}
                                disabled={isSavingSettings}
                            >
                                {isSavingSettings ? 'Saving...' : 'Save Settings'}
                            </button>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default UserDashboard;

