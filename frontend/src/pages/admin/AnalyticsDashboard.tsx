import React, { useEffect, useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { useOutletContext, Navigate } from 'react-router-dom';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
    PieChart, Pie, Cell
} from 'recharts';
import type { WeeklyStats, DistributionStat, HeatmapResponse, AnalyticsSummary } from '../../api';
import { getWeeklyStats, getPointsDistribution, getHeatmapData, getAnalyticsSummary } from '../../api';
import type { User } from '../../types';
import { SkeletonLoader } from '../../components/SkeletonLoader';
import { useToast } from '../../hooks/useToast';
import Toast from '../../components/Toast';
import StatCards from '../../components/StatCards';
import Heatmap from '../../components/Heatmap';
import TimeRangeSelector from '../../components/TimeRangeSelector';
import './AnalyticsDashboard.css';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d'];

interface DashboardContext {
    currentUser: User;
}

const AnalyticsDashboard: React.FC = () => {
    const { t } = useTranslation();
    const { currentUser } = useOutletContext<DashboardContext>();
    const [weeklyData, setWeeklyData] = useState<WeeklyStats[]>([]);
    const [distributionData, setDistributionData] = useState<DistributionStat[]>([]);
    const [heatmapData, setHeatmapData] = useState<HeatmapResponse | null>(null);
    const [summaryData, setSummaryData] = useState<AnalyticsSummary | null>(null);
    const [heatmapDays, setHeatmapDays] = useState(30);
    const [loading, setLoading] = useState(true);
    const [heatmapLoading, setHeatmapLoading] = useState(false);
    const { toasts, removeToast, error } = useToast();

    useEffect(() => {
        if (currentUser.role.name === 'Admin') {
            fetchAnalytics();
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [currentUser]);

    const fetchAnalytics = async () => {
        try {
            const [weeklyRes, distRes, heatmapRes, summaryRes] = await Promise.all([
                getWeeklyStats(),
                getPointsDistribution(),
                getHeatmapData(heatmapDays),
                getAnalyticsSummary(),
            ]);
            setWeeklyData(weeklyRes.data);
            setDistributionData(distRes.data);
            setHeatmapData(heatmapRes.data);
            setSummaryData(summaryRes.data);
        } catch (err) {
            console.error("Failed to load analytics", err);
            error(t('common.error_loading'));
        } finally {
            setLoading(false);
        }
    };

    const handleTimeRangeChange = useCallback(async (days: number) => {
        setHeatmapDays(days);
        setHeatmapLoading(true);
        try {
            const res = await getHeatmapData(days);
            setHeatmapData(res.data);
        } catch (err) {
            console.error("Failed to reload heatmap", err);
            error(t('common.error_loading'));
        } finally {
            setHeatmapLoading(false);
        }
    }, [error, t]);

    if (currentUser.role.name !== 'Admin') {
        return <Navigate to="/dashboard" replace />;
    }

    if (loading) {
        return (
            <div className="page-container analytics-dashboard fade-in">
                <header className="page-header mb-4">
                    <SkeletonLoader type="title" className="mb-2" />
                    <SkeletonLoader type="text" className="w-64" />
                </header>

                {/* Summary Stat Cards */}
                <div className="stats-grid" style={{ marginBottom: '2rem' }}>
                    <SkeletonLoader type="card" count={4} />
                </div>

                <div className="analytics-grid">
                    <div className="glass-panel chart-card" style={{ minHeight: '400px' }}>
                        <SkeletonLoader type="title" className="mb-4" />
                        <SkeletonLoader type="card" className="h-full" style={{ minHeight: '300px' }} />
                    </div>
                </div>
            </div>
        );
    }

    // Extract unique user names from weekly data keys (excluding 'date') for BarChart lines
    const allKeys = weeklyData.reduce((keys, entry) => {
        Object.keys(entry).forEach(k => {
            if (k !== 'date' && !keys.includes(k)) {
                keys.push(k);
            }
        });
        return keys;
    }, [] as string[]);

    // Custom Tooltip for Pie Chart
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const CustomPieTooltip = ({ active, payload }: { active?: boolean; payload?: any[] }) => {
        if (active && payload && payload.length) {
            const data = payload[0].payload;
            return (
                <div className="custom-tooltip">
                    <p className="label">{`${data.name}`}</p>
                    <p className="intro">{`${t('analytics.points')}: ${data.value}`}</p>
                    <p className="intro">{`${data.role}`}</p>
                </div>
            );
        }
        return null;
    };

    return (
        <div className="page-container analytics-dashboard fade-in">
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
                    <h1 className="page-title">📊 {t('analytics.title')}</h1>
                    <p className="page-subtitle">{t('analytics.subtitle')}</p>
                </div>
            </header>

            {/* Summary Stat Cards */}
            <StatCards summary={summaryData} />

            <div className="analytics-grid">
                {/* Weekly Activity Chart */}
                <div className="glass-panel chart-card">
                    <h2>📅 {t('analytics.weekly_activity')}</h2>
                    <div className="chart-container">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart
                                data={weeklyData}
                                margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                            >
                                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                <XAxis dataKey="date" stroke="#ccc" />
                                <YAxis stroke="#ccc" />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#1a1a2e', borderColor: '#333', color: '#fff' }}
                                    itemStyle={{ color: '#fff' }}
                                    cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                                />
                                <Legend />
                                {allKeys.map((key, index) => (
                                    <Bar
                                        key={key}
                                        dataKey={key}
                                        stackId="a"
                                        fill={COLORS[index % COLORS.length]}
                                        name={key}
                                        animationDuration={1500}
                                    />
                                ))}
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Fairness / Distribution Chart */}
                <div className="glass-panel chart-card">
                    <h2>⚖️ {t('analytics.fairness_distribution')}</h2>
                    <div className="chart-container">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={distributionData}
                                    cx="50%"
                                    cy="50%"
                                    labelLine={false}
                                    label={({ name, percent }) => `${name} ${(percent ? percent * 100 : 0).toFixed(0)}%`}
                                    outerRadius={100}
                                    fill="#8884d8"
                                    dataKey="value"
                                    animationDuration={1500}
                                >
                                    {distributionData.map((_entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip content={<CustomPieTooltip />} />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            {/* Family Progress Heatmap */}
            {heatmapData && heatmapData.users.length > 0 && (
                <section className="heatmap-section">
                    <div className="heatmap-section__header">
                        <h2 className="section-title">
                            🗓️ {t('analytics.family_heatmap', { days: heatmapDays, defaultValue: 'Family Progress (Last {{days}} Days)' })}
                        </h2>
                        <TimeRangeSelector
                            selectedDays={heatmapDays}
                            onChange={handleTimeRangeChange}
                        />
                    </div>
                    {heatmapLoading ? (
                        <div className="glass-panel" style={{ minHeight: '300px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                            <div style={{ width: '100%', padding: '2rem' }}>
                                <SkeletonLoader type="title" className="mb-4" />
                                <div style={{ display: 'flex', gap: '8px' }}>
                                    {Array.from({ length: 12 }).map((_, i) => (
                                        <div key={i} style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                                            {Array.from({ length: 7 }).map((_, j) => (
                                                <div key={j} style={{ width: '15px', height: '15px', borderRadius: '4px', background: 'rgba(255,255,255,0.05)' }} />
                                            ))}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="heatmap-grid-container">
                            {heatmapData.users.map(user => (
                                <Heatmap
                                    key={user.user_id}
                                    nickname={user.nickname}
                                    userId={user.user_id}
                                    days={user.days}
                                />
                            ))}
                        </div>
                    )}
                </section>
            )}
        </div>
    );
};

export default AnalyticsDashboard;
