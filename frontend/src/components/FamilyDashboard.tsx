import { useState, useEffect, useRef, useCallback } from 'react';
import { getPendingTasks, getUsers, getRewards, completeTask, redeemRewardSplit, getAllTransactions } from '../api';
import type { TaskInstance, User, Reward, Transaction } from '../types';
import './FamilyDashboard.css';

interface ClaimModalProps {
    taskName: string;
    users: User[];
    onSelectUser: (userId: number) => void;
    onClose: () => void;
}

function ClaimModal({ taskName, users, onSelectUser, onClose }: ClaimModalProps) {
    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content glass-card" onClick={e => e.stopPropagation()}>
                <h2>Who did it?</h2>
                <p>Completing: <strong>{taskName}</strong></p>

                <div className="user-grid">
                    {users.map(user => (
                        <div
                            key={user.id}
                            className="user-select-card"
                            onClick={() => onSelectUser(user.id)}
                        >
                            <div className="user-avatar">
                                {user.nickname.charAt(0).toUpperCase()}
                            </div>
                            <div className="user-name">{user.nickname}</div>
                        </div>
                    ))}
                </div>

                <button className="btn btn-secondary" style={{ marginTop: '2rem', width: '100%' }} onClick={onClose}>
                    Cancel
                </button>
            </div>
        </div>
    );
}

interface SplitRedeemModalProps {
    reward: Reward;
    users: User[];
    onConfirm: (contributions: { user_id: number; points: number }[]) => void;
    onClose: () => void;
    redeeming: boolean;
}

