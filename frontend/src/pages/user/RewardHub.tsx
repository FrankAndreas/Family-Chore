import React, { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import { useTranslation, Trans } from 'react-i18next';
import { getRewards, createReward, setUserGoal, redeemReward } from '../../api';
import type { Reward, User } from '../../types';
import LoadingSpinner from '../../components/LoadingSpinner';
import Toast from '../../components/Toast';
import { useToast } from '../../hooks/useToast';
import '../admin/Dashboard.css';
import './RewardHub.css';

interface DashboardContext {
    currentUser: User;
}

const RewardHub: React.FC = () => {
    const { currentUser } = useOutletContext<DashboardContext>();
    const { t } = useTranslation();
    const [rewards, setRewards] = useState<Reward[]>([]);
    const [loading, setLoading] = useState(true);
    const [showCreateForm, setShowCreateForm] = useState(false);
    const [submitting, setSubmitting] = useState(false);
    const { toasts, removeToast, success, error } = useToast();

    const [formData, setFormData] = useState({
        name: '',
        description: '',
        cost_points: 0,
        tier_level: 1,
    });

    // Redemption modal state
    const [redeemConfirm, setRedeemConfirm] = useState<{ reward: Reward; show: boolean } | null>(null);
    const [redeeming, setRedeeming] = useState(false);

    useEffect(() => {
        fetchRewards();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const fetchRewards = async () => {
        try {
            const response = await getRewards();
            setRewards(response.data);
        } catch (err) {
            error(t('rewards.toasts.load_error'));
            console.error('Failed to fetch rewards', err);
        } finally {
            setLoading(false);
        }
    };

    const handleCreateReward = async (e: React.FormEvent) => {
        e.preventDefault();
        setSubmitting(true);

        try {
            await createReward(formData);
            success(t('rewards.toasts.create_success'));
            setShowCreateForm(false);
            setFormData({ name: '', description: '', cost_points: 0, tier_level: 1 });
            fetchRewards();
        } catch (err) {
            error(t('rewards.toasts.create_error'));
            console.error('Failed to create reward', err);
        } finally {
            setSubmitting(false);
        }
    };

    const handleSetGoal = async (rewardId: number) => {
        try {
            await setUserGoal(currentUser.id, rewardId);
            success(t('rewards.toasts.goal_success'));
        } catch (err) {
            error(t('rewards.toasts.goal_error'));
            console.error('Failed to set goal', err);
        }
    };

    const handleRedeemClick = (reward: Reward) => {
        setRedeemConfirm({ reward, show: true });
    };

    const handleRedeemConfirm = async () => {
        if (!redeemConfirm) return;

        setRedeeming(true);
        try {
            await redeemReward(redeemConfirm.reward.id, currentUser.id);
            success(t('rewards.toasts.redeem_success', { name: redeemConfirm.reward.name }));
            setRedeemConfirm(null);
            // Refresh page to update points (SSE should handle this, but forcing refresh)
            window.location.reload();
        } catch (err) {
            error(t('rewards.toasts.redeem_error'));
            console.error('Failed to redeem reward', err);
        } finally {
            setRedeeming(false);
        }
    };

    const handleRedeemCancel = () => {
        setRedeemConfirm(null);
    };

    const getProgressPercentage = (cost: number): number => {
        return Math.min(100, Math.round((currentUser.current_points / cost) * 100));
    };

    const canAfford = (cost: number): boolean => {
        return currentUser.current_points >= cost;
    };

    const getTierBadge = (tier: number) => {
        const badges = {
            1: { label: t('rewards.tier_names.1'), color: '#cd7f32', emoji: '🥉' },
            2: { label: t('rewards.tier_names.2'), color: '#c0c0c0', emoji: '🥈' },
            3: { label: t('rewards.tier_names.3'), color: '#ffd700', emoji: '🥇' },
        };
        const badge = badges[tier as keyof typeof badges] || badges[1];
        return (
            <span className="tier-badge" style={{ backgroundColor: badge.color }}>
                {badge.emoji} {badge.label}
            </span>
        );
    };

    if (loading) {
        return <LoadingSpinner fullPage message={t('rewards.loading')} />;
    }

    // Sort rewards by tier and cost
    const sortedRewards = [...rewards].sort((a, b) => {
        if (a.tier_level !== b.tier_level) {
            return a.tier_level - b.tier_level;
        }
        return a.cost_points - b.cost_points;
    });

    const userGoal = currentUser.current_goal_reward_id
        ? rewards.find(r => r.id === currentUser.current_goal_reward_id)
        : null;

    return (
        <div className="page-container reward-hub fade-in">
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
                <div>
                    <h1 className="page-title">🎁 {t('rewards.title')}</h1>
                    <p className="page-subtitle">
                        <Trans i18nKey="rewards.subtitle" values={{ points: currentUser.current_points }} components={{ 1: <strong /> }} />
                    </p>
                </div>
                {currentUser.role.name === 'Admin' && (
                    <button
                        className="btn btn-primary"
                        onClick={() => setShowCreateForm(!showCreateForm)}
                    >
                        {showCreateForm ? t('rewards.cancel_button') : '+ ' + t('rewards.add_button')}
                    </button>
                )}
            </header>

            {/* Current Goal Display */}
            {userGoal && (
                <div className="current-goal glass-panel mb-lg">
                    <div className="goal-header">
                        <h2>{t('rewards.card.goal_indicator')}</h2>
                        {canAfford(userGoal.cost_points) && (
                            <div className="ready-badge pulse">{t('rewards.current_goal.ready')}</div>
                        )}
                    </div>
                    <div className="goal-content">
                        <div className="goal-info">
                            <h3>{userGoal.name}</h3>
                            <p>{userGoal.description}</p>
                            <div className="goal-stats">
                                <span className="cost">{t('rewards.card.points_val', { points: userGoal.cost_points })}</span>
                                {getTierBadge(userGoal.tier_level)}
                            </div>
                        </div>
                        <div className="goal-progress">
                            <div className="progress-stats">
                                <span>{currentUser.current_points} / {userGoal.cost_points}</span>
                                <span>{getProgressPercentage(userGoal.cost_points)}%</span>
                            </div>
                            <div className="progress-bar">
                                <div
                                    className="progress-fill"
                                    style={{ width: `${getProgressPercentage(userGoal.cost_points)}%` }}
                                ></div>
                            </div>
                            <div className="points-needed">
                                {canAfford(userGoal.cost_points)
                                    ? t('rewards.current_goal.achieved')
                                    : t('rewards.current_goal.points_needed', { points: userGoal.cost_points - currentUser.current_points })
                                }
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Create Reward Form */}
            {showCreateForm && (
                <div className="glass-panel mb-lg">
                    <h2>{t('rewards.create_form.title')}</h2>
                    <form onSubmit={handleCreateReward} className="create-reward-form">
                        <div className="form-grid">
                            <div className="form-group">
                                <label>{t('rewards.create_form.name_label')}</label>
                                <input
                                    type="text"
                                    required
                                    value={formData.name}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                    placeholder={t('rewards.create_form.name_placeholder')}
                                />
                            </div>

                            <div className="form-group">
                                <label>{t('rewards.create_form.cost_label')}</label>
                                <input
                                    type="number"
                                    required
                                    min="1"
                                    value={formData.cost_points}
                                    onChange={(e) => setFormData({ ...formData, cost_points: parseInt(e.target.value) })}
                                    placeholder="50"
                                />
                            </div>

                            <div className="form-group">
                                <label>{t('rewards.create_form.tier_label')}</label>
                                <select
                                    value={formData.tier_level}
                                    onChange={(e) => setFormData({ ...formData, tier_level: parseInt(e.target.value) })}
                                >
                                    <option value={1}>{t('rewards.create_form.tiers.bronze')}</option>
                                    <option value={2}>{t('rewards.create_form.tiers.silver')}</option>
                                    <option value={3}>{t('rewards.create_form.tiers.gold')}</option>
                                </select>
                            </div>

                            <div className="form-group full-width">
                                <label>{t('rewards.create_form.description_label')}</label>
                                <textarea
                                    value={formData.description}
                                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                    placeholder={t('rewards.create_form.description_placeholder')}
                                    rows={3}
                                />
                            </div>
                        </div>

                        <div className="form-actions">
                            <button type="button" className="btn btn-secondary" onClick={() => setShowCreateForm(false)}>
                                {t('rewards.cancel_button')}
                            </button>
                            <button type="submit" className="btn btn-primary" disabled={submitting}>
                                {submitting ? t('rewards.create_form.submitting') : t('rewards.create_form.submit_button')}
                            </button>
                        </div>
                    </form>
                </div>
            )}

            {/* Rewards Grid */}
            <div className="rewards-grid">
                {sortedRewards.length === 0 && (
                    <div className="empty-state">
                        <p>{t('rewards.empty_state.message')} {currentUser.role.name === 'Admin' && t('rewards.empty_state.admin_hint')}</p>
                    </div>
                )}

                {sortedRewards.map(reward => {
                    const progress = getProgressPercentage(reward.cost_points);
                    const affordable = canAfford(reward.cost_points);
                    const isCurrentGoal = userGoal?.id === reward.id;

                    return (
                        <div
                            key={reward.id}
                            className={`reward-card glass-panel ${affordable ? 'affordable' : ''} ${isCurrentGoal ? 'current-goal' : ''}`}
                        >
                            {isCurrentGoal && <div className="goal-indicator">{t('rewards.card.goal_indicator')}</div>}

                            <div className="reward-header">
                                <h3>{reward.name}</h3>
                                {getTierBadge(reward.tier_level)}
                            </div>

                            <p className="reward-description">{reward.description || t('rewards.card.no_description')}</p>

                            <div className="reward-cost">
                                <span className="cost-label">{t('rewards.card.cost_label')}</span>
                                <span className="cost-value">{t('rewards.card.points_val', { points: reward.cost_points })}</span>
                            </div>

                            <div className="reward-progress">
                                <div className="progress-bar">
                                    <div
                                        className="progress-fill"
                                        style={{ width: `${progress}%` }}
                                    ></div>
                                </div>
                                <span className="progress-text">{progress}%</span>
                            </div>

                            {!isCurrentGoal && (
                                <button
                                    className="btn btn-secondary btn-block"
                                    onClick={() => handleSetGoal(reward.id)}
                                >
                                    {t('rewards.card.set_goal_button')}
                                </button>
                            )}

                            {affordable && (
                                <button
                                    className="btn btn-success btn-block mt-sm"
                                    onClick={() => handleRedeemClick(reward)}
                                >
                                    🎉 {t('rewards.redeem_button')}
                                </button>
                            )}

                            {affordable && (
                                <div className="affordable-badge">{t('rewards.card.can_afford_badge')}</div>
                            )}
                        </div>
                    );
                })}
            </div>

            {/* Redemption Confirmation Modal */}
            {redeemConfirm && redeemConfirm.show && (
                <div className="modal-overlay" onClick={handleRedeemCancel}>
                    <div className="modal-content glass-panel" onClick={e => e.stopPropagation()}>
                        <h2>{t('rewards.confirm_redeem_title')}</h2>
                        <p>{t('rewards.confirm_redeem_message', {
                            name: redeemConfirm.reward.name,
                            points: redeemConfirm.reward.cost_points
                        })}</p>
                        <div className="modal-actions">
                            <button
                                className="btn btn-secondary"
                                onClick={handleRedeemCancel}
                                disabled={redeeming}
                            >
                                {t('common.cancel')}
                            </button>
                            <button
                                className="btn btn-success"
                                onClick={handleRedeemConfirm}
                                disabled={redeeming}
                            >
                                {redeeming ? t('common.loading') : t('rewards.confirm_redeem_button')}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default RewardHub;
