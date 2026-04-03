import { useTranslation } from 'react-i18next';
import { triggerConfetti } from '../../../utils/confetti';

interface TierStats {
    current: string;
    next: string;
    target: number;
    percent: number;
}

interface TierProgressBarProps {
    tierStats: TierStats;
    lifetimePoints: number;
}

export default function TierProgressBar({ tierStats, lifetimePoints }: TierProgressBarProps) {
    const { t } = useTranslation();

    return (
        <div className="tier-progress-container glass-panel">
            <div className="tier-header">
                <h2>
                    <span style={{ fontSize: '24px', cursor: 'pointer' }} onClick={triggerConfetti}>
                        {tierStats.current === 'Gold' ? '🥇' : tierStats.current === 'Silver' ? '🥈' : '🥉'}
                    </span>
                    {t('rewards.tier_progress.title', { tier: tierStats.current })}
                </h2>
                <span className="tier-info">
                    {tierStats.current === 'Gold'
                        ? t('rewards.tier_progress.max_level')
                        : `${lifetimePoints} / ${tierStats.target} LP`}
                </span>
            </div>
            <div className="tier-progress-bar">
                <div
                    className="tier-progress-fill"
                    style={{ width: `${tierStats.percent}%` }}
                ></div>
            </div>
        </div>
    );
}