function SplitRedeemModal({ reward, users, onConfirm, onClose, redeeming }: SplitRedeemModalProps) {
    const [contributions, setContributions] = useState<{ [userId: number]: number }>(
        () => Object.fromEntries(users.map(u => [u.id, 0]))
    );

    const totalContribution = Object.values(contributions).reduce((sum, pts) => sum + pts, 0);
    const remaining = reward.cost_points - totalContribution;
    const isExact = remaining === 0;

    const updateContribution = (userId: number, points: number) => {
        const user = users.find(u => u.id === userId);
        if (!user) return;
        const clamped = Math.max(0, Math.min(points, user.current_points));
        setContributions(prev => ({ ...prev, [userId]: clamped }));
    };

    const handleSplitEvenly = () => {
        const eligibleUsers = users.filter(u => u.current_points > 0);
        if (eligibleUsers.length === 0) return;

        const perUser = Math.floor(reward.cost_points / eligibleUsers.length);
        let leftover = reward.cost_points % eligibleUsers.length;

        const newContribs: { [userId: number]: number } = {};
        users.forEach(u => {
            if (u.current_points === 0) {
                newContribs[u.id] = 0;
            } else {
                let contrib = Math.min(perUser, u.current_points);
                if (leftover > 0 && contrib < u.current_points) {
                    contrib++;
                    leftover--;
                }
                newContribs[u.id] = contrib;
            }
        });
        setContributions(newContribs);
    };

    const handleMaxFromEach = () => {
        let remaining = reward.cost_points;
        const newContribs: { [userId: number]: number } = {};
        const sorted = [...users].sort((a, b) => b.current_points - a.current_points);

        sorted.forEach(user => {
            const take = Math.min(user.current_points, remaining);
            newContribs[user.id] = take;
            remaining -= take;
        });

        setContributions(newContribs);
    };

    const handleConfirm = () => {
        const contribs = Object.entries(contributions).map(([userId, points]) => ({
            user_id: parseInt(userId),
            points
        }));
        onConfirm(contribs);
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content glass-card split-modal" onClick={e => e.stopPropagation()}>
                <h2>🎁 Split Redemption</h2>
                <p className="reward-title"><strong>{reward.name}</strong> — {reward.cost_points} pts</p>

                <div className="preset-buttons">
                    <button className="btn btn-secondary btn-small" onClick={handleSplitEvenly}>
                        Split Evenly
                    </button>
                    <button className="btn btn-secondary btn-small" onClick={handleMaxFromEach}>
                        Max from Each
                    </button>
                </div>

                <div className="contribution-list">
                    {users.map(user => (
                        <div key={user.id} className="contribution-row">
                            <span className="contrib-user">
                                {user.nickname}
                                <span className="contrib-available">({user.current_points} pts)</span>
                            </span>
                            <input
                                type="number"
                                min={0}
                                max={user.current_points}
                                value={contributions[user.id] || 0}
                                onChange={e => updateContribution(user.id, parseInt(e.target.value) || 0)}
                                className="contrib-input"
                            />
                        </div>
                    ))}
                </div>

                <div className={`total-display ${isExact ? 'exact' : remaining < 0 ? 'over' : 'under'}`}>
                    Total: {totalContribution}/{reward.cost_points} pts
                    {isExact ? ' ✅' : remaining > 0 ? ` (need ${remaining} more)` : ` (${-remaining} over!)`}
                </div>

                <div className="modal-actions">
                    <button className="btn btn-secondary" onClick={onClose} disabled={redeeming}>
                        Cancel
                    </button>
                    <button
                        className="btn btn-success"
                        onClick={handleConfirm}
                        disabled={!isExact || redeeming}
                    >
                        {redeeming ? 'Redeeming...' : '🎉 Redeem!'}
                    </button>
                </div>
            </div>
        </div>
    );
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export default function FamilyDashboard({ onExit }: { onExit: () => void }) {
    const [activeTab, setActiveTab] = useState<'tasks' | 'redeem' | 'history'>('tasks');
    const [tasks, setTasks] = useState<TaskInstance[]>([]);
    const [users, setUsers] = useState<User[]>([]);
    const [rewards, setRewards] = useState<Reward[]>([]);
    const [transactions, setTransactions] = useState<Transaction[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedTask, setSelectedTask] = useState<TaskInstance | null>(null);
    const [selectedRedeem, setSelectedRedeem] = useState<Reward | null>(null);
    const [redeeming, setRedeeming] = useState(false);
    const [toast, setToast] = useState<string | null>(null);
    const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
    const [connected, setConnected] = useState(false);
    const eventSourceRef = useRef<EventSource | null>(null);

    const loadData = useCallback(async () => {
        try {
            const [tasksRes, usersRes, rewardsRes] = await Promise.all([
                getPendingTasks(),
                getUsers(),
                getRewards()
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
            const tasksRes = await getPendingTasks();
            setTasks(tasksRes.data);
            setLastUpdate(new Date());
        } catch (error) {
            console.error("Failed to refresh tasks", error);
        }
    }, []);

    const refreshData = useCallback(async () => {
        try {
            const [usersRes, rewardsRes] = await Promise.all([getUsers(), getRewards()]);
            setUsers(usersRes.data);
            setRewards(rewardsRes.data);
            setLastUpdate(new Date());
        } catch (error) {
            console.error("Failed to refresh data", error);
        }
    }, []);

    const [filters, setFilters] = useState({});

    const refreshTransactions = useCallback(async (newFilters = {}) => {
        const updatedFilters = { ...filters, ...newFilters };
        setFilters(updatedFilters);
        try {
            const transactionsRes = await getAllTransactions({
                skip: 0,
                limit: 50,
                ...updatedFilters
            });
            setTransactions(transactionsRes.data);
        } catch (error) {
            console.error("Failed to refresh transactions", error);
        }
    }, [filters]);

    useEffect(() => {
        loadData();

        const eventSource = new EventSource(`${API_BASE}/events`);
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
                if (activeTab === 'history') refreshTransactions();
            } else if (data.type === 'reward_redeemed') {
                refreshData();
                setToast(`🎉 ${data.payload?.reward_name || 'Reward'} redeemed!`);
                setTimeout(() => setToast(null), 3000);
                if (activeTab === 'history') refreshTransactions();
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
    }, [activeTab, loadData, refreshData, refreshTasks, refreshTransactions]);

    useEffect(() => {
        if (activeTab === 'history') {
            refreshTransactions();
        }
    }, [activeTab, refreshTransactions]);

    const handleCompleteClick = (task: TaskInstance) => {
        setSelectedTask(task);
    };

    const handleUserSelect = async (userId: number) => {
        if (!selectedTask) return;

        try {
            await completeTask(selectedTask.id, userId);
            setTasks(prev => prev.filter(t => t.id !== selectedTask.id));
            setSelectedTask(null);
            refreshTransactions(); // Refresh history if needed
        } catch (error) {
            console.error("Failed to complete task", error);
            alert("Error completing task");
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
            setToast(`🎉 ${selectedRedeem.name} redeemed by ${contributors}!`);
            setTimeout(() => setToast(null), 4000);
            setSelectedRedeem(null);
            refreshData();
            refreshTransactions();
        } catch (error) {
            console.error("Failed to redeem", error);
            setToast('❌ Redemption failed. Check contributions?');
            setTimeout(() => setToast(null), 3000);
        } finally {
            setRedeeming(false);
        }
    };

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' });
    };

    const getUserName = (userId: number) => {
        return users.find(u => u.id === userId)?.nickname || `User #${userId}`;
    };

    const getAffordableRewards = (user: User) => {
        return rewards.filter(r => user.current_points >= r.cost_points);
    };

    const groupedTasks = users.reduce((acc, user) => {
        acc[user.id] = tasks.filter(t => t.user_id === user.id);
        return acc;
    }, {} as Record<number, TaskInstance[]>);

    const unknownTasks = tasks.filter(t => !users.find(u => u.id === t.user_id));

    if (loading) return <div className="loading">Loading Family Board...</div>;

    return (
        <div className="family-dashboard">
            {toast && (
                <div className="dashboard-toast">
                    {toast}
                </div>
            )}

            <div className="family-dashboard-header">
                <div>
                    <h1>🏡 Family Dashboard</h1>
                    <small style={{ color: 'rgba(255,255,255,0.5)', fontSize: '0.75rem' }}>
                        {connected ? '🟢 Live updates' : '🔴 Reconnecting...'} • Last: {lastUpdate.toLocaleTimeString()}
                    </small>
                </div>
                <button className="btn btn-secondary" onClick={onExit}>
                    Back to Login
                </button>
            </div>

            <div className="dashboard-tabs">
                <button
                    className={`tab-btn ${activeTab === 'tasks' ? 'active' : ''}`}
                    onClick={() => setActiveTab('tasks')}
                >
                    📋 Tasks
                </button>
                <button
                    className={`tab-btn ${activeTab === 'redeem' ? 'active' : ''}`}
                    onClick={() => setActiveTab('redeem')}
                >
                    🎁 Redeem
                </button>
                <button
                    className={`tab-btn ${activeTab === 'history' ? 'active' : ''}`}
                    onClick={() => setActiveTab('history')}
                >
                    📜 History
                </button>
            </div>

            {activeTab === 'tasks' && (
                <div className="tab-content fade-in">
                    {users.map(user => {
                        const userTasks = groupedTasks[user.id] || [];
                        if (userTasks.length === 0) return null;

                        return (
                            <div key={user.id} className="user-group">
                                <h3>{user.nickname}'s Tasks</h3>
                                <div className="tasks-grid">
                                    {userTasks.map(instance => (
                                        <div key={instance.id} className="task-card glass-card">
                                            <div>
                                                <h4>{instance.task?.name || `Task #${instance.task_id}`}</h4>
                                                <p className="task-desc">{instance.task?.description}</p>
                                                <div className="task-info">
                                                    <span className="task-points">💎 {instance.task?.base_points} pts</span>
                                                    <span>📅 {instance.due_time.split('T')[0]}</span>
                                                </div>
                                            </div>
                                            <button
                                                className="btn btn-primary btn-complete"
                                                onClick={() => handleCompleteClick(instance)}
                                            >
                                                ✅ Done
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        );
                    })}

                    {unknownTasks.length > 0 && (
                        <div className="user-group">
                            <h3>Unassigned / Other</h3>
                            <div className="tasks-grid">
                                {unknownTasks.map(instance => (
                                    <div key={instance.id} className="task-card glass-card">
                                        <h4>{instance.task?.name}</h4>
                                        <button
                                            className="btn btn-primary"
                                            onClick={() => handleCompleteClick(instance)}
                                        >
                                            Done
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {tasks.length === 0 && (
                        <div className="empty-state">
                            <h2>🎉 All caught up! No pending tasks.</h2>
                        </div>
                    )}
                </div>
            )}

            {activeTab === 'redeem' && (
                <div className="tab-content fade-in">
                    {users.map(user => {
                        const affordable = getAffordableRewards(user);
                        if (affordable.length === 0) return null;

                        return (
                            <div key={user.id} className="user-group">
                                <h3>
                                    {user.nickname}
                                    <span className="user-points-badge">💎 {user.current_points} pts</span>
                                </h3>
                                <div className="rewards-grid">
                                    {affordable.map(reward => (
                                        <div key={reward.id} className="reward-card glass-card">
                                            <div className="reward-info">
                                                <h4>{reward.name}</h4>
                                                {reward.description && (
                                                    <p className="reward-desc">{reward.description}</p>
                                                )}
                                                <div className="reward-cost">
                                                    💰 {reward.cost_points} pts
                                                </div>
                                            </div>
                                            <button
                                                className="btn btn-success btn-redeem"
                                                onClick={() => handleRedeemClick(reward)}
                                            >
                                                🎁 Redeem
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        );
                    })}

                    {users.every(u => getAffordableRewards(u).length === 0) && (
                        <div className="empty-state">
                            <h2>😢 No affordable rewards yet.</h2>
                            <p>Complete more tasks to earn points!</p>
                        </div>
                    )}
                </div>
            )}

            {activeTab === 'history' && (
                <div className="tab-content fade-in">
                    <div className="glass-card history-panel">
                        <h2>📜 Recent Activity</h2>

                        {/* Filters */}
                        <div className="filters-bar">
                            <select
                                onChange={(e) => refreshTransactions({ user_id: e.target.value ? Number(e.target.value) : undefined })}
                                className="filter-select"
                            >
                                <option value="">All Users</option>
                                {users.map(u => <option key={u.id} value={u.id}>{u.nickname}</option>)}
                            </select>

                            <select
                                onChange={(e) => refreshTransactions({ type: e.target.value || undefined })}
                                className="filter-select"
                            >
                                <option value="">All Activity</option>
                                <option value="EARN">Earned</option>
                                <option value="REDEEM">Redeemed</option>
                            </select>

                            <input
                                type="text"
                                placeholder="Search..."
                                onChange={(e) => refreshTransactions({ search: e.target.value || undefined })}
                                className="filter-input"
                            />
                        </div>

                        {transactions.length === 0 ? (
                            <div className="empty-state">
                                <p>No recent activity matching your filters.</p>
                            </div>
                        ) : (
                            <div className="table-container">
                                <table className="data-table">
                                    <thead>
                                        <tr>
                                            <th>Time</th>
                                            <th>Who</th>
                                            <th>Action</th>
                                            <th>Points</th>
                                            <th>Details</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {transactions.map(tx => (
                                            <tr key={tx.id}>
                                                <td>{formatDate(tx.timestamp)}</td>
                                                <td><strong>{getUserName(tx.user_id)}</strong></td>
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
                </div>
            )}

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

