import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
    PieChart, Pie, Cell
} from 'recharts';
import type { WeeklyStats, DistributionStat } from '../../api';
import { getWeeklyStats, getPointsDistribution } from '../../api';
import LoadingSpinner from '../../components/LoadingSpinner';
import { useToast } from '../../hooks/useToast';
import Toast from '../../components/Toast';
import './AnalyticsDashboard.css';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d'];

const AnalyticsDashboard: React.FC = () => {
    const { t } = useTranslation();
    const [weeklyData, setWeeklyData] = useState<WeeklyStats[]>([]);
    const [distributionData, setDistributionData] = useState<DistributionStat[]>([]);
    const [loading, setLoading] = useState(true);
    const { toasts, removeToast, error } = useToast();

    useEffect(() => {
        fetchAnalytics();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const fetchAnalytics = async () => {
        try {
            const [weeklyRes, distRes] = await Promise.all([
                getWeeklyStats(),
                getPointsDistribution()
            ]);
            setWeeklyData(weeklyRes.data);
            setDistributionData(distRes.data);
        } catch (err) {
            console.error("Failed to load analytics", err);
            error(t('common.error_loading'));
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return <LoadingSpinner fullPage message={t('common.loading')} />;
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
                                        name={key} // Display user name in legend
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
        </div>
    );
};

export default AnalyticsDashboard;
