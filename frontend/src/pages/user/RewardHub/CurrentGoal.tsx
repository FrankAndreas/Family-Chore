import { useTranslation } from 'react-i18next';
import type { Reward } from '../../../types';

interface CurrentGoalProps {
    goal: Reward;
    currentPoints: number;
    canAfford: boolean;
    getProgressPercentage: (cost: number) => number;
    getTierBadge: (tier: number) => React.ReactNode;
}

export default function CurrentGoal({ goal, currentPoints, canAfford, getProgressPercentage, getTierBadge }: CurrentGoalProps) {
    const { t } = useTranslation();
    const progress = getProgressPercentage(goal.cost_points);

    return (
        <div className="current-goal glass-panel mb-lg">
            <div className="goal-header">
                <h2>{t('rewards.card.goal_indicator')}</h2>
                {canAfford && (
                    <div className="ready-badge pulse">{t('rewards.current_goal.ready')}</div>
                )}
            </div>
            <div className="goal-content">
                <div className="goal-info">
                    <h3>{goal.name}</h3>
                    <p>{goal.description}</p>
                    <div className="goal-stats">
                        <span className="cost">{t('rewards.card.points_val', { points: goal.cost_points })}</span>
                        {getTierBadge(goal.tier_level)}
                    </div>
                </div>
                <div className="goal-progress">
                    <div className="progress-stats">
                        <span>{currentPoints} / {goal.cost_points}</span>
                        <span>{progress}%</span>
                    </div>
                    <div className="progress-bar">
                        <div
                            className="progress-fill"
                            style={{ width: `${progress}%` }}
                        ></div>
                    </div>
                    <div className="points-needed">
                        {canAfford
                            ? t('rewards.current_goal.achieved')
                            : t('rewards.current_goal.points_needed', { points: goal.cost_points - currentPoints })
                        }
                    </div>
                </div>
            </div>
        </div>
    );
}
