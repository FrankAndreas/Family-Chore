import React from 'react';
import type { Role } from '../types';

interface TaskFormProps {
    name: string;
    setName: (value: string) => void;
    description: string;
    setDescription: (value: string) => void;
    basePoints: number;
    setBasePoints: (value: number) => void;
    assignedRoleId: number;
    setAssignedRoleId: (value: number) => void;
    scheduleType: string;
    setScheduleType: (value: string) => void;
    defaultDueTime: string;
    setDefaultDueTime: (value: string) => void;
    recurrenceMinDays: number;
    setRecurrenceMinDays: (value: number) => void;
    recurrenceMaxDays: number;
    setRecurrenceMaxDays: (value: number) => void;
    roles: Role[];
    onSubmit: (e: React.FormEvent) => void;
    onCancel?: () => void;
    error: string;
    submitButtonText?: string;
    submitting?: boolean;

}

const TaskForm: React.FC<TaskFormProps> = ({
    name,
    setName,
    description,
    setDescription,
    basePoints,
    setBasePoints,
    assignedRoleId,
    setAssignedRoleId,
    scheduleType,
    setScheduleType,
    defaultDueTime,
    setDefaultDueTime,
    recurrenceMinDays,
    setRecurrenceMinDays,
    recurrenceMaxDays,
    setRecurrenceMaxDays,
    roles,
    onSubmit,
    onCancel,
    error,
    submitButtonText = 'Create Task',
    submitting = false,

}) => {

    return (
        <form onSubmit={onSubmit} className="form-grid">
            <div className="form-group">
                <label>Task Name</label>
                <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    required
                    placeholder="e.g. Wash Dishes"
                />
            </div>
            <div className="form-group">
                <label>Description</label>
                <input
                    type="text"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    required
                    placeholder="e.g. Load and start the dishwasher"
                />
            </div>
            <div className="form-group">
                <label>Base Points</label>
                <input
                    type="number"
                    value={basePoints}
                    onChange={(e) => setBasePoints(Number(e.target.value))}
                    min={1}
                    max={1000}
                    required
                />
            </div>
            <div className="form-group">
                <label>Assigned To</label>
                <select
                    value={assignedRoleId || 0}
                    onChange={(e) => {
                        const value = Number(e.target.value);
                        setAssignedRoleId(value === 0 ? 0 : value);
                    }}
                >
                    <option value={0}>🏠 All Family Members</option>
                    {roles.map(role => (
                        <option key={role.id} value={role.id}>
                            {role.name}
                        </option>
                    ))}
                </select>
                <small style={{ color: 'var(--text-secondary)', fontSize: 'var(--font-size-xs)' }}>
                    Select "All Family Members" for tasks anyone can do
                </small>
            </div>
            <div className="form-group">
                <label>Schedule Type</label>
                <select
                    value={scheduleType}
                    onChange={(e) => {
                        const newType = e.target.value;
                        setScheduleType(newType);
                        // Reset due time to appropriate default
                        if (newType === 'daily') {
                            setDefaultDueTime('17:00');
                        } else if (newType === 'weekly') {
                            setDefaultDueTime('Monday');
                        } else {  // recurring
                            setDefaultDueTime('recurring');
                        }
                    }}
                    className="schedule-select"
                >
                    <option value="daily">📅 Daily - Task appears every day</option>
                    <option value="weekly">📆 Weekly - Task appears on specific weekday</option>
                    <option value="recurring">🔄 Recurring - Task with cooldown period</option>
                </select>
                <small style={{ color: 'var(--text-secondary)', fontSize: 'var(--font-size-xs)', marginTop: '0.25rem', display: 'block' }}>
                    {scheduleType === 'daily' && '⏰ Appears at the same time every day'}
                    {scheduleType === 'weekly' && '🗓️ Appears once per week on chosen day'}
                    {scheduleType === 'recurring' && '⏳ Reappears after cooldown period expires'}
                </small>
            </div>

            {scheduleType === 'recurring' ? (
                <>
                    <div className="recurring-fields-container" style={{
                        gridColumn: '1 / -1',
                        padding: '1.5rem',
                        background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(59, 130, 246, 0.1))',
                        borderRadius: '12px',
                        border: '1px solid rgba(139, 92, 246, 0.2)',
                        marginTop: '0.5rem'
                    }}>
                        <h4 style={{
                            margin: '0 0 1rem 0',
                            color: 'var(--primary)',
                            fontSize: '1rem',
                            fontWeight: '600',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.5rem'
                        }}>
                            🔄 Cooldown Settings
                        </h4>

                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                            <div className="form-group" style={{ margin: 0 }}>
                                <label>Minimum Days Between ⏱️</label>
                                <input
                                    type="number"
                                    value={recurrenceMinDays}
                                    onChange={(e) => {
                                        const val = Number(e.target.value);
                                        setRecurrenceMinDays(val);
                                        if (val > recurrenceMaxDays) {
                                            setRecurrenceMaxDays(val);
                                        }
                                    }}
                                    min={1}
                                    max={365}
                                    required
                                />
                                <small style={{ color: 'var(--text-secondary)', fontSize: 'var(--font-size-xs)' }}>
                                    Wait at least <strong>{recurrenceMinDays}</strong> {recurrenceMinDays === 1 ? 'day' : 'days'} after completion
                                </small>
                            </div>

                            <div className="form-group" style={{ margin: 0 }}>
                                <label>Maximum Days Between ⌛</label>
                                <input
                                    type="number"
                                    value={recurrenceMaxDays}
                                    onChange={(e) => {
                                        const val = Number(e.target.value);
                                        setRecurrenceMaxDays(val);
                                        if (val < recurrenceMinDays) {
                                            setRecurrenceMinDays(val);
                                        }
                                    }}
                                    min={1}
                                    max={365}
                                    required
                                />
                                <small style={{ color: 'var(--text-secondary)', fontSize: 'var(--font-size-xs)' }}>
                                    Should be done within <strong>{recurrenceMaxDays}</strong> {recurrenceMaxDays === 1 ? 'day' : 'days'}
                                </small>
                            </div>
                        </div>
                    </div>
                </>
            ) : (
                <div className="form-group">
                    <label>{scheduleType === 'daily' ? 'Due Time' : 'Due Day'}</label>
                    {scheduleType === 'daily' ? (
                        <input
                            type="time"
                            value={defaultDueTime}
                            onChange={(e) => setDefaultDueTime(e.target.value)}
                            required
                        />
                    ) : (
                        <select
                            value={defaultDueTime}
                            onChange={(e) => setDefaultDueTime(e.target.value)}
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
                    <small style={{ color: 'var(--text-secondary)', fontSize: 'var(--font-size-xs)' }}>
                        {scheduleType === 'daily' ? 'When the task is due each day' : 'Which day of the week this task occurs'}
                    </small>
                </div>
            )}

            <div className="form-actions" style={{ gridColumn: '1 / -1' }}>
                {onCancel && (
                    <button type="button" className="btn btn-secondary" onClick={onCancel}>
                        Cancel
                    </button>
                )}
                <button type="submit" className="btn btn-primary" disabled={submitting}>
                    {submitting ? 'Saving...' : submitButtonText}
                </button>
            </div>

            {error && <div className="error-message" style={{ gridColumn: '1 / -1' }}>{error}</div>}
        </form>
    );
};

export default TaskForm;
