import type { ReactNode } from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { UserContext } from '../context/UserContext';
import type { UserContextType } from '../context/UserContext';
import * as api from '../api';
import AdminDashboard from './admin/AdminDashboard';
import AnalyticsDashboard from './admin/AnalyticsDashboard';
import RoleManagement from './admin/RoleManagement';
import TaskManagement from './admin/TaskManagement';
import UserManagement from './admin/UserManagement';
import RewardHub from './user/RewardHub';

vi.mock('react-i18next', () => {
    // Stable like the real hook's t, so effects depending on it don't re-run
    const t = (key: string, opt?: string | { defaultValue?: string }) =>
        typeof opt === 'string' ? opt : opt?.defaultValue ?? key;
    const i18n = { language: 'en', changeLanguage: () => {} };
    return {
        useTranslation: () => ({ t, i18n }),
        Trans: ({ i18nKey, children }: { i18nKey?: string; children?: ReactNode }) => children ?? i18nKey,
    };
});

const showToast = vi.fn();
vi.mock('../context/ToastContext', () => ({
    useToast: () => ({ showToast }),
}));

vi.mock('../api', () => ({
    getRoles: vi.fn(),
    getUsersAdmin: vi.fn(),
    getTasks: vi.fn(),
    getRewards: vi.fn(),
    getAllTransactions: vi.fn(),
    getReviewQueue: vi.fn(),
    getWeeklyStats: vi.fn(),
    getPointsDistribution: vi.fn(),
    getHeatmapData: vi.fn(),
    getAnalyticsSummary: vi.fn(),
}));

const role = { id: 1, name: 'Admin', multiplier_value: 1 };
const admin = {
    id: 1, nickname: 'Admin', role_id: 1, role, current_points: 0, lifetime_points: 0,
    current_streak: 0, last_task_date: null, current_goal_reward_id: null,
};
const child = { ...admin, id: 2, nickname: 'Kiddo', role: { id: 2, name: 'Child', multiplier_value: 1 }, role_id: 2 };

const ok = (data: unknown) => Promise.resolve({ data } as never);

const renderPage = (page: ReactNode) =>
    render(
        <MemoryRouter>
            <UserContext.Provider value={{ currentUser: admin, refreshUser: async () => {}, logout: () => {} } as unknown as UserContextType}>
                {page}
            </UserContext.Provider>
        </MemoryRouter>
    );

describe('pages load their data on mount', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        vi.mocked(api.getRoles).mockImplementation(() => ok([role, child.role]));
        vi.mocked(api.getUsersAdmin).mockImplementation(() => ok([admin, child]));
        vi.mocked(api.getTasks).mockImplementation(() => ok([{
            id: 1, name: 'Make Bed', description: 'Tidy up', base_points: 10, assigned_role_id: 2,
            schedule_type: 'daily', default_due_time: '08:00', requires_photo_verification: false,
        }]));
        vi.mocked(api.getRewards).mockImplementation(() => ok([{ id: 1, name: 'Ice Cream', cost_points: 50, description: 'Yum', tier_level: 1 }]));
        vi.mocked(api.getAllTransactions).mockImplementation(() => ok([]));
        vi.mocked(api.getReviewQueue).mockImplementation(() => ok([]));
        vi.mocked(api.getWeeklyStats).mockImplementation(() => ok([]));
        vi.mocked(api.getPointsDistribution).mockImplementation(() => ok([]));
        vi.mocked(api.getHeatmapData).mockImplementation(() => ok({ users: [] }));
        vi.mocked(api.getAnalyticsSummary).mockImplementation(() => ok({ week_total_tasks: 0, top_performer: null, streaks: [] }));
    });

    it('RoleManagement', async () => {
        renderPage(<RoleManagement />);
        expect(await screen.findByText('Child')).toBeInTheDocument();
        expect(api.getRoles).toHaveBeenCalledTimes(1);
    });

    it('UserManagement', async () => {
        renderPage(<UserManagement />);
        expect(await screen.findByText('Kiddo')).toBeInTheDocument();
        expect(api.getUsersAdmin).toHaveBeenCalledTimes(1);
    });

    it('TaskManagement', async () => {
        renderPage(<TaskManagement />);
        expect(await screen.findByText('Make Bed')).toBeInTheDocument();
        expect(api.getTasks).toHaveBeenCalledTimes(1);
    });

    it('RewardHub', async () => {
        renderPage(<RewardHub />);
        expect(await screen.findByText('Ice Cream')).toBeInTheDocument();
        expect(api.getRewards).toHaveBeenCalledTimes(1);
    });

    it('AdminDashboard', async () => {
        renderPage(<AdminDashboard />);
        await waitFor(() => expect(api.getAllTransactions).toHaveBeenCalledTimes(1));
        expect(api.getAllTransactions).toHaveBeenCalledWith({ limit: 50, search: undefined });
        expect(await screen.findByText('No recent activity matching your filters.')).toBeInTheDocument();
    });

    it('AnalyticsDashboard', async () => {
        renderPage(<AnalyticsDashboard />);
        await waitFor(() => expect(api.getHeatmapData).toHaveBeenCalledWith(30));
        expect(api.getAnalyticsSummary).toHaveBeenCalledTimes(1);
        await waitFor(() => expect(document.querySelector('.skeleton, [class*="skeleton"]')).toBeNull());
    });
});
