import React, { useState, useEffect, useCallback } from 'react';
import { useOutletContext } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { getUserDailyTasks, completeTask, getTasks, getUserTransactions, uploadTaskPhoto } from '../../api';
import type { TaskInstance, Task, User, Transaction, TransactionFilters } from '../../types';
import { SkeletonLoader } from '../../components/SkeletonLoader';
import PhotoDropzone from '../../components/PhotoDropzone';
import Toast from '../../components/Toast';
import { useToast } from '../../hooks/useToast';
import { useDebounce } from '../../hooks/useDebounce';
import { useSwipeTabs } from '../../hooks/useSwipeTabs';
import '../../styles/SharedDashboard.css';
import './UserDashboard.css';

interface DashboardContext {
    currentUser: User;
    refreshUser: () => Promise<void>;
}

// Extended TaskInstance with task details
interface TaskInstanceWithDetails extends TaskInstance {
    taskDetails?: Task;
}

// PhotoPreview component moved to PhotoDropzone.tsx

const UserDashboard: React.FC = () => {
    const { t } = useTranslation();
    const { currentUser, refreshUser } = useOutletContext<DashboardContext>();
    const [tasks, setTasks] = useState<TaskInstanceWithDetails[]>([]);
    const [transactions, setTransactions] = useState<Transaction[]>([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<'tasks' | 'history'>('tasks');
    const TABS = ['tasks', 'history'] as const;
    const swipeHandlers = useSwipeTabs(TABS, activeTab, setActiveTab as (tab: string) => void);
    const [historyPage, setHistoryPage] = useState(1);
    const [hasMoreHistory, setHasMoreHistory] = useState(true);
    const [completingId, setCompletingId] = useState<number | null>(null);
    const [photoUrls, setPhotoUrls] = useState<Record<number, File | null>>({});
    const { toasts, removeToast, success, error: showError } = useToast();

    const [searchTerm, setSearchTerm] = useState('');
    const debouncedSearch = useDebounce(searchTerm, 300);
    const [filters, setFilters] = useState<TransactionFilters>({});

    useEffect(() => {
        setFilters(prev => ({ ...prev, search: debouncedSearch || undefined }));
    }, [debouncedSearch]);

    // Removed redundant effect for resolving photoUrls memory leaks because PhotoPreview handles it.

    const fetchData = useCallback(async (resetHistory = false) => {
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
                const currentPage = resetHistory ? 1 : historyPage;
                if (resetHistory) setHistoryPage(1);
                const limit = 50;

                const transactionsRes = await getUserTransactions(currentUser.id, {
                    skip: (currentPage - 1) * limit,
                    limit,
                    ...filters
                });

                if (resetHistory) {
                    setTransactions(transactionsRes.data);
                } else {
                    setTransactions(prev => [...prev, ...transactionsRes.data]);
                }

                setHasMoreHistory(transactionsRes.data.length === limit);
            }
        } catch (err) {
            console.error('Failed to fetch data', err);
            showError('Failed to load dashboard data. Please try again.');
        } finally {
            setLoading(false);
        }
    }, [currentUser.id, activeTab, filters, historyPage, showError]);

    useEffect(() => {
        if (currentUser) {
            // Only reset history on activeTab change to 'history' or filter changes
            // Initial load for 'tasks' also runs here
            fetchData(activeTab === 'history' && historyPage === 1);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [activeTab, filters, currentUser]);

    // Handle history pagination changes specifically
    useEffect(() => {
        if (historyPage > 1 && activeTab === 'history') {
            fetchData(false);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [historyPage]);

    const loadMoreHistory = () => {
        setHistoryPage(prev => prev + 1);
    };

    const handleComplete = async (instance: TaskInstanceWithDetails) => {
        setCompletingId(instance.id);
        try {
            const task = instance.taskDetails;
            if (task?.requires_photo_verification && !photoUrls[instance.id] && instance.status !== 'IN_REVIEW') {
                showError(t('dashboard.photoRequiredError', { defaultValue: `Photo verification required for "${task.name}".`, task: task.name }));
                setCompletingId(null);
                return;
            }

            if (task?.requires_photo_verification && photoUrls[instance.id] && instance.status !== 'IN_REVIEW') {
                // First upload photo, then call completeTask
                await uploadTaskPhoto(instance.id, photoUrls[instance.id]!);
            }

            const res = await completeTask(instance.id);
            if (res.data.status === 'IN_REVIEW') {
                success(t('dashboard.taskSubmittedReview', 'Task submitted for review! 📸'));
                setPhotoUrls(prev => { const next = { ...prev }; delete next[instance.id]; return next; });
            } else {
                success(t('dashboard.taskCompletedSuccess', 'Task completed! Points awarded. 🎉'));
                await refreshUser();
            }
            fetchData(); // Refresh list to show updated status
        } catch (err) {
            console.error('Failed to complete task', err);
            showError(t('dashboard.errorCompletingTaskContext', { defaultValue: `Error completing "${instance.taskDetails?.name || 'Task'}". Please try again.`, task: instance.taskDetails?.name || 'Task' }));
        } finally {
            setCompletingId(null);
        }
    };

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' });
    };

    if (!currentUser) return (
        <div className="page-container fade-in">
            <header className="dashboard-header mb-4">
                <SkeletonLoader type="avatar" className="mb-2" />
                <SkeletonLoader type="title" className="mb-2" />
                <SkeletonLoader type="text" className="w-64" />
            </header>
            <div className="dashboard-content">
                <SkeletonLoader type="card" count={3} />
            </div>
        </div>
    );

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
                <h1 className="page-title">{t('dashboard.myDashboard', 'My Dashboard')}</h1>
                <p className="page-subtitle">
                    {t('dashboard.welcome', { defaultValue: 'Welcome, {{name}}!', name: currentUser.nickname })} 
                    {' '}
                    {t('dashboard.youHave', 'You have')} {currentUser.current_points} {t('dashboard.points', 'points')}.
                </p>
                <div className="gamification-badges flex-center gap-2 mt-2 center-badges">
                    {currentUser.current_streak > 0 && (
                        <span className="badge badge-warning text-lg px-2 py-1">
                            🔥 {currentUser.current_streak} {t('dashboard.dayStreak', { count: currentUser.current_streak })}
                        </span>
                    )}
                    {currentUser.last_task_date !== new Date().toISOString().split('T')[0] && (
                        <span className="badge badge-success text-lg px-2 py-1">
                            🎁 {t('dashboard.dailyBonus', '+5 Daily Bonus Available!')}
                        </span>
                    )}
                </div>
            </header>

            <div className="tabs">
                <button
                    className={`tab-btn ${activeTab === 'tasks' ? 'active' : ''}`}
                    onClick={() => setActiveTab('tasks')}
                >
                    📝 {t('dashboard.myTasks', 'My Tasks')}
                </button>
                <button
                    className={`tab-btn ${activeTab === 'history' ? 'active' : ''}`}
                    onClick={() => setActiveTab('history')}
                >
                    📜 {t('navigation.history', 'History')}
                </button>
            </div>

            {loading ? (
                <div className="dashboard-content dashboard-sections">
                    <div className="section glass-panel">
                        <SkeletonLoader type="title" className="mb-3" />
                        <SkeletonLoader type="card" count={3} />
                    </div>
                </div>
            ) : (
                <div className="dashboard-content" {...swipeHandlers}>
                    {activeTab === 'tasks' && (
                        <div className="dashboard-sections">
                            <div className="section glass-panel">
                                <h2>📅 {t('dashboard.todaysToDo', "Today's To-Do")}</h2>
                                {tasks.length === 0 ? (
                                    <div className="empty-state">
                                        <div className="empty-state-icon">🏖️</div>
                                        <h3>{t('dashboard.allCaughtUpUserTitle')}</h3>
                                        <p>{t('dashboard.noPendingTasksDesc', 'No pending tasks for today. Enjoy your free time or check back later! 🌟')}</p>
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
                                                        <p className="task-description">{task?.description || t('dashboard.noDescription', 'No description')}</p>
                                                        <div className="task-meta-info">
                                                            <span className="due-time">
                                                                🕒 {t('dashboard.due', 'Due')}: {new Date(instance.due_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                                            </span>
                                                            <span className="points-earn">
                                                                💰 {calculatedPoints} {t('dashboard.points', 'points')}
                                                            </span>
                                                            {isInReview && (
                                                                <span className="badge badge-warning ml-2">
                                                                    ⏳ {t('dashboard.inReview', 'In Review')}
                                                                </span>
                                                            )}
                                                        </div>
                                                        {task?.requires_photo_verification && !isInReview && (
                                                            <PhotoDropzone
                                                                instanceId={instance.id}
                                                                photo={photoUrls[instance.id] || null}
                                                                onPhotoChange={(id, file) => setPhotoUrls(prev => ({ ...prev, [id]: file }))}
                                                            />
                                                        )}
                                                    </div>
                                                    <button
                                                        className={`btn ${isInReview ? 'btn-secondary' : 'btn-primary'}`}
                                                        onClick={() => handleComplete(instance)}
                                                        disabled={completingId === instance.id || isInReview}
                                                    >
                                                        {completingId === instance.id ? t('dashboard.submitting', 'Submitting...') : (isInReview ? t('dashboard.pendingAdminReview', 'Pending Admin Review') : t('dashboard.markComplete', 'Mark Complete'))}
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
                            <h2>📜 {t('dashboard.transactionHistory', 'Transaction History')}</h2>

                            {/* Filters */}
                            <div className="filters-bar">
                                <select
                                    onChange={(e) => setFilters((prev: TransactionFilters) => ({ ...prev, txn_type: e.target.value as 'EARN' | 'REDEEM' | undefined || undefined }))}
                                    className="filter-select"
                                    value={filters.txn_type || ''}
                                >
                                    <option value="">{t('dashboard.allActivity', 'All Activity')}</option>
                                    <option value="EARN">{t('dashboard.earned', 'Earned')}</option>
                                    <option value="REDEEM">{t('dashboard.redeemed', 'Redeemed')}</option>
                                </select>

                                <input
                                    type="text"
                                    placeholder={t('dashboard.searchDescription', 'Search description...')}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                    className="filter-input"
                                    value={searchTerm}
                                />
                            </div>

                            {transactions.length === 0 ? (
                                <div className="empty-state">
                                    <p>{t('dashboard.noTransactionsMatchingFilters', 'No transactions found matching your filters.')}</p>
                                </div>
                            ) : (
                                <div className="table-container">
                                    <table className="data-table">
                                        <thead>
                                            <tr>
                                                <th>{t('history.date')}</th>
                                                <th>{t('history.type')}</th>
                                                <th>{t('history.points')}</th>
                                                <th>{t('history.details')}</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {transactions.map(tx => (
                                                <tr key={tx.id}>
                                                    <td>{formatDate(tx.timestamp)}</td>
                                                    <td>
                                                        <span className={`badge ${tx.type === 'EARN' ? 'badge-success' : 'badge-warning'}`}>
                                                            {tx.type === 'EARN' ? t('dashboard.earnType', 'EARN') : t('dashboard.redeemType', 'REDEEM')}
                                                        </span>
                                                    </td>
                                                    <td className={tx.awarded_points >= 0 ? 'text-success' : 'text-danger'}>
                                                        {tx.awarded_points > 0 ? '+' : ''}{tx.awarded_points}
                                                    </td>
                                                    <td>
                                                        {tx.description || (tx.type === 'EARN' ? t('dashboard.completedTaskDef', 'Completed task') : t('dashboard.redeemedRewardDef', 'Redeemed reward'))}
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                    {hasMoreHistory && (
                                        <div className="load-more-wrapper">
                                            <button className="btn btn-secondary" onClick={loadMoreHistory}>
                                                {t('dashboard.loadMore', 'Load More')}
                                            </button>
                                        </div>
                                    )}
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

