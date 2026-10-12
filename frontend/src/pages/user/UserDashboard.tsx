import React, { useState, useEffect, useMemo } from 'react';
import { useUser } from '../../context/UserContext';
import { useTranslation } from 'react-i18next';
import { getUserDailyTasks, completeTask, getTasks, getUserTransactions, uploadTaskPhoto } from '../../api';
import type { TaskInstance, Task, Transaction, TransactionFilters } from '../../types';
import { SkeletonLoader } from '../../components/SkeletonLoader';
import PhotoDropzone from '../../components/PhotoDropzone';
import { useToast } from '../../context/ToastContext';
import { useDebounce } from '../../hooks/useDebounce';
import { useSwipeTabs } from '../../hooks/useSwipeTabs';
import '../../styles/SharedDashboard.css';
import './UserDashboard.css';

// Extended TaskInstance with task details
interface TaskInstanceWithDetails extends TaskInstance {
    taskDetails?: Task;
}

// PhotoPreview component moved to PhotoDropzone.tsx

const HISTORY_PAGE_SIZE = 50;

const UserDashboard: React.FC = () => {
    const { t } = useTranslation();
    const { currentUser, refreshUser } = useUser();
    const [tasks, setTasks] = useState<TaskInstanceWithDetails[]>([]);
    const [transactions, setTransactions] = useState<Transaction[]>([]);
    const [activeTab, setActiveTab] = useState<'tasks' | 'history'>('tasks');
    const TABS = ['tasks', 'history'] as const;
    const swipeHandlers = useSwipeTabs(TABS, activeTab, setActiveTab as (tab: string) => void);
    const [historyPage, setHistoryPage] = useState(1);
    const [hasMoreHistory, setHasMoreHistory] = useState(true);
    const [completingId, setCompletingId] = useState<number | null>(null);
    const [photoUrls, setPhotoUrls] = useState<Record<number, File | null>>({});
    const { showToast } = useToast();

    const [searchTerm, setSearchTerm] = useState('');
    const debouncedSearch = useDebounce(searchTerm, 300);
    const [filters, setFilters] = useState<TransactionFilters>({});
    const txFilters = useMemo<TransactionFilters>(
        () => ({ ...filters, search: debouncedSearch || undefined }),
        [filters, debouncedSearch]
    );

    // Bumped to reload the task list after completing a task
    const [tasksVersion, setTasksVersion] = useState(0);

    // Restart history paging whenever the tab or the history filters change
    const historyQuery = `${activeTab}|${JSON.stringify(txFilters)}`;
    const [pagedQuery, setPagedQuery] = useState(historyQuery);
    if (historyQuery !== pagedQuery) {
        setPagedQuery(historyQuery);
        setHistoryPage(1);
    }

    // Identifies the data the current view needs; loading until that request has finished
    const requestKey = activeTab === 'tasks'
        ? `tasks|${tasksVersion}`
        : `${historyQuery}|${historyPage}`;
    const [loadedKey, setLoadedKey] = useState<string | null>(null);
    const loading = loadedKey !== requestKey;

    // Removed redundant effect for resolving photoUrls memory leaks because PhotoPreview handles it.

    useEffect(() => {
        let ignore = false;
        const userId = currentUser.id;

        const request = activeTab === 'tasks'
            // Fetch both task instances and task templates
            ? Promise.all([getUserDailyTasks(userId), getTasks()]).then(([instancesRes, templatesRes]) => {
                if (ignore) return;
                const instances: TaskInstance[] = instancesRes.data;
                const templates: Task[] = templatesRes.data;

                // Merge instances with their task details
                const instancesWithDetails = instances.map(instance => ({
                    ...instance,
                    taskDetails: templates.find(t => t.id === instance.task_id)
                }));
                // Only show PENDING or IN_REVIEW tasks on the dashboard actively
                setTasks(instancesWithDetails.filter(t => t.status === 'PENDING' || t.status === 'IN_REVIEW'));
            })
            : getUserTransactions(userId, {
                skip: (historyPage - 1) * HISTORY_PAGE_SIZE,
                limit: HISTORY_PAGE_SIZE,
                ...txFilters
            }).then((transactionsRes) => {
                if (ignore) return;
                // Page 1 replaces the list; later pages append to it
                setTransactions(prev => historyPage === 1 ? transactionsRes.data : [...prev, ...transactionsRes.data]);
                setHasMoreHistory(transactionsRes.data.length === HISTORY_PAGE_SIZE);
            });

        request
            .catch((err) => {
                console.error('Failed to fetch data', err);
                if (!ignore) showToast('Failed to load dashboard data. Please try again.', 'error');
            })
            .finally(() => {
                if (!ignore) setLoadedKey(requestKey);
            });

        return () => {
            ignore = true;
        };
    }, [currentUser.id, activeTab, historyPage, txFilters, tasksVersion, requestKey, showToast]);

    const loadMoreHistory = () => {
        setHistoryPage(prev => prev + 1);
    };

    const handleComplete = async (instance: TaskInstanceWithDetails) => {
        setCompletingId(instance.id);
        try {
            const task = instance.taskDetails;
            if (task?.requires_photo_verification && !photoUrls[instance.id] && instance.status !== 'IN_REVIEW') {
                showToast(t('dashboard.photoRequiredError', { defaultValue: `Photo verification required for "${task.name}".`, task: task.name }), 'error');
                setCompletingId(null);
                return;
            }

            if (task?.requires_photo_verification && photoUrls[instance.id] && instance.status !== 'IN_REVIEW') {
                // First upload photo, then call completeTask
                await uploadTaskPhoto(instance.id, photoUrls[instance.id]!);
            }

            const res = await completeTask(instance.id);
            if (res.data.status === 'IN_REVIEW') {
                showToast(t('dashboard.taskSubmittedReview', 'Task submitted for review! 📸'), 'success');
                setPhotoUrls(prev => { const next = { ...prev }; delete next[instance.id]; return next; });
            } else {
                showToast(t('dashboard.taskCompletedSuccess', 'Task completed! Points awarded. 🎉'), 'success');
                await refreshUser();
            }
            setTasksVersion(v => v + 1); // Refresh list to show updated status
        } catch (err) {
            console.error('Failed to complete task', err);
            showToast(t('dashboard.errorCompletingTaskContext', { defaultValue: `Error completing "${instance.taskDetails?.name || 'Task'}". Please try again.`, task: instance.taskDetails?.name || 'Task' }), 'error');
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

