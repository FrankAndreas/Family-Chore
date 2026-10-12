import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import UserDashboard from './UserDashboard';
import { UserContext } from '../../context/UserContext';
import type { UserContextType } from '../../context/UserContext';
import { getUserDailyTasks, getTasks, getUserTransactions } from '../../api';

vi.mock('react-i18next', () => {
    // Stable like the real hook's t, so effects depending on it don't re-run
    const t = (key: string, opt?: string | { defaultValue?: string }) =>
        typeof opt === 'string' ? opt : opt?.defaultValue ?? key;
    return { useTranslation: () => ({ t }) };
});

const showToast = vi.fn();
vi.mock('../../context/ToastContext', () => ({
    useToast: () => ({ showToast }),
}));

vi.mock('../../api', () => ({
    getUserDailyTasks: vi.fn(),
    getTasks: vi.fn(),
    getUserTransactions: vi.fn(),
    completeTask: vi.fn(),
    uploadTaskPhoto: vi.fn(),
}));

const PAGE_SIZE = 50;

const makeTransactions = (count: number, startId: number, label: string) =>
    Array.from({ length: count }, (_, i) => ({
        id: startId + i,
        user_id: 1,
        type: 'EARN',
        base_points_value: 10,
        multiplier_used: 1,
        awarded_points: 10,
        description: `${label} ${startId + i}`,
        timestamp: '2026-10-01T10:00:00Z',
    }));

const user = {
    id: 1,
    nickname: 'Kid',
    current_points: 10,
    current_streak: 0,
    last_task_date: null,
    role: { id: 1, name: 'Child', multiplier_value: 1 },
};

const renderDashboard = () =>
    render(
        <UserContext.Provider value={{ currentUser: user, refreshUser: async () => {}, logout: () => {} } as unknown as UserContextType}>
            <UserDashboard />
        </UserContext.Provider>
    );

const historyRows = () => screen.queryAllByText(/^(page|search) \d+$/);

describe('UserDashboard data loading', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        vi.mocked(getUserDailyTasks).mockResolvedValue({
            data: [{ id: 7, task_id: 3, user_id: 1, status: 'PENDING', due_time: '2026-10-01T18:00:00Z' }],
        } as never);
        vi.mocked(getTasks).mockResolvedValue({
            data: [{ id: 3, name: 'Make Bed', description: 'Tidy up', base_points: 10 }],
        } as never);
        vi.mocked(getUserTransactions).mockImplementation(async (_userId, params) => {
            const skip = params?.skip ?? 0;
            const label = params?.search ? 'search' : 'page';
            // Searches return a short single page; unfiltered history has two full pages
            const count = params?.search ? 3 : PAGE_SIZE;
            return { data: makeTransactions(count, skip + 1, label) } as never;
        });
    });

    it('loads the task list once on mount', async () => {
        renderDashboard();
        expect(await screen.findByText('Make Bed')).toBeInTheDocument();
        expect(getUserDailyTasks).toHaveBeenCalledTimes(1);
        expect(getUserTransactions).not.toHaveBeenCalled();
    });

    it('pages history, then restarts from page 1 when the search changes', async () => {
        renderDashboard();
        await screen.findByText('Make Bed');

        fireEvent.click(screen.getByText(/History/));
        await waitFor(() => expect(historyRows()).toHaveLength(PAGE_SIZE));
        expect(getUserTransactions).toHaveBeenLastCalledWith(1, expect.objectContaining({ skip: 0, limit: PAGE_SIZE }));

        fireEvent.click(screen.getByText('Load More'));
        await waitFor(() => expect(historyRows()).toHaveLength(PAGE_SIZE * 2));
        expect(getUserTransactions).toHaveBeenLastCalledWith(1, expect.objectContaining({ skip: PAGE_SIZE }));

        // A new search replaces the list instead of appending to page 2
        fireEvent.change(screen.getByPlaceholderText('Search description...'), { target: { value: 'bed' } });
        await waitFor(() => expect(screen.getAllByText(/^search \d+$/)).toHaveLength(3));
        expect(screen.queryAllByText(/^page \d+$/)).toHaveLength(0);
        expect(getUserTransactions).toHaveBeenLastCalledWith(1, expect.objectContaining({ skip: 0, search: 'bed' }));
    });

    it('reloads history from page 1 when returning to the tab', async () => {
        renderDashboard();
        await screen.findByText('Make Bed');

        fireEvent.click(screen.getByText(/History/));
        await waitFor(() => expect(historyRows()).toHaveLength(PAGE_SIZE));
        fireEvent.click(screen.getByText('Load More'));
        await waitFor(() => expect(historyRows()).toHaveLength(PAGE_SIZE * 2));

        fireEvent.click(screen.getByText(/My Tasks|Tasks/));
        await screen.findByText('Make Bed');
        fireEvent.click(screen.getByText(/History/));

        // No duplicated pages: back to exactly the first page
        await waitFor(() => expect(historyRows()).toHaveLength(PAGE_SIZE));
        expect(getUserTransactions).toHaveBeenLastCalledWith(1, expect.objectContaining({ skip: 0 }));
    });
});
