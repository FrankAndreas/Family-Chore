import React from 'react';
import { useTranslation } from 'react-i18next';
import type { Role } from '../types';
import './TaskForm.css';

export interface TaskFormData {
    name: string;
    description: string;
    basePoints: number;
    assignedRoleId: number;
    scheduleType: string;
    defaultDueTime: string;
    recurrenceMinDays: number;
    recurrenceMaxDays: number;
}

interface TaskFormProps {
    formData: TaskFormData;
    onChange: (updates: Partial<TaskFormData>) => void;
    roles: Role[];
    onSubmit: (e: React.FormEvent) => void;
    onCancel?: () => void;
    error: string;
    submitButtonText?: string;
    submitting?: boolean;
}

const TaskForm: React.FC<TaskFormProps> = ({
    formData,
    onChange,
    roles,
    onSubmit,
    onCancel,
    error,
    submitButtonText = 'Create Task',
    submitting = false,

}) => {
    const { t } = useTranslation();
    const [nameError, setNameError] = React.useState('');
    const [descError, setDescError] = React.useState('');
    const [pointsError, setPointsError] = React.useState('');
    const [minDaysError, setMinDaysError] = React.useState('');

    const validate = () => {
        let valid = true;
        if (!formData.name.trim()) {
            setNameError('Task name is required');
            valid = false;
        } else {
            setNameError('');
        }

        if (!formData.description.trim()) {
            setDescError('Description is required');
            valid = false;
        } else {
            setDescError('');
        }

        if (formData.basePoints < 1) {
            setPointsError('Base points must be at least 1');
            valid = false;
        } else {
            setPointsError('');
        }

        if (formData.scheduleType === 'recurring') {
            if (formData.recurrenceMinDays < 1) {
                setMinDaysError('Minimum days must be at least 1');
                valid = false;
            } else if (formData.recurrenceMinDays > formData.recurrenceMaxDays) {
                setMinDaysError('Minimum days cannot exceed maximum days');
                valid = false;
            } else {
                setMinDaysError('');
            }
        }

        return valid;
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (validate()) {
            onSubmit(e);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="form-grid task-form">
            <div className="form-group">
                <label htmlFor="taskName">Task Name</label>
                <input
                    id="taskName"
                    type="text"
                    value={formData.name}
                    className={nameError ? 'error-input' : ''}
                    onChange={(e) => {
                        onChange({ name: e.target.value });
                        if (nameError) setNameError('');
                    }}
                    onBlur={validate}
                    required
                    placeholder="e.g. Wash Dishes"
                />
                {nameError && <small className="error-text">{nameError}</small>}
            </div>
            <div className="form-group">
                <label htmlFor="taskDescription">Description</label>
                <input
                    id="taskDescription"
                    type="text"
                    value={formData.description}
                    className={descError ? 'error-input' : ''}
                    onChange={(e) => {
                        onChange({ description: e.target.value });
                        if (descError) setDescError('');
                    }}
                    onBlur={validate}
                    required
                    placeholder="e.g. Load and start the dishwasher"
                />
                {descError && <small className="error-text">{descError}</small>}
            </div>
            <div className="form-group">
                <label htmlFor="taskBasePoints">Base Points</label>
                <input
                    id="taskBasePoints"
                    type="number"
                    value={formData.basePoints}
                    className={pointsError ? 'error-input' : ''}
                    onChange={(e) => {
                        onChange({ basePoints: Number(e.target.value) });
                        if (pointsError) setPointsError('');
                    }}
                    onBlur={validate}
                    min={1}
                    max={1000}
                    required
                />
                {pointsError && <small className="error-text">{pointsError}</small>}
            </div>
            <div className="form-group">
                <label>Assigned To</label>
                <select
                    value={formData.assignedRoleId || 0}
                    onChange={(e) => {
                        const value = Number(e.target.value);
                        onChange({ assignedRoleId: value === 0 ? 0 : value });
                    }}
                >
                    <option value={0}>🏠 All Family Members</option>
                    {roles.map(role => (
                        <option key={role.id} value={role.id}>
                            {role.name}
                        </option>
                    ))}
                </select>
                <small className="help-text">
                    Select "All Family Members" for tasks anyone can do
                </small>
            </div>
            <div className="form-group">
                <label>Schedule Type</label>
                <select
                    value={formData.scheduleType}
                    onChange={(e) => {
                        const newType = e.target.value;
                        const updates: Partial<TaskFormData> = { scheduleType: newType };
                        // Reset due time to appropriate default
                        if (newType === 'daily') {
                            updates.defaultDueTime = '17:00';
                        } else if (newType === 'weekly') {
                            updates.defaultDueTime = 'Monday';
                        } else {  // recurring
                            updates.defaultDueTime = 'recurring';
                        }
                        onChange(updates);
                    }}
                    className="schedule-select"
                >
                    <option value="daily">📅 Daily - Task appears every day</option>
                    <option value="weekly">📆 Weekly - Task appears on specific weekday</option>
                    <option value="recurring">🔄 Recurring - Task with cooldown period</option>
                </select>
                <small className="help-text-block">
                    {formData.scheduleType === 'daily' && '⏰ Appears at the same time every day'}
                    {formData.scheduleType === 'weekly' && '🗓️ Appears once per week on chosen day'}
                    {formData.scheduleType === 'recurring' && '⏳ Reappears after cooldown period expires'}
                </small>
            </div>

            {formData.scheduleType === 'recurring' ? (
                <>
                    <div className="recurring-fields-container">
                        <h4 className="recurring-header">
                            🔄 Cooldown Settings
                        </h4>

                        <div className="recurring-grid">
                            <div className="form-group form-group-no-margin">
                                <label>Minimum Days Between ⏱️</label>
                                <input
                                    type="number"
                                    value={formData.recurrenceMinDays}
                                    className={minDaysError ? 'error-input' : ''}
                                    onChange={(e) => {
                                        const val = Number(e.target.value);
                                        const updates: Partial<TaskFormData> = { recurrenceMinDays: val };
                                        if (val > formData.recurrenceMaxDays) {
                                            updates.recurrenceMaxDays = val;
                                        }
                                        onChange(updates);
                                        if (minDaysError) setMinDaysError('');
                                    }}
                                    onBlur={validate}
                                    min={1}
                                    max={365}
                                    required
                                />
                                {minDaysError && <small className="error-text">{minDaysError}</small>}
                                <small className="help-text">
                                    Wait at least <strong>{formData.recurrenceMinDays}</strong> {t('tasks.days_count', { count: formData.recurrenceMinDays })} after completion
                                </small>
                            </div>

                            <div className="form-group form-group-no-margin">
                                <label>Maximum Days Between ⌛</label>
                                <input
                                    type="number"
                                    value={formData.recurrenceMaxDays}
                                    onChange={(e) => {
                                        const val = Number(e.target.value);
                                        const updates: Partial<TaskFormData> = { recurrenceMaxDays: val };
                                        if (val < formData.recurrenceMinDays) {
                                            updates.recurrenceMinDays = val;
                                        }
                                        onChange(updates);
                                    }}
                                    min={1}
                                    max={365}
                                    required
                                />
                                <small className="help-text">
                                    Should be done within <strong>{formData.recurrenceMaxDays}</strong> {t('tasks.days_count', { count: formData.recurrenceMaxDays })}
                                </small>
                            </div>
                        </div>
                    </div>
                </>
            ) : (
                <div className="form-group">
                    <label>{formData.scheduleType === 'daily' ? 'Due Time' : 'Due Day'}</label>
                    {formData.scheduleType === 'daily' ? (
                        <input
                            type="time"
                            value={formData.defaultDueTime}
                            onChange={(e) => onChange({ defaultDueTime: e.target.value })}
                            required
                        />
                    ) : (
                        <select
                            value={formData.defaultDueTime}
                            onChange={(e) => onChange({ defaultDueTime: e.target.value })}
                            required
                        >
                            <option value="Monday">Monday</option>
                            <option value="Tuesday">Tuesday</option>
                            <option value="Wednesday">Wednesday</option>
                            <option value="Thursday">Thursday</option>
                            <option value="Friday">Friday</option>
                            <option value="Saturday">Saturday</option>
                            <option value="Sunday">Sunday</option>
                        </select>
                    )}
                    <small className="help-text">
                        {formData.scheduleType === 'daily' ? 'When the task is due each day' : 'Which day of the week this task occurs'}
                    </small>
                </div>
            )}

            <div className="form-actions form-actions-full">
                {onCancel && (
                    <button type="button" className="btn btn-secondary" onClick={onCancel}>
                        Cancel
                    </button>
                )}
                <button type="submit" className="btn btn-primary" disabled={submitting}>
                    {submitting ? 'Saving...' : submitButtonText}
                </button>
            </div>

            {error && <div className="error-message error-message-full">{error}</div>}
        </form>
    );
};

export default TaskForm;
