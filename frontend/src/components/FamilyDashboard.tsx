import { useState, useEffect, useRef, useCallback } from 'react';
import api, { completeTask, redeemRewardSplit } from '../api';
import { useTranslation } from 'react-i18next';
import type { TaskInstance, User, Reward, Transaction } from '../types';
import { useDebounce } from '../hooks/useDebounce';
import { useToast } from '../hooks/useToast';
import { useSwipeTabs } from '../hooks/useSwipeTabs';
import { SkeletonLoader } from './SkeletonLoader';
// import Modal from './Modal'; // Moved to sub-components
import Toast from './Toast';
import './FamilyDashboard.css';

// Extracted sub-components (C1 decomposition)
import ClaimModal from './FamilyDashboard/ClaimModal';
import SplitRedeemModal from './FamilyDashboard/SplitRedeemModal';
import TasksTab from './FamilyDashboard/TasksTab';
import RedeemTab from './FamilyDashboard/RedeemTab';
import HistoryTab from './FamilyDashboard/HistoryTab';

// FamilyDashboard-specific API calls with skipAuthRedirect
// These may be called without login, so we suppress 401-triggered reloads.
const getPendingTasksPublic = () => api.get('/tasks/pending', { skipAuthRedirect: true });
const getUsersPublic = () => api.get('/users/', { skipAuthRedirect: true });
const getRewardsPublic = () => api.get('/rewards/', { skipAuthRedirect: true });
const getAllTransactionsPublic = (params: Record<string, unknown> = {}) =>
    api.get('/transactions', { params: { skip: 0, limit: 100, ...params }, skipAuthRedirect: true });

