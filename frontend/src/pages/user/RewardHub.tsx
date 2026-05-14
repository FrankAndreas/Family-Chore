import React, { useState, useEffect } from 'react';
import { useUser } from '../../context/UserContext';
import { useTranslation, Trans } from 'react-i18next';
import { getRewards, createReward, setUserGoal, redeemReward, updateReward, deleteReward } from '../../api';
import type { Reward } from '../../types';
import { TIER_THRESHOLDS } from '../../constants';
import { triggerConfetti } from '../../utils/confetti';
import { SkeletonLoader } from '../../components/SkeletonLoader';
import Modal from '../../components/Modal';
import { useToast } from '../../context/ToastContext';
import '../../styles/SharedDashboard.css';
import './RewardHub.css';

// Extracted sub-components (C2 decomposition)
import TierProgressBar from './RewardHub/TierProgressBar';
import CurrentGoal from './RewardHub/CurrentGoal';
import RewardCard from './RewardHub/RewardCard';
import RewardForm from './RewardHub/RewardForm';
import type { RewardFormData } from './RewardHub/RewardForm';

const RewardHub: React.FC = () => {
    const { currentUser, refreshUser } = useUser();
    const { t } = useTranslation();
    const [rewards, setRewards] = useState<Reward[]>([]);
    const [loading, setLoading] = useState(true);
    const [rewardToDelete, setRewardToDelete] = useState<Reward | null>(null);
    const [showCreateForm, setShowCreateForm] = useState(false);
    const [submitting, setSubmitting] = useState(false);
    const { showToast } = useToast();

    const [formData, setFormData] = useState<RewardFormData>({
        name: '',
        description: '',
        cost_points: 0,
        tier_level: 1,
    });

    const [editingReward, setEditingReward] = useState<Reward | null>(null);

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
            showToast(t('rewards.toasts.load_error'), 'error');
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
            showToast(t('rewards.toasts.create_success'), 'success');
            setShowCreateForm(false);
            setFormData({ name: '', description: '', cost_points: 0, tier_level: 1 });
            fetchRewards();
        } catch (err) {
            showToast(t('rewards.toasts.create_error'), 'error');
            console.error('Failed to create reward', err);
        } finally {
            setSubmitting(false);
        }
    };

    const handleEditReward = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!editingReward) return;
        setSubmitting(true);

        try {
            await updateReward(editingReward.id, {
                name: formData.name,
                description: formData.description,
                cost_points: formData.cost_points,
                tier_level: formData.tier_level
            });
            showToast(t('rewards.toasts.update_success', 'Reward updated successfully!'), 'success');
            setEditingReward(null);
            setFormData({ name: '', description: '', cost_points: 0, tier_level: 1 });
            fetchRewards();
        } catch (err) {
            showToast(t('rewards.toasts.update_error', 'Failed to update reward'), 'error');
            console.error('Failed to update reward', err);
        } finally {
            setSubmitting(false);
        }
    };

    const openEditForm = (reward: Reward) => {
        setFormData({
            name: reward.name,
            description: reward.description || '',
            cost_points: reward.cost_points,
            tier_level: reward.tier_level
        });
        setEditingReward(reward);
    };

    const handleSetGoal = async (rewardId: number) => {
        try {
            await setUserGoal(currentUser.id, rewardId);
            showToast(t('rewards.toasts.goal_success'), 'success');
        } catch (err) {
            showToast(t('rewards.toasts.goal_error'), 'error');
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
            await redeemReward(redeemConfirm.reward.id);
            showToast(t('rewards.toasts.redeem_success', { name: redeemConfirm.reward.name }), 'success');
            setRedeemConfirm(null);
            await refreshUser();
            // Re-fetch rewards instead of full page reload (preserves React state and SSE)
            fetchRewards();
        } catch (err) {
            showToast(t('rewards.toasts.redeem_error'), 'error');
            console.error('Failed to redeem reward', err);
        } finally {
            setRedeeming(false);
        }
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

    const getTierProgress = () => {
        const lp = currentUser.lifetime_points;
        if (lp < TIER_THRESHOLDS.SILVER) {
            return {
                current: 'Bronze',
                next: 'Silver',
                target: TIER_THRESHOLDS.SILVER,
                percent: Math.min(100, (lp / TIER_THRESHOLDS.SILVER) * 100)
            };
        } else if (lp < TIER_THRESHOLDS.GOLD) {
            return {
                current: 'Silver',
                next: 'Gold',
                target: TIER_THRESHOLDS.GOLD,
                percent: Math.min(100, ((lp - TIER_THRESHOLDS.SILVER) / (TIER_THRESHOLDS.GOLD - TIER_THRESHOLDS.SILVER)) * 100)
            };
        } else {
            return {
                current: 'Gold',
                next: 'Max',
                target: lp,
                percent: 100
            };
        }
    };

    const tierStats = getTierProgress();
    const isAdmin = currentUser.role.name === 'Admin';

    // Celebration Logic: trigger if points increase across a threshold
    const prevPoints = React.useRef(currentUser.lifetime_points);

    useEffect(() => {
        const prev = prevPoints.current;
        const curr = currentUser.lifetime_points;

        if (curr > prev) {
            if ((prev < TIER_THRESHOLDS.SILVER && curr >= TIER_THRESHOLDS.SILVER) ||
                (prev < TIER_THRESHOLDS.GOLD && curr >= TIER_THRESHOLDS.GOLD)) {
                triggerConfetti();
                showToast(t('rewards.toasts.tier_unlocked', { tier: tierStats.current }), 'success');
            }
        }
        prevPoints.current = curr;
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [currentUser.lifetime_points, t, showToast]);

    if (loading) {
        return (
            <div className="page-container reward-hub fade-in">
                <header className="hub-header">
                    <SkeletonLoader type="title" className="mb-2" />
                    <SkeletonLoader type="text" className="w-48 mb-4" />
                </header>
                <div className="hub-content">
                    <div className="main-section">
                        <section className="rewards-grid">
                            <SkeletonLoader type="card" count={4} />
                        </section>
                    </div>
                </div>
            </div>
        );
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
            {/* Delete Confirmation Modal */}
            <Modal
                isOpen={!!rewardToDelete}
                onClose={() => setRewardToDelete(null)}
                title={t('common.confirm', 'Confirm Action')}
            >
                <div>
                    <p style={{ color: '#333' }}>
                        {t('rewards.confirm_delete', `Are you sure you want to delete ${rewardToDelete?.name}? This will remove it as a goal for anyone tracking it.`)}
                    </p>
                    <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem', justifyContent: 'flex-end' }}>
                        <button className="btn btn-secondary" onClick={() => setRewardToDelete(null)}>
                            {t('common.cancel', 'Cancel')}
                        </button>
                        <button
                            className="btn"
                            style={{ backgroundColor: '#ef4444', color: 'white' }}
                            onClick={async () => {
                                if (!rewardToDelete) return;
                                try {
                                    await deleteReward(rewardToDelete.id);
                                    showToast(t('rewards.toasts.delete_success', 'Reward deleted!'), 'success');
                                    fetchRewards();
                                } catch (err) {
                                    showToast(t('rewards.toasts.delete_error', 'Failed to delete reward.'), 'error');
                                    console.error('Failed to delete reward', err);
                                } finally {
                                    setRewardToDelete(null);
                                }
                            }}
                        >
                            {t('common.delete', 'Delete')}
                        </button>
                    </div>
                </div>
            </Modal>

            {/* Edit Reward Modal — uses shared Modal component for accessibility (fixes A1/N4 regression) */}
            <Modal
                isOpen={!!editingReward}
                onClose={() => setEditingReward(null)}
                title={t('rewards.edit_form.title', 'Edit Reward')}
                size="large"
            >
                <RewardForm
                    formData={formData}
                    onChange={setFormData}
                    onSubmit={handleEditReward}
                    onCancel={() => setEditingReward(null)}
                    submitting={submitting}
                    submitButtonText={t('common.save', 'Save')}
                />
            </Modal>

            {/* Redemption Confirmation Modal — uses shared Modal component for accessibility */}
            <Modal
                isOpen={!!redeemConfirm?.show}
                onClose={() => setRedeemConfirm(null)}
                title={t('rewards.confirm_redeem_title')}
            >
                {redeemConfirm && (
                    <div>
                        <p>{t('rewards.confirm_redeem_message', {
                            name: redeemConfirm.reward.name,
                            points: redeemConfirm.reward.cost_points
                        })}</p>

                        <div className="redemption-math mb-lg glass-panel-inner">
                            <div className="math-row">
                                <span>{t('rewards.modal.current_balance', 'Current Balance')}:</span>
                                <span>{currentUser.current_points} pts</span>
                            </div>
                            <div className="math-row">
                                <span>{t('rewards.modal.reward_cost', 'Reward Cost')}:</span>
                                <span className="negative">- {redeemConfirm.reward.cost_points} pts</span>
                            </div>
                            <hr className="math-divider" />
                            <div className="math-row total">
                                <span>{t('rewards.modal.remaining_balance', 'Remaining Balance')}:</span>
                                <span>{currentUser.current_points - redeemConfirm.reward.cost_points} pts</span>
                            </div>
                        </div>

                        <div className="modal-actions">
                            <button
                                className="btn btn-secondary"
                                onClick={() => setRedeemConfirm(null)}
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
                )}
            </Modal>

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

            <TierProgressBar
                tierStats={tierStats}
                lifetimePoints={currentUser.lifetime_points}
            />

            {userGoal && (
                <CurrentGoal
                    goal={userGoal}
                    currentPoints={currentUser.current_points}
                    canAfford={canAfford(userGoal.cost_points)}
                    getProgressPercentage={getProgressPercentage}
                    getTierBadge={getTierBadge}
                />
            )}

            {/* Create Reward Form */}
            {showCreateForm && (
                <div className="glass-panel mb-lg">
                    <h2>{t('rewards.create_form.title')}</h2>
                    <RewardForm
                        formData={formData}
                        onChange={setFormData}
                        onSubmit={handleCreateReward}
                        onCancel={() => setShowCreateForm(false)}
                        submitting={submitting}
                    />
                </div>
            )}

            {/* Tiered Rewards */}
            {sortedRewards.length === 0 && (
                <div className="empty-state">
                    <div className="empty-state-icon">🎁</div>
                    <h3>No Rewards Available</h3>
                    <p>{t('rewards.empty_state.message')} {currentUser.role.name === 'Admin' && t('rewards.empty_state.admin_hint')}</p>
                </div>
            )}

            {[1, 2, 3].map(tier => {
                const tierRewards = sortedRewards.filter(r => r.tier_level === tier);
                if (tierRewards.length === 0) return null;

                const tierTitle = t(`rewards.tier_names.${tier}`);
                let tierSubtitle = t('rewards.tier_default');
                let emoji = '🥉';
                if (tier === 2) {
                    tierSubtitle = t('rewards.tier_requires', { lp: TIER_THRESHOLDS.SILVER });
                    emoji = '🥈';
                } else if (tier === 3) {
                    tierSubtitle = t('rewards.tier_requires', { lp: TIER_THRESHOLDS.GOLD });
                    emoji = '🥇';
                }

                return (
                    <div key={tier} className="tier-section fade-in">
                        <div className="tier-section-header">
                            <h2>{emoji} {tierTitle}</h2>
                            <span className="tier-section-subtitle">{tierSubtitle}</span>
                        </div>
                        <div className="rewards-grid">
                            {tierRewards.map(reward => {
                                const progress = getProgressPercentage(reward.cost_points);
                                const affordable = canAfford(reward.cost_points);
                                const isCurrentGoal = userGoal?.id === reward.id;

                                const requiredPoints = reward.tier_level === 3 ? TIER_THRESHOLDS.GOLD
                                    : reward.tier_level === 2 ? TIER_THRESHOLDS.SILVER
                                        : TIER_THRESHOLDS.BRONZE;

                                const isLocked = !isAdmin && currentUser.lifetime_points < requiredPoints;

                                return (
                                    <RewardCard
                                        key={reward.id}
                                        reward={reward}
                                        affordable={affordable}
                                        isLocked={isLocked}
                                        isCurrentGoal={isCurrentGoal}
                                        isAdmin={isAdmin}
                                        progress={progress}
                                        getTierBadge={getTierBadge}
                                        onSetGoal={handleSetGoal}
                                        onRedeem={handleRedeemClick}
                                        onEdit={openEditForm}
                                        onDelete={(r) => setRewardToDelete(r)}
                                    />
                                );
                            })}
                        </div>
                    </div>
                );
            })}
        </div>
    );
};

export default RewardHub;
