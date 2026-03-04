import React from 'react';
import { useTranslation } from 'react-i18next';
import './TimeRangeSelector.css';

interface TimeRangeOption {
    label: string;
    value: number;
}

interface TimeRangeSelectorProps {
    selectedDays: number;
    onChange: (days: number) => void;
}

const TimeRangeSelector: React.FC<TimeRangeSelectorProps> = ({ selectedDays, onChange }) => {
    const { t } = useTranslation();

    const options: TimeRangeOption[] = [
        { label: t('analytics.range_7d', '7d'), value: 7 },
        { label: t('analytics.range_14d', '14d'), value: 14 },
        { label: t('analytics.range_30d', '30d'), value: 30 },
        { label: t('analytics.range_60d', '60d'), value: 60 },
        { label: t('analytics.range_90d', '90d'), value: 90 },
    ];

    return (
        <div className="time-range-selector">
            <span className="time-range-selector__label">
                🕐 {t('analytics.time_range', 'Time Range')}
            </span>
            <div className="time-range-selector__buttons">
                {options.map((opt) => (
                    <button
                        key={opt.value}
                        className={`time-range-btn ${selectedDays === opt.value ? 'time-range-btn--active' : ''}`}
                        onClick={() => onChange(opt.value)}
                    >
                        {opt.label}
                    </button>
                ))}
            </div>
        </div>
    );
};

export default TimeRangeSelector;
