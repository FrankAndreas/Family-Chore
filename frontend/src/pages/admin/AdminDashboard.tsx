import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { getUsers, getTasks, triggerDailyReset, getAllTransactions } from '../../api';
import type { User, Task, Transaction, TransactionFilters } from '../../types';
import './Dashboard.css';

const AdminDashboard: React.FC = () => {
    const navigate = useNavigate();
    const [users, setUsers] = useState<User[]>([]);
    const [tasks, setTasks] = useState<Task[]>([]);
    const [transactions, setTransactions] = useState<Transaction[]>([]);
    const [loading, setLoading] = useState(true);
    const [resetting, setResetting] = useState(false);

    const [filters, setFilters] = useState<TransactionFilters>({});

    const fetchData = useCallback(async () => {
        try {
            const [usersRes, tasksRes, transactionsRes] = await Promise.all([
                getUsers(),
                getTasks(),
                getAllTransactions({ limit: 50, ...filters })
            ]);
            setUsers(usersRes.data);
            setTasks(tasksRes.data);
            setTransactions(transactionsRes.data);
        } catch (err) {
            console.error('Failed to fetch dashboard data', err);
        } finally {
            setLoading(false);
        }
    }, [filters]);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    const handleDailyReset = async () => {
        setResetting(true);
        try {
            await triggerDailyReset();
            alert('Daily reset completed! Task instances generated.');
        } catch (err) {
            console.error('Failed to trigger daily reset', err);
            alert('Failed to trigger daily reset');
        } finally {
            setResetting(false);
        }
    };

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' });
    };

    const getUserName = (userId: number) => {
        return users.find(u => u.id === userId)?.nickname || `User #${userId}`;
    };

    if (loading) return <div className="loading">Loading dashboard...</div>;

    // Calculate stats
    const totalUsers = users.length;
    const totalTasks = tasks.length;
    const totalPoints = users.reduce((sum, user) => sum + user.lifetime_points, 0);
    const totalCurrentPoints = users.reduce((sum, user) => sum + user.current_points, 0);

    return (
        <div className="page-container fade-in">
            <header className="page-header">
                <h1 className="page-title">Admin Dashboard</h1>
                <p className="page-subtitle">Overview of family performance and system status</p>
            </header>

            <div className="stats-grid">
                <div className="stat-card glass-panel">
                    <div className="stat-icon">👥</div>
                    <div className="stat-content">
                        <h3>Total Users</h3>
                        <p className="stat-value">{totalUsers}</p>
                    </div>
                </div>
                <div className="stat-card glass-panel">
                    <div className="stat-icon">📋</div>
                    <div className="stat-content">
                        <h3>Active Tasks</h3>
                        <p className="stat-value">{totalTasks}</p>
                    </div>
                </div>
                <div className="stat-card glass-panel">
                    <div className="stat-icon">💰</div>
                    <div className="stat-content">
                        <h3>Current Points</h3>
                        <p className="stat-value">{totalCurrentPoints.toLocaleString()}</p>
                    </div>
                </div>
                <div className="stat-card glass-panel">
                    <div className="stat-icon">🏆</div>
                    <div className="stat-content">
                        <h3>Lifetime Points</h3>
                        <p className="stat-value">{totalPoints.toLocaleString()}</p>
                    </div>
                </div>
            </div>

            <div className="dashboard-sections">
                <div className="section glass-panel">
                    <h2>Top Performers</h2>
                    <div className="leaderboard">
                        {users
                            .sort((a, b) => b.current_points - a.current_points)
                            .slice(0, 5)
                            .map((user, index) => (
                                <div key={user.id} className="leaderboard-item">
                                    <span className="rank">#{index + 1}</span>
                                    <span className="name">{user.nickname}</span>
                                    <span className="role-badge">{user.role.name}</span>
                                    <span className="points">{user.current_points} pts</span>
                                </div>
                            ))}
                        {users.length === 0 && (
                            <div className="empty-state">
                                <p>No users yet. Create some users to get started!</p>
                            </div>
                        )}
                    </div>
                </div>

                <div className="section glass-panel">
                    <h2>Quick Actions</h2>
                    <div className="action-buttons">
                        <button
                            className="btn btn-primary"
                            onClick={() => navigate('/admin/tasks')}
                        >
                            📋 Create Task
                        </button>
                        <button
                            className="btn btn-secondary"
                            onClick={() => navigate('/admin/users')}
                        >
                            👥 Add User
                        </button>
                        <button
                            className="btn btn-secondary"
                            onClick={handleDailyReset}
                            disabled={resetting}
                        >
                            {resetting ? '⏳ Resetting...' : '🔄 Daily Reset'}
                        </button>
                    </div>
                </div>
            </div>

            <div className="section glass-panel full-width">
                <h2>📜 Global Activity Log</h2>

                {/* Filters */}
                <div className="filters-bar">
                    <select
                        onChange={(e) => setFilters((prev: TransactionFilters) => ({ ...prev, user_id: e.target.value ? Number(e.target.value) : undefined }))}
                        className="filter-select"
                        value={filters.user_id || ''}
                    >
                        <option value="">All Users</option>
                        {users.map(u => <option key={u.id} value={u.id}>{u.nickname}</option>)}
                    </select>

                    <select
                        onChange={(e) => setFilters((prev: TransactionFilters) => ({ ...prev, type: e.target.value || undefined }))}
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
                        <p>No recent activity matching your filters.</p>
                    </div>
                ) : (
                    <div className="table-container">
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>Date</th>
                                    <th>User</th>
                                    <th>Action</th>
                                    <th>Points</th>
                                    <th>Details</th>
                                </tr>
                            </thead>
                            <tbody>
                                {transactions.map(tx => (
                                    <tr key={tx.id}>
                                        <td>{formatDate(tx.timestamp)}</td>
                                        <td>{getUserName(tx.user_id)}</td>
                                        <td>
                                            <span className={`badge ${tx.type === 'EARN' ? 'badge-success' : 'badge-warning'}`}>
                                                {tx.type}
                                            </span>
                                        </td>
                                        <td className={tx.awarded_points >= 0 ? 'text-success' : 'text-danger'}>
                                            {tx.awarded_points > 0 ? '+' : ''}{tx.awarded_points}
                                        </td>
                                        <td>
                                            {tx.description || (tx.type === 'EARN' ?
                                                `Task Completion (Base: ${tx.base_points_value})` :
                                                'Reward Redemption')}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
};

export default AdminDashboard;
