import { useTranslation } from 'react-i18next';
import type { User, Reward } from '../../types';

export interface RedeemTabProps {
    users: User[];
    rewards: Reward[];
    redeeming: boolean;
    handleRedeemClick: (reward: Reward) => void;
}

export default function RedeemTab({
    users,
    rewards,
    redeeming,
    handleRedeemClick,
}: RedeemTabProps) {
    const { t } = useTranslation();

    const getAffordableRewards = (user: User) => {
        return rewards.filter(r => user.current_points >= r.cost_points);
    };

    return (
        <div className="tab-content fade-in">
            {users.map(user => {
                const affordable = getAffordableRewards(user);
                if (affordable.length === 0) return null;

                return (
                    <div key={user.id} className="user-group">
                        <h3>
                            {user.nickname}
                            <span className="user-points-badge">💎 {user.current_points} {t('common.pts', 'pts')}</span>
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
                                            💰 {reward.cost_points} {t('common.pts', 'pts')}
                                        </div>
                                    </div>
                                    <button
                                        className="btn btn-success btn-redeem"
                                        disabled={redeeming}
                                        onClick={() => handleRedeemClick(reward)}
                                    >
                                        {t('dashboard.redeemReward', '🎁 Redeem')}
                                    </button>
                                </div>
                            ))}
                        </div>
                    </div>
                );
            })}

            {users.every(u => getAffordableRewards(u).length === 0) && (
                <div className="empty-state">
                    <div className="empty-state-icon">😢</div>
                    <h3>{t('dashboard.noAffordableRewardsTitle', 'No affordable rewards yet')}</h3>
                    <p>{t('dashboard.noAffordableRewardsDesc', 'Complete more tasks to earn points!')}</p>
                </div>
            )}
        </div>
    );
}
