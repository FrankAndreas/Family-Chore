import { useState, useEffect, useRef } from 'react';
import { getPendingTasks, getUsers, completeTask } from '../api';
import type { TaskInstance, User } from '../types';
import './FamilyDashboard.css';

interface ClaimModalProps {
    taskName: string;
    users: User[];
    onSelectUser: (userId: number) => void;
    onClose: () => void;
}

function ClaimModal({ taskName, users, onSelectUser, onClose }: ClaimModalProps) {
    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content glass-card" onClick={e => e.stopPropagation()}>
                <h2>Who did it?</h2>
                <p>Completing: <strong>{taskName}</strong></p>

                <div className="user-grid">
                    {users.map(user => (
                        <div
                            key={user.id}
                            className="user-select-card"
                            onClick={() => onSelectUser(user.id)}
                        >
                            <div className="user-avatar">
                                {user.nickname.charAt(0).toUpperCase()}
                            </div>
                            <div className="user-name">{user.nickname}</div>
                        </div>
                    ))}
                </div>

                <button className="btn btn-secondary" style={{ marginTop: '2rem', width: '100%' }} onClick={onClose}>
                    Cancel
                </button>
            </div>
        </div>
    );
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001';

export default function FamilyDashboard({ onExit }: { onExit: () => void }) {
    const [tasks, setTasks] = useState<TaskInstance[]>([]);
    const [users, setUsers] = useState<User[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedTask, setSelectedTask] = useState<TaskInstance | null>(null);
    const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
    const [connected, setConnected] = useState(false);
    const eventSourceRef = useRef<EventSource | null>(null);

    useEffect(() => {
        loadData();

        // Connect to Server-Sent Events for real-time updates
        const eventSource = new EventSource(`${API_BASE}/events`);
        eventSourceRef.current = eventSource;

        eventSource.onopen = () => {
            console.log('SSE connected');
            setConnected(true);
        };

        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log('SSE event:', data);

            if (data.type === 'connected') {
                setConnected(true);
            } else if (data.type === 'task_created' || data.type === 'task_completed' || data.type === 'task_deleted') {
                // Refresh tasks when any task-related event occurs
                refreshTasks();
            }
            setLastUpdate(new Date());
        };

        eventSource.onerror = (error) => {
            console.error('SSE error:', error);
            setConnected(false);
        };

        // Cleanup on unmount
        return () => {
            if (eventSourceRef.current) {
                eventSourceRef.current.close();
            }
        };
    }, []);

    const loadData = async () => {
        try {
            const [tasksRes, usersRes] = await Promise.all([
                getPendingTasks(),
                getUsers()
            ]);
            setTasks(tasksRes.data);
            setUsers(usersRes.data);
            setLastUpdate(new Date());
        } catch (error) {
            console.error("Failed to load family dashboard data", error);
        } finally {
            setLoading(false);
        }
    };

    const refreshTasks = async () => {
        try {
            const tasksRes = await getPendingTasks();
            setTasks(tasksRes.data);
            setLastUpdate(new Date());
        } catch (error) {
            console.error("Failed to refresh tasks", error);
        }
    };

    const handleCompleteClick = (task: TaskInstance) => {
        setSelectedTask(task);
    };

    const handleUserSelect = async (userId: number) => {
        if (!selectedTask) return;

        try {
            await completeTask(selectedTask.id, userId);
            // Refresh list
            setTasks(prev => prev.filter(t => t.id !== selectedTask.id));
            setSelectedTask(null);
        } catch (error) {
            console.error("Failed to complete task", error);
            alert("Error completing task");
        }
    };

    // Group tasks by assigned user
    const groupedTasks = users.reduce((acc, user) => {
        acc[user.id] = tasks.filter(t => t.user_id === user.id);
        return acc;
    }, {} as Record<number, TaskInstance[]>);

    // Create a group for unassigned or unknown users if any (safety check)
    const unknownTasks = tasks.filter(t => !users.find(u => u.id === t.user_id));

    if (loading) return <div className="loading">Loading Family Board...</div>;

    return (
        <div className="family-dashboard">
            <div className="family-dashboard-header">
                <div>
                    <h1>🏡 Family Dashboard</h1>
                    <p>See what needs to be done, regardless of who does it.</p>
                    <small style={{ color: 'rgba(255,255,255,0.5)', fontSize: '0.75rem' }}>
                        {connected ? '🟢 Live updates' : '🔴 Reconnecting...'} • Last: {lastUpdate.toLocaleTimeString()}
                    </small>
                </div>
                <button className="btn btn-secondary" onClick={onExit}>
                    Back to Login
                </button>
            </div>

            {users.map(user => {
                const userTasks = groupedTasks[user.id] || [];
                if (userTasks.length === 0) return null;

                return (
                    <div key={user.id} className="user-group">
                        <h3>{user.nickname}'s Tasks</h3>
                        <div className="tasks-grid">
                            {userTasks.map(instance => (
                                <div key={instance.id} className="task-card glass-card">
                                    <div>
                                        <h4>{instance.task?.name || `Task #${instance.task_id}`}</h4>
                                        <p className="task-desc">{instance.task?.description}</p>
                                        <div className="task-info">
                                            <span className="task-points">💎 {instance.task?.base_points} pts</span>
                                            <span>📅 {instance.due_time.split('T')[0]}</span>
                                        </div>
                                    </div>
                                    <button
                                        className="btn btn-primary btn-complete"
                                        onClick={() => handleCompleteClick(instance)}
                                    >
                                        ✅ Done
                                    </button>
                                </div>
                            ))}
                        </div>
                    </div>
                );
            })}

            {/* Fallback for unassigned tasks */}
            {unknownTasks.length > 0 && (
                <div className="user-group">
                    <h3>Unassigned / Other</h3>
                    <div className="tasks-grid">
                        {unknownTasks.map(instance => (
                            <div key={instance.id} className="task-card glass-card">
                                <h4>{instance.task?.name}</h4>
                                <button
                                    className="btn btn-primary"
                                    onClick={() => handleCompleteClick(instance)}
                                >
                                    Done
                                </button>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {tasks.length === 0 && (
                <div className="empty-state">
                    <h2>🎉 All caught up! No pending tasks.</h2>
                </div>
            )}

            {selectedTask && (
                <ClaimModal
                    taskName={selectedTask.task?.name || 'Task'}
                    users={users}
                    onSelectUser={handleUserSelect}
                    onClose={() => setSelectedTask(null)}
                />
            )}
        </div>
    );
}
