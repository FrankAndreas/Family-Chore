import { useTranslation } from 'react-i18next';
import type { Reward } from '../../../types';

interface RewardCardProps {
    reward: Reward;
    affordable: boolean;
    isLocked: boolean;
    isCurrentGoal: boolean;
    isAdmin: boolean;
    progress: number;
    getTierBadge: (tier: number) => React.ReactNode;
    onSetGoal: (rewardId: number) => void;
    onRedeem: (reward: Reward) => void;
    onEdit: (reward: Reward) => void;
    onDelete: (reward: Reward) => void;
}

export default function RewardCard({
    reward,
    affordable,
    isLocked,
    isCurrentGoal,
    isAdmin,
    progress,
    getTierBadge,
    onSetGoal,
    onRedeem,
    onEdit,
    onDelete,
}: RewardCardProps) {
    const { t } = useTranslation();

    return (
        <div
            className={`reward-card glass-panel ${affordable && !isLocked ? 'affordable pulse-affordable' : ''} ${isCurrentGoal ? 'current-goal' : ''} ${isLocked ? 'locked' : ''}`}
        >
            {isLocked && (
                <div className="locked-overlay">
                    🔒 {t('rewards.card.locked_label')}
                </div>
            )}

            {isCurrentGoal && <div className="goal-indicator">{t('rewards.card.goal_indicator')}</div>}

            <div className="reward-header">
                <h3>{reward.name}</h3>
                <div className="reward-header-actions">
                    {getTierBadge(reward.tier_level)}
                    {isAdmin && (
                        <div className="admin-actions">
                            <button
                                className="icon-btn edit-btn"
                                onClick={() => onEdit(reward)}
                                title="Edit Reward"
                            >
                                ✏️
                            </button>
                            <button
                                className="icon-btn delete-btn"
                                onClick={() => onDelete(reward)}
                                title="Delete Reward"
                            >
                                🗑️
                            </button>
                        </div>
                    )}
                </div>
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
                    onClick={() => onSetGoal(reward.id)}
                >
                    {t('rewards.card.set_goal_button')}
                </button>
            )}

            {affordable && !isLocked && (
                <button
                    className="btn btn-success btn-block mt-sm"
                    onClick={() => onRedeem(reward)}
                >
                    🎉 {t('rewards.redeem_button')}
                </button>
            )}

            {affordable && !isLocked && (
                <div className="affordable-badge">{t('rewards.card.can_afford_badge')}</div>
            )}
        </div>
    );
}
