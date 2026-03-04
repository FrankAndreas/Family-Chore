import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import type { AnalyticsSummary } from '../api';
import './StatCards.css';

interface StatCardsProps {
    summary: AnalyticsSummary | null;
}

/** Animated count-up hook */
const useCountUp = (target: number, durationMs = 800): number => {
    const [value, setValue] = useState(target);

    useEffect(() => {
        if (target === 0) return;
        let start = 0;
        const step = Math.max(1, Math.ceil(target / (durationMs / 16)));
        const timer = setInterval(() => {
            start += step;
            if (start >= target) {
                setValue(target);
                clearInterval(timer);
            } else {
                setValue(start);
            }
        }, 16);
        return () => clearInterval(timer);
    }, [target, durationMs]);

    return value;
};

const StatCards: React.FC<StatCardsProps> = ({ summary }) => {
    const { t } = useTranslation();

    const weekTotal = useCountUp(summary?.week_total_tasks ?? 0);
    const topCount = useCountUp(summary?.top_performer?.count ?? 0);
    const bestStreak = useCountUp(
        summary?.streaks?.[0]?.current_streak ?? 0,
    );

    const topName = summary?.top_performer?.nickname ?? '—';
    const streakName = summary?.streaks?.[0]?.nickname ?? '—';

    return (
        <div className="stat-cards-row">
            {/* Tasks This Week */}
            <div className="stat-card glass-panel stat-card--tasks">
                <div className="stat-card__icon">📋</div>
                <div className="stat-card__body">
                    <span className="stat-card__value">{weekTotal}</span>
                    <span className="stat-card__label">
                        {t('analytics.tasks_this_week', 'Tasks This Week')}
                    </span>
                </div>
            </div>

            {/* Top Performer */}
            <div className="stat-card glass-panel stat-card--top">
                <div className="stat-card__icon">🏆</div>
                <div className="stat-card__body">
                    <span className="stat-card__value">{topName}</span>
                    <span className="stat-card__label">
                        {topCount} {t('analytics.tasks_lowercase', 'tasks')} ·{' '}
                        {t('analytics.top_performer', 'Top Performer')}
                    </span>
                </div>
            </div>

            {/* Longest Active Streak */}
            <div className="stat-card glass-panel stat-card--streak">
                <div className="stat-card__icon">🔥</div>
                <div className="stat-card__body">
                    <span className="stat-card__value">
                        {bestStreak} {t('analytics.days', 'days')}
                    </span>
                    <span className="stat-card__label">
                        {streakName} · {t('analytics.best_streak', 'Best Streak')}
                    </span>
                </div>
            </div>
        </div>
    );
};

export default StatCards;
