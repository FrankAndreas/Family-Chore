import React from 'react';
import { useTranslation } from 'react-i18next';
import type { User, Transaction } from '../../types';

export interface HistoryTabProps {
    users: User[];
    transactions: Transaction[];
    refreshTransactions: (filters: Record<string, unknown>, reset: boolean) => void;
    searchTerm: string;
    setSearchTerm: React.Dispatch<React.SetStateAction<string>>;
    hasMoreHistory: boolean;
    loadMoreHistory: () => void;
}

export default function HistoryTab({
    users,
    transactions,
    refreshTransactions,
    searchTerm,
    setSearchTerm,
    hasMoreHistory,
    loadMoreHistory,
}: HistoryTabProps) {
    const { t } = useTranslation();

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' });
    };

    const getUserName = (userId: number) => {
        return users.find(u => u.id === userId)?.nickname || `User #${userId}`;
    };

    return (
        <div className="tab-content fade-in">
            <div className="glass-card history-panel">
                <h2>📜 {t('dashboard.recentActivity', 'Recent Activity')}</h2>

                {/* Filters */}
                <div className="filters-bar">
                    <select
                        onChange={(e) => refreshTransactions({ user_id: e.target.value ? Number(e.target.value) : undefined }, true)}
                        className="filter-select"
                    >
                        <option value="">{t('dashboard.allUsers', 'All Users')}</option>
                        {users.map(u => <option key={u.id} value={u.id}>{u.nickname}</option>)}
                    </select>

                    <select
                        onChange={(e) => refreshTransactions({ txn_type: e.target.value || undefined }, true)}
                        className="filter-select"
                    >
                        <option value="">{t('dashboard.allActivity', 'All Activity')}</option>
                        <option value="EARN">{t('dashboard.earned', 'Earned')}</option>
                        <option value="REDEEM">{t('dashboard.redeemed', 'Redeemed')}</option>
                    </select>

                    <input
                        type="text"
                        placeholder={t('dashboard.search', 'Search...')}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="filter-input"
                        value={searchTerm}
                    />
                </div>

                {transactions.length === 0 ? (
                    <div className="empty-state">
                        <div className="empty-state-icon">📭</div>
                        <h3>{t('dashboard.noHistoryFound', 'No History Found')}</h3>
                        <p>{t('dashboard.noActivityMatchingFilters', 'No recent activity matching your filters.')}</p>
                    </div>
                ) : (
                    <div className="table-container">
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>{t('history.time')}</th>
                                    <th>{t('history.who')}</th>
                                    <th>{t('history.action')}</th>
                                    <th>{t('history.points')}</th>
                                    <th>{t('history.details')}</th>
                                </tr>
                            </thead>
                            <tbody>
                                {transactions.map(tx => (
                                    <tr key={tx.id}>
                                        <td>{formatDate(tx.timestamp)}</td>
                                        <td><strong>{getUserName(tx.user_id)}</strong></td>
                                        <td>
                                            <span className={`badge ${tx.type === 'EARN' ? 'badge-success' : 'badge-warning'}`}>
                                                <span aria-hidden="true">{tx.type === 'EARN' ? '📈 ' : '📉 '}</span>{tx.type === 'EARN' ? t('dashboard.earnType', 'EARN') : t('dashboard.redeemType', 'REDEEM')}
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
        </div>
    );
}
