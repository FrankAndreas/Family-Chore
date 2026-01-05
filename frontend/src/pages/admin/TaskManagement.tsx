import React, { useState, useEffect } from 'react';
import { getTasks, createTask, updateTask, getRoles } from '../../api';
import type { Task, Role } from '../../types';
import LoadingSpinner from '../../components/LoadingSpinner';
import Toast from '../../components/Toast';
import Modal from '../../components/Modal';
import TaskForm from '../../components/TaskForm';
import { useToast } from '../../hooks/useToast';
import './Dashboard.css';

const TaskManagement: React.FC = () => {
    const [tasks, setTasks] = useState<Task[]>([]);
    const [roles, setRoles] = useState<Role[]>([]);
    const [loading, setLoading] = useState(true);
    const [showAddForm, setShowAddForm] = useState(false);
    const [showEditModal, setShowEditModal] = useState(false);
    const [editingTask, setEditingTask] = useState<Task | null>(null);
    const [submitting, setSubmitting] = useState(false);
    const { toasts, removeToast, success, error: showError } = useToast();

    // Form state
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');
    const [basePoints, setBasePoints] = useState<number>(10);
    const [assignedRoleId, setAssignedRoleId] = useState<number>(0);
    const [scheduleType, setScheduleType] = useState('daily');
    const [defaultDueTime, setDefaultDueTime] = useState('17:00');
    const [recurrenceMinDays, setRecurrenceMinDays] = useState<number>(3);
    const [recurrenceMaxDays, setRecurrenceMaxDays] = useState<number>(5);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchData();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const fetchData = async () => {
        try {
            const [tasksRes, rolesRes] = await Promise.all([getTasks(), getRoles()]);
            setTasks(tasksRes.data);
            setRoles(rolesRes.data);
            if (rolesRes.data.length > 0 && assignedRoleId === 0) {
                setAssignedRoleId(rolesRes.data[0].id);
            }
        } catch (err) {
            console.error('Failed to fetch data', err);
            showError('Failed to load tasks and roles');
        } finally {
            setLoading(false);
        }
    };

    const resetForm = () => {
        setName('');
        setDescription('');
        setBasePoints(10);
        setAssignedRoleId(roles.length > 0 ? roles[0].id : 0);
        setScheduleType('daily');
        setDefaultDueTime('17:00');
        setRecurrenceMinDays(3);
        setRecurrenceMaxDays(5);
        setError('');
    };

    const fillFormWithTask = (task: Task) => {
        setName(task.name);
        setDescription(task.description);
        setBasePoints(task.base_points);
        setAssignedRoleId(task.assigned_role_id || 0);
        setScheduleType(task.schedule_type);
        setDefaultDueTime(task.default_due_time);
        setRecurrenceMinDays(task.recurrence_min_days || 3);
        setRecurrenceMaxDays(task.recurrence_max_days || 5);
        setError('');
    };

    const handleEditClick = (task: Task) => {
        setEditingTask(task);
        fillFormWithTask(task);
        setShowEditModal(true);
        setShowAddForm(false);  // Close add form if open
    };

    const handleCancelEdit = () => {
        setShowEditModal(false);
        setEditingTask(null);
        resetForm();
    };

    const handleCreateTask = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setSubmitting(true);

        try {
            await createTask({
                name,
                description,
                base_points: basePoints,
                assigned_role_id: assignedRoleId === 0 ? null : assignedRoleId,
                schedule_type: scheduleType,
                default_due_time: scheduleType === 'recurring' ? 'recurring' : defaultDueTime,
                recurrence_min_days: scheduleType === 'recurring' ? recurrenceMinDays : null,
                recurrence_max_days: scheduleType === 'recurring' ? recurrenceMaxDays : null
            });
            success('Task created successfully! 🎉');
            setShowAddForm(false);
            resetForm();
            fetchData();
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } catch (err: any) {
            const errorMsg = err.response?.data?.detail || 'Failed to create task';
            setError(errorMsg);
            showError(errorMsg);
        } finally {
            setSubmitting(false);
        }
    };

    const handleUpdateTask = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!editingTask) return;

        setError('');
        setSubmitting(true);

        try {
            await updateTask(editingTask.id, {
                name,
                description,
                base_points: basePoints,
                assigned_role_id: assignedRoleId === 0 ? null : assignedRoleId,
                schedule_type: scheduleType,
                default_due_time: scheduleType === 'recurring' ? 'recurring' : defaultDueTime,
                recurrence_min_days: scheduleType === 'recurring' ? recurrenceMinDays : null,
                recurrence_max_days: scheduleType === 'recurring' ? recurrenceMaxDays : null
            });
            success('Task updated successfully! ✅');
            setShowEditModal(false);
            setEditingTask(null);
            resetForm();
            fetchData();
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } catch (err: any) {
            const errorMsg = err.response?.data?.detail || 'Failed to update task';
            setError(errorMsg);
            showError(errorMsg);
        } finally {
            setSubmitting(false);
        }
    };

    if (loading) return <LoadingSpinner fullPage message="Loading tasks..." />;

    // Get schedule icon and label
    const getScheduleInfo = (type: string) => {
        switch (type) {
            case 'daily': return { icon: '📅', label: 'Daily', color: '#3b82f6' };
            case 'weekly': return { icon: '📆', label: 'Weekly', color: '#8b5cf6' };
            case 'recurring': return { icon: '🔄', label: 'Recurring', color: '#10b981' };
            default: return { icon: '📋', label: type, color: '#6b7280' };
        }
    };

    return (
        <div className="page-container fade-in">
            {/* Toast notifications */}
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

            {/* Edit Task Modal */}
            <Modal
                isOpen={showEditModal}
                onClose={handleCancelEdit}
                title={`Edit Task: ${editingTask?.name || ''}`}
                size="large"
            >
                <TaskForm
                    name={name}
                    setName={setName}
                    description={description}
                    setDescription={setDescription}
                    basePoints={basePoints}
                    setBasePoints={setBasePoints}
                    assignedRoleId={assignedRoleId}
                    setAssignedRoleId={setAssignedRoleId}
                    scheduleType={scheduleType}
                    setScheduleType={setScheduleType}
                    defaultDueTime={defaultDueTime}
                    setDefaultDueTime={setDefaultDueTime}
                    recurrenceMinDays={recurrenceMinDays}
                    setRecurrenceMinDays={setRecurrenceMinDays}
                    recurrenceMaxDays={recurrenceMaxDays}
                    setRecurrenceMaxDays={setRecurrenceMaxDays}
                    roles={roles}
                    onSubmit={handleUpdateTask}
                    onCancel={handleCancelEdit}
                    error={error}
                    submitButtonText="Update Task"
                    submitting={submitting}
                />
            </Modal>

            <header className="page-header">
                <div className="header-content">
                    <div>
                        <h1 className="page-title">Task Management</h1>
                        <p className="page-subtitle">Create and manage household chores</p>
                    </div>
                    <button
                        className="btn btn-primary"
                        onClick={() => {
                            setShowAddForm(!showAddForm);
                            if (!showAddForm) {
                                resetForm();
                            }
                        }}
                    >
                        {showAddForm ? 'Cancel' : '+ Add New Task'}
                    </button>
                </div>
            </header>

            {showAddForm && (
                <div className="section glass-panel mb-xl fade-in">
                    <h2>Add New Task</h2>
                    <TaskForm
                        name={name}
                        setName={setName}
                        description={description}
                        setDescription={setDescription}
                        basePoints={basePoints}
                        setBasePoints={setBasePoints}
                        assignedRoleId={assignedRoleId}
                        setAssignedRoleId={setAssignedRoleId}
                        scheduleType={scheduleType}
                        setScheduleType={setScheduleType}
                        defaultDueTime={defaultDueTime}
                        setDefaultDueTime={setDefaultDueTime}
                        recurrenceMinDays={recurrenceMinDays}
                        setRecurrenceMinDays={setRecurrenceMinDays}
                        recurrenceMaxDays={recurrenceMaxDays}
                        setRecurrenceMaxDays={setRecurrenceMaxDays}
                        roles={roles}
                        onSubmit={handleCreateTask}
                        error={error}
                        submitButtonText="Create Task"
                        submitting={submitting}
                    />
                </div>
            )}

            <div className="tasks-grid">
                {tasks.length === 0 && (
                    <div className="empty-state">
                        <p>No tasks yet. Create one to get started!</p>
                    </div>
                )}

                {tasks.map(task => {
                    const role = task.assigned_role_id ? roles.find(r => r.id === task.assigned_role_id) : null;
                    const assignedTo = role ? role.name : '🏠 All Family Members';
                    const scheduleInfo = getScheduleInfo(task.schedule_type);

                    return (
                        <div key={task.id} className="task-card glass-panel">
                            <div className="task-header">
                                <div className="task-icon">{scheduleInfo.icon}</div>
                                <div className="task-info">
                                    <h3>{task.name}</h3>
                                    <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginTop: '0.25rem' }}>
                                        <span className="role-badge">{assignedTo}</span>
                                        <span
                                            className="schedule-badge"
                                            style={{
                                                background: `linear-gradient(135deg, ${scheduleInfo.color}22, ${scheduleInfo.color}11)`,
                                                border: `1px solid ${scheduleInfo.color}44`,
                                                color: scheduleInfo.color,
                                                padding: '0.125rem 0.5rem',
                                                borderRadius: '12px',
                                                fontSize: '0.75rem',
                                                fontWeight: '600'
                                            }}
                                        >
                                            {scheduleInfo.icon} {scheduleInfo.label}
                                        </span>
                                    </div>
                                </div>
                                <div className="task-points">
                                    <span className="points-value">{task.base_points}</span>
                                    <span className="points-label">pts</span>
                                </div>
                            </div>
                            <p className="task-description">{task.description}</p>
                            <div className="task-footer">
                                <div className="task-meta">
                                    {task.schedule_type === 'daily' && (
                                        <span>🕒 Due at {task.default_due_time}</span>
                                    )}
                                    {task.schedule_type === 'weekly' && (
                                        <span>📅 Every {task.default_due_time}</span>
                                    )}
                                    {task.schedule_type === 'recurring' && (
                                        <span>⏳ Cooldown: {task.recurrence_min_days}-{task.recurrence_max_days} days</span>
                                    )}
                                </div>
                                <button
                                    className="btn btn-secondary btn-sm"
                                    onClick={() => handleEditClick(task)}
                                    style={{ marginLeft: 'auto' }}
                                >
                                    ✏️ Edit
                                </button>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default TaskManagement;
