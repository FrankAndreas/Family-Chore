import React, { useState, useEffect } from 'react';
import { getTasks, createTask, updateTask, deleteTask, getRoles, exportTasks } from '../../api';
import type { Task, Role } from '../../types';
import { SkeletonLoader } from '../../components/SkeletonLoader';
import Modal from '../../components/Modal';
import TaskForm, { type TaskFormData } from '../../components/TaskForm';
import ImportTasksModal from '../../components/ImportTasksModal';
import { useToast } from '../../context/ToastContext';
import { useTranslation } from 'react-i18next';
import '../../styles/SharedDashboard.css';
import './Dashboard.css';

// Extracted sub-components (C2 decomposition)
import DeleteTaskModal from './TaskManagement/DeleteTaskModal';
import TaskRoleGroup from './TaskManagement/TaskRoleGroup';

const TaskManagement: React.FC = () => {
    const { t } = useTranslation();
    const [tasks, setTasks] = useState<Task[]>([]);
    const [roles, setRoles] = useState<Role[]>([]);
    const [loading, setLoading] = useState(true);
    const [showAddForm, setShowAddForm] = useState(false);
    const [showEditModal, setShowEditModal] = useState(false);
    const [showImportModal, setShowImportModal] = useState(false);
    const [taskToDelete, setTaskToDelete] = useState<Task | null>(null);
    const [editingTask, setEditingTask] = useState<Task | null>(null);
    const [submitting, setSubmitting] = useState(false);
    const { showToast } = useToast();

    // Form state
    const [formData, setFormData] = useState<TaskFormData>({
        name: '',
        description: '',
        basePoints: 10,
        assignedRoleId: 0,
        scheduleType: 'daily',
        defaultDueTime: '17:00',
        recurrenceMinDays: 3,
        recurrenceMaxDays: 5
    });
    const [error, setError] = useState('');

    useEffect(() => {
        fetchData();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const fetchData = async () => {
        setLoading(true);
        setError('');
        try {
            const [tasksRes, rolesRes] = await Promise.all([getTasks(), getRoles()]);
            setTasks(tasksRes.data);
            setRoles(rolesRes.data);
            if (rolesRes.data.length > 0 && formData.assignedRoleId === 0) {
                setFormData(prev => ({ ...prev, assignedRoleId: rolesRes.data[0].id }));
            }
        } catch (err: unknown) {
            console.error('Failed to fetch data', err);
            let errorMsg = 'Failed to load tasks and roles. Please verify database connection and schema.';
            if (err && typeof err === 'object' && 'response' in err) {
                const response = (err as { response: { data?: { detail?: string } } }).response;
                errorMsg = response?.data?.detail || errorMsg;
            }
            setError(errorMsg);
            showToast(errorMsg, 'error');
        } finally {
            setLoading(false);
        }
    };

    const resetForm = () => {
        setFormData({
            name: '',
            description: '',
            basePoints: 10,
            assignedRoleId: roles.length > 0 ? roles[0].id : 0,
            scheduleType: 'daily',
            defaultDueTime: '17:00',
            recurrenceMinDays: 3,
            recurrenceMaxDays: 5
        });
        setError('');
    };

    const fillFormWithTask = (task: Task) => {
        setFormData({
            name: task.name,
            description: task.description,
            basePoints: task.base_points,
            assignedRoleId: task.assigned_role_id || 0,
            scheduleType: task.schedule_type,
            defaultDueTime: task.default_due_time,
            recurrenceMinDays: task.recurrence_min_days || 3,
            recurrenceMaxDays: task.recurrence_max_days || 5
        });
        setError('');
    };

    const handleEditClick = (task: Task) => {
        setEditingTask(task);
        fillFormWithTask(task);
        setShowEditModal(true);
        setShowAddForm(false);
    };

    const handleCancelEdit = () => {
        setShowEditModal(false);
        setEditingTask(null);
        resetForm();
    };

    const handleCopyTask = (task: Task) => {
        fillFormWithTask(task);

        const baseName = task.name.replace(/ \(Copy( \d+)?\)$/, '');
        let copyName = `${baseName} (Copy)`;
        let counter = 2;

        while (tasks.some(t => t.name === copyName)) {
            copyName = `${baseName} (Copy ${counter})`;
            counter++;
        }

        setFormData(prev => ({ ...prev, name: copyName }));
        setShowAddForm(true);
        setShowEditModal(false);
        showToast('Task copied to form. Edit and save as new task.', 'success');
    };

    const handleExport = async () => {
        try {
            const response = await exportTasks();
            const json = JSON.stringify(response.data, null, 2);
            const blob = new Blob([json], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `tasks-export-${new Date().toISOString().split('T')[0]}.json`;
            a.click();
            URL.revokeObjectURL(url);
            showToast(`Exported ${response.data.tasks.length} tasks`, 'success');
        } catch (err) {
            console.error('Failed to export tasks', err);
            showToast('Failed to export tasks', 'error');
        }
    };

    const handleDeleteConfirm = async (task: Task) => {
        try {
            await deleteTask(task.id);
            showToast(`Task "${task.name}" deleted successfully`, 'success');
            fetchData();
        } catch (err) {
            console.error('Failed to delete task', err);
            showToast('Failed to delete task', 'error');
        } finally {
            setTaskToDelete(null);
        }
    };

    const handleCreateTask = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setSubmitting(true);

        try {
            await createTask({
                name: formData.name,
                description: formData.description,
                base_points: formData.basePoints,
                assigned_role_id: formData.assignedRoleId === 0 ? null : formData.assignedRoleId,
                schedule_type: formData.scheduleType,
                default_due_time: formData.scheduleType === 'recurring' ? 'recurring' : formData.defaultDueTime,
                recurrence_min_days: formData.scheduleType === 'recurring' ? formData.recurrenceMinDays : null,
                recurrence_max_days: formData.scheduleType === 'recurring' ? formData.recurrenceMaxDays : null
            });
            showToast('Task created successfully! 🎉', 'success');
            setShowAddForm(false);
            resetForm();
            fetchData();
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } catch (err: any) {
            const errorMsg = err.response?.data?.detail || 'Failed to create task';
            setError(errorMsg);
            showToast(errorMsg, 'error');
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
                name: formData.name,
                description: formData.description,
                base_points: formData.basePoints,
                assigned_role_id: formData.assignedRoleId === 0 ? null : formData.assignedRoleId,
                schedule_type: formData.scheduleType,
                default_due_time: formData.scheduleType === 'recurring' ? 'recurring' : formData.defaultDueTime,
                recurrence_min_days: formData.scheduleType === 'recurring' ? formData.recurrenceMinDays : null,
                recurrence_max_days: formData.scheduleType === 'recurring' ? formData.recurrenceMaxDays : null
            });
            showToast('Task updated successfully! ✅', 'success');
            setShowEditModal(false);
            setEditingTask(null);
            resetForm();
            fetchData();
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } catch (err: any) {
            const errorMsg = err.response?.data?.detail || 'Failed to update task';
            setError(errorMsg);
            showToast(errorMsg, 'error');
        } finally {
            setSubmitting(false);
        }
    };

    // Get schedule icon and label
    const getScheduleInfo = (type: string) => {
        switch (type) {
            case 'daily': return { icon: '📅', label: 'Daily', color: '#3b82f6' };
            case 'weekly': return { icon: '📆', label: 'Weekly', color: '#8b5cf6' };
            case 'recurring': return { icon: '🔄', label: 'Recurring', color: '#10b981' };
            default: return { icon: '📋', label: type, color: '#6b7280' };
        }
    };

    if (loading) {
        return (
            <div className="page-container fade-in">
                <header className="page-header">
                    <SkeletonLoader type="title" className="mb-2" />
                    <SkeletonLoader type="text" className="w-64" />
                </header>
                <div className="tasks-grid">
                    <SkeletonLoader type="card" count={6} />
                </div>
            </div>
        );
    }

    // Create groups: null role first, then each role
    const allFamilyTasks = tasks.filter(t => !t.assigned_role_id);
    const roleGroups = roles.map(role => ({
        role,
        tasks: tasks.filter(t => t.assigned_role_id === role.id)
    })).filter(g => g.tasks.length > 0);

    return (
        <div className="page-container fade-in">
            {/* Delete Confirmation Modal */}
            <DeleteTaskModal
                task={taskToDelete}
                onClose={() => setTaskToDelete(null)}
                onConfirm={handleDeleteConfirm}
            />

            {/* Edit Task Modal */}
            <Modal
                isOpen={showEditModal}
                onClose={handleCancelEdit}
                title={`Edit Task: ${editingTask?.name || ''}`}
                size="large"
            >
                <TaskForm
                    formData={formData}
                    onChange={(updates) => setFormData(prev => ({ ...prev, ...updates }))}
                    roles={roles}
                    onSubmit={handleUpdateTask}
                    onCancel={handleCancelEdit}
                    error={error}
                    submitButtonText="Update Task"
                    submitting={submitting}
                />
            </Modal>

            {/* Import Modal */}
            <ImportTasksModal
                isOpen={showImportModal}
                onClose={() => setShowImportModal(false)}
                onSuccess={() => {
                    fetchData();
                    showToast('Tasks imported successfully!', 'success');
                }}
            />

            <header className="page-header">
                <div className="header-content">
                    <div>
                        <h1 className="page-title">Task Management</h1>
                        <p className="page-subtitle">{t('tasks.subtitle', 'Create and manage household chores')}</p>
                    </div>
                    <div className="header-actions" style={{ display: 'flex', gap: '0.5rem' }}>
                        <button
                            className="btn btn-secondary"
                            onClick={handleExport}
                            title="Export all tasks as JSON"
                        >
                            📤 Export
                        </button>
                        <button
                            className="btn btn-secondary"
                            onClick={() => setShowImportModal(true)}
                            title="Import tasks from JSON"
                        >
                            📥 Import
                        </button>
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
                </div>
            </header>

            {showAddForm && (
                <div className="section glass-panel mb-xl fade-in">
                    <h2>Add New Task</h2>
                    <TaskForm
                        formData={formData}
                        onChange={(updates) => setFormData(prev => ({ ...prev, ...updates }))}
                        roles={roles}
                        onSubmit={handleCreateTask}
                        error={error}
                        submitButtonText="Create Task"
                        submitting={submitting}
                    />
                </div>
            )}

            {tasks.length === 0 && !error && (
                <div className="empty-state">
                    <p>No tasks yet. Create one to get started!</p>
                </div>
            )}

            {error && (
                <div className="empty-state" style={{ borderColor: '#ef4444' }}>
                    <p style={{ color: '#ef4444' }}>⚠️ {error}</p>
                    <button className="btn btn-secondary btn-sm mt-m" onClick={fetchData}>
                        Retry Loading
                    </button>
                </div>
            )}

            {/* All Family Members section */}
            <TaskRoleGroup
                title={t('tasks.allFamilyMembers', 'All Family Members')}
                titleColor="#10b981"
                titleEmoji="🏠"
                badgeBackground="rgba(16, 185, 129, 0.2)"
                tasks={allFamilyTasks}
                roles={roles}
                getScheduleInfo={getScheduleInfo}
                onEdit={handleEditClick}
                onCopy={handleCopyTask}
                onDelete={(task) => setTaskToDelete(task)}
            />

            {/* Role-specific sections */}
            {roleGroups.map(({ role, tasks: roleTasks }) => (
                <TaskRoleGroup
                    key={role.id}
                    title={role.name}
                    titleColor="#8b5cf6"
                    titleEmoji="👤"
                    badgeBackground="rgba(139, 92, 246, 0.2)"
                    tasks={roleTasks}
                    roles={roles}
                    subtitle={`${role.multiplier_value}x`}
                    getScheduleInfo={getScheduleInfo}
                    onEdit={handleEditClick}
                    onCopy={handleCopyTask}
                    onDelete={(task) => setTaskToDelete(task)}
                />
            ))}
        </div>
    );
};

export default TaskManagement;
