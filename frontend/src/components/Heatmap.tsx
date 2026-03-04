import React, { useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import type { HeatmapDay, HeatmapDayDetails } from '../api';
import { getHeatmapDayDetails } from '../api';
import './Heatmap.css';

interface HeatmapProps {
    days: HeatmapDay[];
    nickname: string;
    userId: number;
}

const DAY_LABELS = ['M', 'T', 'W', 'T', 'F', 'S', 'S'];

const intensityClass = (count: number): string => {
    if (count === 0) return 'heatmap-cell--empty';
    if (count <= 1) return 'heatmap-cell--low';
    if (count <= 3) return 'heatmap-cell--mid';
    if (count <= 5) return 'heatmap-cell--high';
    return 'heatmap-cell--max';
};

const Heatmap: React.FC<HeatmapProps> = ({ days, nickname, userId }) => {
    const { t } = useTranslation();
    const [tooltip, setTooltip] = useState<{ x: number; y: number; text: string } | null>(null);
    const [popup, setPopup] = useState<{ x: number; y: number; details: HeatmapDayDetails } | null>(null);
    const [loadingPopup, setLoadingPopup] = useState(false);

    const handleMouseEnter = useCallback(
        (e: React.MouseEvent<HTMLDivElement>, day: HeatmapDay) => {
            if (popup) return; // Don't show tooltip while popup is open
            const rect = e.currentTarget.getBoundingClientRect();
            setTooltip({
                x: rect.left + rect.width / 2,
                y: rect.top - 8,
                text: `${day.date}: ${day.count} ${t('analytics.tasks_lowercase', 'tasks')}`,
            });
        },
        [t, popup],
    );

    const handleMouseLeave = useCallback(() => {
        if (!popup) setTooltip(null);
    }, [popup]);

    const handleCellClick = useCallback(
        async (e: React.MouseEvent<HTMLDivElement>, day: HeatmapDay) => {
            if (day.count === 0) return; // Nothing to show
            setTooltip(null);
            setLoadingPopup(true);

            const rect = e.currentTarget.getBoundingClientRect();

            try {
                const res = await getHeatmapDayDetails(userId, day.date);
                setPopup({
                    x: rect.left + rect.width / 2,
                    y: rect.bottom + 8,
                    details: res.data,
                });
            } catch (err) {
                console.error('Failed to load heatmap details', err);
            } finally {
                setLoadingPopup(false);
            }
        },
        [userId],
    );

    const closePopup = useCallback(() => setPopup(null), []);

    // Pad days so the grid starts on Monday
    const firstDate = days.length > 0 ? new Date(days[0].date) : new Date();
    const startDow = (firstDate.getDay() + 6) % 7; // 0=Mon
    const paddedDays: (HeatmapDay | null)[] = [
        ...Array.from<null>({ length: startDow }).fill(null),
        ...days,
    ];

    return (
        <div className="heatmap-card glass-panel">
            <h3 className="heatmap-title">{nickname}</h3>

            {/* Day-of-week labels */}
            <div className="heatmap-wrapper">
                <div className="heatmap-labels">
                    {DAY_LABELS.map((l, i) => (
                        <span key={i} className="heatmap-label">{l}</span>
                    ))}
                </div>

                <div className="heatmap-grid">
                    {paddedDays.map((day, i) =>
                        day ? (
                            <div
                                key={day.date}
                                className={`heatmap-cell ${intensityClass(day.count)} ${day.count > 0 ? 'heatmap-cell--clickable' : ''}`}
                                onMouseEnter={(e) => handleMouseEnter(e, day)}
                                onMouseLeave={handleMouseLeave}
                                onClick={(e) => handleCellClick(e, day)}
                            />
                        ) : (
                            <div key={`pad-${i}`} className="heatmap-cell heatmap-cell--pad" />
                        ),
                    )}
                </div>
            </div>

            {/* Hover tooltip */}
            {tooltip && !loadingPopup && (
                <div
                    className="heatmap-tooltip"
                    style={{ left: tooltip.x, top: tooltip.y }}
                >
                    {tooltip.text}
                </div>
            )}

            {/* Click popup with task details */}
            {popup && (
                <>
                    <div className="heatmap-overlay" onClick={closePopup} />
                    <div
                        className="heatmap-popup"
                        style={{ left: popup.x, top: popup.y }}
                    >
                        <div className="heatmap-popup__header">
                            <strong>{popup.details.date}</strong>
                            <button className="heatmap-popup__close" onClick={closePopup}>✕</button>
                        </div>
                        <ul className="heatmap-popup__list">
                            {popup.details.tasks.map((task, i) => (
                                <li key={i} className="heatmap-popup__item">
                                    <span className="heatmap-popup__task-name">{task.task_name}</span>
                                    <span className="heatmap-popup__points">+{task.base_points} pts</span>
                                </li>
                            ))}
                        </ul>
                        {popup.details.tasks.length === 0 && (
                            <p className="heatmap-popup__empty">
                                {t('analytics.no_tasks', 'No tasks found')}
                            </p>
                        )}
                    </div>
                </>
            )}
        </div>
    );
};

export default Heatmap;
