export interface Role {
    id: number;
    name: string;
    multiplier_value: number;
}

export interface User {
    id: number;
    nickname: string;
    role_id: number;
    role: Role;
    current_points: number;
    lifetime_points: number;
    current_goal_reward_id: number | null;
    current_streak: number;
    last_task_date: string | null;
}

export interface Task {
    id: number;
    name: string;
    description: string;
    base_points: number;
    assigned_role_id: number | null;
    schedule_type: string;
    default_due_time: string;
    recurrence_min_days?: number | null;
    recurrence_max_days?: number | null;
}

export interface TaskInstance {
    id: number;
    task_id: number;
    user_id: number;
    due_time: string;
    completed_at: string | null;
    status: string;
    completion_photo_url: string | null;
    task?: Task;
    user?: User;
}

export interface Notification {
    id: number;
    user_id: number;
    type: string; // 'TASK_ASSIGNED', 'TASK_COMPLETED', 'REWARD_REDEEMED', 'SYSTEM'
    title: string;
    message: string;
    read: number; // 0 or 1
    created_at: string;
    data?: string;
}

export interface Reward {
    id: number;
    name: string;
    cost_points: number;
    description: string | null;
    tier_level: number;
}

export interface Transaction {
    id: number;
    user_id: number;
    type: string;
    base_points_value: number;
    multiplier_used: number;
    awarded_points: number;
    description: string | null;
    reference_instance_id: number | null;
    timestamp: string;
}

export interface TransactionFilters {
    user_id?: number;
    type?: string;
    search?: string;
    limit?: number;
    offset?: number;
}
