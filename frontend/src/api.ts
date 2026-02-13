import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// User APIs
export const login = (nickname: string, login_pin: string) =>
    api.post('/login/', { nickname, login_pin });

export const getUsers = () => api.get('/users/');

export const createUser = (nickname: string, login_pin: string, role_id: number) =>
    api.post('/users/', { nickname, login_pin, role_id });

// Role APIs
export const getRoles = () => api.get('/roles/');

export const updateRole = (role_id: number, multiplier_value: number) =>
    api.put(`/roles/${role_id}`, { multiplier_value });

export const createRole = (name: string, multiplier_value: number) =>
    api.post('/roles/', { name, multiplier_value });

export const deleteRole = (role_id: number, reassign_to_role_id?: number) =>
    api.delete(`/roles/${role_id}`, { params: { reassign_to_role_id } });

export const getRoleUsers = (role_id: number) =>
    api.get(`/roles/${role_id}/users`);

// Task APIs
export const getTasks = () => api.get('/tasks/');

export const createTask = (taskData: {
    name: string;
    description: string;
    base_points: number;
    assigned_role_id: number | null;  // Can be null for "All Family Members" tasks
    schedule_type: string;
    default_due_time: string;
    recurrence_min_days?: number | null;  // For recurring tasks
    recurrence_max_days?: number | null;  // For recurring tasks
}) => api.post('/tasks/', taskData);

export const triggerDailyReset = () => api.post('/daily-reset/');

export const getUserDailyTasks = (user_id: number) =>
    api.get(`/tasks/daily/${user_id}`);

export const getPendingTasks = () => api.get('/tasks/pending');

export const completeTask = (instance_id: number, actual_user_id?: number) =>
    api.post(`/tasks/${instance_id}/complete`, null, {
        params: { actual_user_id }
    });

export const updateTask = (task_id: number, taskData: Partial<{
    name: string;
    description: string;
    base_points: number;
    assigned_role_id: number | null;
    schedule_type: string;
    default_due_time: string;
    recurrence_min_days?: number | null;
    recurrence_max_days?: number | null;
}>) => api.put(`/tasks/${task_id}`, taskData);

export const deleteTask = (task_id: number) => api.delete(`/tasks/${task_id}`);

// Task Import/Export APIs
export interface TaskImportItem {
    name: string;
    description: string;
    base_points: number;
    assigned_role: string | null;
    schedule_type: string;
    default_due_time: string;
    recurrence_min_days?: number | null;
    recurrence_max_days?: number | null;
}

export interface TasksExport {
    version: string;
    exported_at: string;
    tasks: TaskImportItem[];
}

export interface ImportResult {
    success: boolean;
    created: string[];
    skipped: string[];
    errors: string[];
    summary: string;
}

export const exportTasks = () => api.get<TasksExport>('/tasks/export');

export const importTasks = (data: { tasks: TaskImportItem[], skip_duplicates?: boolean }) =>
    api.post<ImportResult>('/tasks/import', data);


// Reward APIs
export const getRewards = () => api.get('/rewards/');

export const createReward = (rewardData: {
    name: string;
    cost_points: number;
    description?: string;
    tier_level?: number;
}) => api.post('/rewards/', rewardData);

export const setUserGoal = (user_id: number, reward_id: number) =>
    api.post(`/users/${user_id}/goal?reward_id=${reward_id}`);

export interface RedemptionResponse {
    success: boolean;
    transaction_id?: number;
    reward_name?: string;
    points_spent?: number;
    remaining_points?: number;
    error?: string;
}

export const redeemReward = (reward_id: number, user_id: number) =>
    api.post<RedemptionResponse>(`/rewards/${reward_id}/redeem`, null, {
        params: { user_id }
    });

export interface SplitContribution {
    user_id: number;
    points: number;
}

export interface SplitRedemptionResponse {
    success: boolean;
    reward_name?: string;
    total_points?: number;
    transactions?: { user_id: number; user_name: string; points: number; transaction_id: number }[];
    error?: string;
}


export const redeemRewardSplit = (reward_id: number, contributions: SplitContribution[]) =>
    api.post<SplitRedemptionResponse>(`/rewards/${reward_id}/redeem-split`, { contributions });


// Transaction APIs
export interface TransactionHeader {
    skip?: number;
    limit?: number;
    type?: string;
    search?: string;
    start_date?: string;
    end_date?: string;
    user_id?: number;
}

export const getUserTransactions = (user_id: number, filters: TransactionHeader = {}) =>
    api.get(`/users/${user_id}/transactions`, { params: { skip: 0, limit: 100, ...filters } });


export const getAllTransactions = (filters: TransactionHeader = {}) =>
    api.get('/transactions', { params: { skip: 0, limit: 100, ...filters } });

// Analytics APIs
export interface WeeklyStats {
    date: string;
    [user: string]: number | string; // Date + dynamic user keys
}

export interface DistributionStat {
    name: string;
    value: number;
    role: string;
}

export const getWeeklyStats = () => api.get<WeeklyStats[]>('/analytics/weekly');

export const getPointsDistribution = () => api.get<DistributionStat[]>('/analytics/distribution');

// Notification APIs
export const getUserNotifications = (user_id: number, unreadOnly = false) =>
    api.get<import('./types').Notification[]>(`/notifications/${user_id}`, { params: { unread_only: unreadOnly } });

export const markNotificationRead = (notification_id: number, user_id: number) =>
    api.post<import('./types').Notification>(`/notifications/${notification_id}/read`, null, { params: { user_id } });

export const markAllNotificationsRead = (user_id: number) =>
    api.post<boolean>('/notifications/read-all', null, { params: { user_id } });

export default api;

