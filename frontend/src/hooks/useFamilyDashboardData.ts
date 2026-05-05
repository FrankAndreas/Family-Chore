import { useState, useEffect, useCallback, useRef } from 'react';
import api from '../api';
import type { TaskInstance, User, Reward } from '../types';

const getPendingTasksPublic = () => api.get('/tasks/pending', { skipAuthRedirect: true });
const getUsersPublic = () => api.get('/users/', { skipAuthRedirect: true });
const getRewardsPublic = () => api.get('/rewards/', { skipAuthRedirect: true });

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export function useFamilyDashboardData(onTasksUpdated?: () => void, onRewardsUpdated?: (data: Record<string, unknown>) => void) {
    const [tasks, setTasks] = useState<TaskInstance[]>([]);
    const [users, setUsers] = useState<User[]>([]);
    const [rewards, setRewards] = useState<Reward[]>([]);
    const [loading, setLoading] = useState(true);
    const [connected, setConnected] = useState(false);
    const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
    const eventSourceRef = useRef<EventSource | null>(null);

    const loadData = useCallback(async () => {
        try {
            const [tasksRes, usersRes, rewardsRes] = await Promise.all([
                getPendingTasksPublic(),
                getUsersPublic(),
                getRewardsPublic()
            ]);
            setTasks(tasksRes.data);
            setUsers(usersRes.data);
            setRewards(rewardsRes.data);
            setLastUpdate(new Date());
        } catch (error) {
            console.error("Failed to load family dashboard data", error);
        } finally {
            setLoading(false);
        }
    }, []);

    const refreshTasks = useCallback(async () => {
        try {
            const tasksRes = await getPendingTasksPublic();
            setTasks(tasksRes.data);
            setLastUpdate(new Date());
        } catch (error) {
            console.error("Failed to refresh tasks", error);
        }
    }, []);

    const refreshData = useCallback(async () => {
        try {
            const [usersRes, rewardsRes] = await Promise.all([getUsersPublic(), getRewardsPublic()]);
            setUsers(usersRes.data);
            setRewards(rewardsRes.data);
            setLastUpdate(new Date());
        } catch (error) {
            console.error("Failed to refresh data", error);
        }
    }, []);

    // Provide callbacks to refs so they don't cause useEffect re-triggers
    const onTasksRef = useRef(onTasksUpdated);
    const onRewardsRef = useRef(onRewardsUpdated);

    useEffect(() => {
        onTasksRef.current = onTasksUpdated;
        onRewardsRef.current = onRewardsUpdated;
    }, [onTasksUpdated, onRewardsUpdated]);

    useEffect(() => {
        loadData();

        const token = localStorage.getItem('auth_token') || '';
        const eventSource = new EventSource(`${API_BASE}/events?token=${encodeURIComponent(token)}`);
        eventSourceRef.current = eventSource;

        eventSource.onopen = () => {
            console.log('SSE connected');
            setConnected(true);
        };

        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log('SSE event:', data);

            if (data.type === 'ping') {
                return; // Ignore keepalive to prevent unnecessary re-renders
            }

            if (data.type === 'connected') {
                setConnected(true);
            } else if (data.type === 'task_created' || data.type === 'task_completed' || data.type === 'task_deleted') {
                refreshTasks();
                if (onTasksRef.current) onTasksRef.current();
            } else if (data.type === 'reward_redeemed') {
                refreshData();
                if (onRewardsRef.current) onRewardsRef.current(data);
            }
            setLastUpdate(new Date());
        };

        eventSource.onerror = (error) => {
            console.error('SSE error:', error);
            setConnected(false);
        };

        return () => {
            if (eventSourceRef.current) {
                eventSourceRef.current.close();
            }
        };
    }, [loadData, refreshTasks, refreshData]);

    return {
        tasks,
        setTasks,
        users,
        rewards,
        loading,
        connected,
        lastUpdate,
        refreshData
    };
}
