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

export default api;
