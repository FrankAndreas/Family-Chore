import { useState, useEffect } from 'react';
import { completeTask, redeemRewardSplit } from '../api';
import { useTranslation } from 'react-i18next';
import type { TaskInstance, Reward } from '../types';
import { useDebounce } from '../hooks/useDebounce';
import { useToast } from '../hooks/useToast';
import { useSwipeTabs } from '../hooks/useSwipeTabs';
import { SkeletonLoader } from './SkeletonLoader';
import { useFamilyDashboardData } from "../hooks/useFamilyDashboardData";
import { useTransactions } from "../hooks/useTransactions";
// import Modal from './Modal'; // Moved to sub-components
import Toast from './Toast';
import './FamilyDashboard.css';

// Extracted sub-components (C1 decomposition)
import ClaimModal from './FamilyDashboard/ClaimModal';
import SplitRedeemModal from './FamilyDashboard/SplitRedeemModal';
import TasksTab from './FamilyDashboard/TasksTab';
import RedeemTab from './FamilyDashboard/RedeemTab';
import HistoryTab from './FamilyDashboard/HistoryTab';


export default function FamilyDashboard({ onExit }: { onExit: () => void }) {
    const { t } = useTranslation();
    const [activeTab, setActiveTab] = useState<"tasks" | "redeem" | "history">("tasks");
    const FAMILY_TABS = ["tasks", "redeem", "history"] as const;
    const swipeHandlers = useSwipeTabs(FAMILY_TABS, activeTab, setActiveTab as (tab: string) => void);
    const { toasts, removeToast, success, error: showError } = useToast();

    const [selectedTask, setSelectedTask] = useState<TaskInstance | null>(null);
    const [selectedRedeem, setSelectedRedeem] = useState<Reward | null>(null);
    const [redeeming, setRedeeming] = useState(false);
    const [collapsedUsers, setCollapsedUsers] = useState<Set<number>>(new Set());
    const [searchTerm, setSearchTerm] = useState("");
    const debouncedSearch = useDebounce(searchTerm, 300);

    const { transactions, hasMoreHistory, refreshTransactions, loadMoreHistory, setFilters } = useTransactions();

    const { tasks, setTasks, users, rewards, loading, connected, lastUpdate, refreshData } = useFamilyDashboardData(
        () => {
            if (activeTab === "history") refreshTransactions({}, true);
        },
        (data) => {
            success(`🎉 ${data?.reward_name || "Reward"} redeemed!`);
            if (activeTab === "history") refreshTransactions({}, true);
        }
    );

    useEffect(() => {
        setFilters(prev => ({ ...prev, search: debouncedSearch || undefined }));
    }, [debouncedSearch, setFilters]);

    useEffect(() => {
        if (activeTab === "history") {
            refreshTransactions({}, true);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [activeTab]);
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