// --- Inline ClaimModal and SplitRedeemModal removed ---
// Moved to ./FamilyDashboard/ClaimModal.tsx and ./FamilyDashboard/SplitRedeemModal.tsx

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export default function FamilyDashboard({ onExit }: { onExit: () => void }) {
    const { t } = useTranslation();
    const [activeTab, setActiveTab] = useState<'tasks' | 'redeem' | 'history'>('tasks');
    const FAMILY_TABS = ['tasks', 'redeem', 'history'] as const;
    const swipeHandlers = useSwipeTabs(FAMILY_TABS, activeTab, setActiveTab as (tab: string) => void);
    const [tasks, setTasks] = useState<TaskInstance[]>([]);
    const [users, setUsers] = useState<User[]>([]);
    const [rewards, setRewards] = useState<Reward[]>([]);
    const [transactions, setTransactions] = useState<Transaction[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedTask, setSelectedTask] = useState<TaskInstance | null>(null);
    const [selectedRedeem, setSelectedRedeem] = useState<Reward | null>(null);
    const [redeeming, setRedeeming] = useState(false);
    const { toasts, removeToast, success, error: showError } = useToast();
    const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
    const [connected, setConnected] = useState(false);
    const [historyPage, setHistoryPage] = useState(1);
    const [hasMoreHistory, setHasMoreHistory] = useState(true);
    const [collapsedUsers, setCollapsedUsers] = useState<Set<number>>(new Set());
    const eventSourceRef = useRef<EventSource | null>(null);

    const loadData = useCallback(async () => {
        try {
            const [tasksRes, usersRes, rewardsRes] = await Promise.all([
                getPendingTasksPublic(),
                getUsersPublic(),
                getRewardsPublic()
            ]);
            setTasks(tasksRes.data);
            setUsers(usersRes.data);
            setRewards(rewardsRes.data);
            setLastUpdate(new Date());
        } catch (error) {
            console.error("Failed to load family dashboard data", error);
        } finally {
            setLoading(false);
        }
    }, []);

    const refreshTasks = useCallback(async () => {
        try {
            const tasksRes = await getPendingTasksPublic();
            setTasks(tasksRes.data);
            setLastUpdate(new Date());
        } catch (error) {
            console.error("Failed to refresh tasks", error);
        }
    }, []);

    const refreshData = useCallback(async () => {
        try {
            const [usersRes, rewardsRes] = await Promise.all([getUsersPublic(), getRewardsPublic()]);
            setUsers(usersRes.data);
            setRewards(rewardsRes.data);
            setLastUpdate(new Date());
        } catch (error) {
            console.error("Failed to refresh data", error);
        }
    }, []);

    const [searchTerm, setSearchTerm] = useState('');
    const debouncedSearch = useDebounce(searchTerm, 300);
    const [filters, setFilters] = useState<Record<string, unknown>>({});

    useEffect(() => {
        setFilters(prev => ({ ...prev, search: debouncedSearch || undefined }));
    }, [debouncedSearch]);

    const refreshTransactions = useCallback(async (newFilters = {}, reset = false) => {
        const updatedFilters = { ...filters, ...newFilters };
        setFilters(updatedFilters);
        const currentPage = reset ? 1 : historyPage;
        if (reset) setHistoryPage(1);

        try {
            const limit = 50;
            const transactionsRes = await getAllTransactionsPublic({
                skip: (currentPage - 1) * limit,
                limit,
                ...updatedFilters
            });

            if (reset) {
                setTransactions(transactionsRes.data);
            } else {
                setTransactions(prev => [...prev, ...transactionsRes.data]);
            }

            setHasMoreHistory(transactionsRes.data.length === limit);
        } catch (error) {
            console.error("Failed to refresh transactions", error);
        }
    }, [filters, historyPage]);

    const loadMoreHistory = () => {
        setHistoryPage(prev => prev + 1);
    };

    // Load more when page changes, if not page 1 (which is handled by reset)
    useEffect(() => {
        if (historyPage > 1 && activeTab === 'history') {
            refreshTransactions({}, false);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [historyPage]);

    const activeTabRef = useRef(activeTab);
    const refreshTransactionsRef = useRef(refreshTransactions);

    useEffect(() => {
        activeTabRef.current = activeTab;
    }, [activeTab]);

    useEffect(() => {
        refreshTransactionsRef.current = refreshTransactions;
    }, [refreshTransactions]);

    useEffect(() => {
        loadData();

        const token = localStorage.getItem('auth_token') || '';
        const eventSource = new EventSource(`${API_BASE}/events?token=${encodeURIComponent(token)}`);
        eventSourceRef.current = eventSource;

        eventSource.onopen = () => {
            console.log('SSE connected');
            setConnected(true);
        };

        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log('SSE event:', data);

            if (data.type === 'connected') {
                setConnected(true);
            } else if (data.type === 'task_created' || data.type === 'task_completed' || data.type === 'task_deleted') {
                refreshTasks();
                // If we're on history tab, refresh that too
                if (activeTabRef.current === 'history') refreshTransactionsRef.current({}, true);
            } else if (data.type === 'reward_redeemed') {
                refreshData();
                success(`🎉 ${data.payload?.reward_name || 'Reward'} redeemed!`);
                if (activeTabRef.current === 'history') refreshTransactionsRef.current({}, true);
            }
            setLastUpdate(new Date());
        };

        eventSource.onerror = (error) => {
            console.error('SSE error:', error);
            setConnected(false);
        };

        return () => {
            if (eventSourceRef.current) {
                eventSourceRef.current.close();
            }
        };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [loadData, refreshData, refreshTasks]);

    useEffect(() => {
        if (activeTab === 'history') {
            refreshTransactions({}, true);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [activeTab]); // Removed refreshTransactions to avoid infinite loops when it changes filters

    const handleCompleteClick = (task: TaskInstance) => {
        setSelectedTask(task);
    };

    const handleUserSelect = async (userId: number) => {
        if (!selectedTask) return;

        try {
            await completeTask(selectedTask.id, userId);
            setTasks(prev => prev.filter(t => t.id !== selectedTask.id));
            setSelectedTask(null);
            if (activeTab === 'history') refreshTransactions({}, true); // Refresh history if needed
        } catch (error) {
            console.error("Failed to complete task", error);
            showError(`Error completing "${selectedTask.task?.name || `Task #${selectedTask.task_id}`}". Please try again.`);
        }
    };

    const handleRedeemClick = (reward: Reward) => {
        setSelectedRedeem(reward);
    };

    const handleSplitRedeemConfirm = async (contributions: { user_id: number; points: number }[]) => {
        if (!selectedRedeem) return;

        setRedeeming(true);
        try {
            const result = await redeemRewardSplit(selectedRedeem.id, contributions);
            const contributors = result.data.transactions?.map(t => t.user_name).join(', ') || '';
            success(`🎉 ${selectedRedeem.name} redeemed by ${contributors}!`);
            setSelectedRedeem(null);
            refreshData();
            if (activeTab === 'history') refreshTransactions({}, true);
        } catch (error) {
            console.error("Failed to redeem", error);
            showError(`❌ Failed to redeem "${selectedRedeem.name}". Check contributions?`);
        } finally {
            setRedeeming(false);
        }
    };

    // formatDate, getUserName, getAffordableRewards moved to sub-components

    const groupedTasks = users.reduce((acc, user) => {
        acc[user.id] = tasks.filter(t => t.user_id === user.id);
        return acc;
    }, {} as Record<number, TaskInstance[]>);

    const unknownTasks = tasks.filter(t => !users.find(u => u.id === t.user_id));

    if (loading) return (
        <div className="family-dashboard fade-in">
            <div className="family-dashboard-header">
                <div>
                    <h1 className="mb-2">🏡 {t('dashboard.familyDashboard')}</h1>
                    <SkeletonLoader type="text" className="w-64" />
                </div>
                <SkeletonLoader type="text" className="w-32" style={{ height: '38px', borderRadius: 'var(--radius-md)' }} />
            </div>
            <div className="dashboard-content dashboard-sections mt-4">
                <div className="section glass-panel">
                    <SkeletonLoader type="title" className="mb-3" />
                    <SkeletonLoader type="card" count={4} />
                </div>
            </div>
        </div>
    );

    return (
        <div className="family-dashboard">
            {/* Toast notifications */}
            <div className="toast-container">
                {toasts.map(tst => (
                    <Toast
                        key={tst.id}
                        message={tst.message}
                        type={tst.type}
                        duration={tst.duration}
                        onClose={() => removeToast(tst.id)}
                    />
                ))}
            </div>

            <div className="family-dashboard-header">
                <div>
                    <h1>🏡 {t('dashboard.familyDashboard')}</h1>
                    <small className="dashboard-live-status">
                        {connected ? `🟢 ${t('dashboard.liveUpdates')}` : `🔴 ${t('dashboard.reconnecting')}...`} • {t('dashboard.last')}: {lastUpdate.toLocaleTimeString()}
                    </small>
                </div>
                <button className="btn btn-secondary" onClick={onExit}>
                    {t('dashboard.backToLogin')}
                </button>
            </div>

            <div className="dashboard-tabs">
                <button
                    className={`tab-btn ${activeTab === 'tasks' ? 'active' : ''}`}
                    onClick={() => setActiveTab('tasks')}
                >
                    📋 {t('navigation.tasks', 'Tasks')}
                </button>
                <button
                    className={`tab-btn ${activeTab === 'redeem' ? 'active' : ''}`}
                    onClick={() => setActiveTab('redeem')}
                >
                    🎁 {t('navigation.rewards')}
                </button>
                <button
                    className={`tab-btn ${activeTab === 'history' ? 'active' : ''}`}
                    onClick={() => setActiveTab('history')}
                >
                    📜 {t('navigation.history', 'History')}
                </button>
            </div>

            <div className="family-dashboard-content" {...swipeHandlers}>
            {activeTab === 'tasks' && (
                <TasksTab
                    users={users}
                    groupedTasks={groupedTasks}
                    unknownTasks={unknownTasks}
                    tasks={tasks}
                    collapsedUsers={collapsedUsers}
                    setCollapsedUsers={setCollapsedUsers}
                    handleCompleteClick={handleCompleteClick}
                />
            )}

            {activeTab === 'redeem' && (
                <RedeemTab
                    users={users}
                    rewards={rewards}
                    redeeming={redeeming}
                    handleRedeemClick={handleRedeemClick}
                />
            )}

            {activeTab === 'history' && (
                <HistoryTab
                    users={users}
                    transactions={transactions}
                    refreshTransactions={refreshTransactions}
                    searchTerm={searchTerm}
                    setSearchTerm={setSearchTerm}
                    hasMoreHistory={hasMoreHistory}
                    loadMoreHistory={loadMoreHistory}
                />
            )}
            </div>

            {selectedTask && (
                <ClaimModal
                    taskName={selectedTask.task?.name || 'Task'}
                    users={users}
                    onSelectUser={handleUserSelect}
                    onClose={() => setSelectedTask(null)}
                />
            )}

            {selectedRedeem && (
                <SplitRedeemModal
                    reward={selectedRedeem}
                    users={users}
                    onConfirm={handleSplitRedeemConfirm}
                    onClose={() => setSelectedRedeem(null)}
                    redeeming={redeeming}
                />
            )}
        </div>
    );
}

