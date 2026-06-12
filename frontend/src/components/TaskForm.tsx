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
    submitButtonText,
    submitting = false,
}) => {
    const { t } = useTranslation();
    const [nameError, setNameError] = React.useState('');
    const [descError, setDescError] = React.useState('');
    const [pointsError, setPointsError] = React.useState('');
    const [minDaysError, setMinDaysError] = React.useState('');

    const validateField = (field: string) => {
        if (field === 'name' || field === 'all') {
            if (!formData.name.trim()) {
                setNameError(t('tasks.validation.nameRequired'));
            } else {
                setNameError('');
            }
        }
        if (field === 'description' || field === 'all') {
            if (!formData.description.trim()) {
                setDescError(t('tasks.validation.descRequired'));
            } else {
                setDescError('');
            }
        }
        if (field === 'basePoints' || field === 'all') {
            if (formData.basePoints < 1) {
                setPointsError(t('tasks.validation.pointsMin'));
            } else {
                setPointsError('');
            }
        }
        if ((field === 'recurrenceMinDays' || field === 'all') && formData.scheduleType === 'recurring') {
            if (formData.recurrenceMinDays < 1) {
                setMinDaysError(t('tasks.validation.minDaysMin'));
            } else if (formData.recurrenceMinDays > formData.recurrenceMaxDays) {
                setMinDaysError(t('tasks.validation.minDaysExceedsMax'));
            } else {
                setMinDaysError('');
            }
        }
    };

    const validateAll = (): boolean => {
        let valid = true;

        if (!formData.name.trim()) {
            setNameError(t('tasks.validation.nameRequired'));
            valid = false;
        } else {
            setNameError('');
        }
        if (!formData.description.trim()) {
            setDescError(t('tasks.validation.descRequired'));
            valid = false;
        } else {
            setDescError('');
        }
        if (formData.basePoints < 1) {
            setPointsError(t('tasks.validation.pointsMin'));
            valid = false;
        } else {
            setPointsError('');
        }
        if (formData.scheduleType === 'recurring') {
            if (formData.recurrenceMinDays < 1) {
                setMinDaysError(t('tasks.validation.minDaysMin'));
                valid = false;
            } else if (formData.recurrenceMinDays > formData.recurrenceMaxDays) {
                setMinDaysError(t('tasks.validation.minDaysExceedsMax'));
                valid = false;
            } else {
                setMinDaysError('');
            }
        }

        return valid;
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (validateAll()) {
            onSubmit(e);
        }
    };

    const WEEKDAY_OPTIONS = [
        { value: 'Monday', label: t('weekdays.monday') },
        { value: 'Tuesday', label: t('weekdays.tuesday') },
        { value: 'Wednesday', label: t('weekdays.wednesday') },
        { value: 'Thursday', label: t('weekdays.thursday') },
        { value: 'Friday', label: t('weekdays.friday') },
        { value: 'Saturday', label: t('weekdays.saturday') },
        { value: 'Sunday', label: t('weekdays.sunday') },
    ];

    return (
        <form onSubmit={handleSubmit} className="form-grid task-form">
            <div className="form-group">
                <label htmlFor="taskName">{t('tasks.fields.name')}</label>
                <input
                    id="taskName"
                    type="text"
                    value={formData.name}
                    className={nameError ? 'error-input' : ''}
                    onChange={(e) => {
                        onChange({ name: e.target.value });
                        if (nameError) setNameError('');
                    }}
                    onBlur={() => validateField('name')}
                    required
                    placeholder="e.g. Wash Dishes"
                />
                {nameError && <small className="error-text">{nameError}</small>}
            </div>
            <div className="form-group">
                <label htmlFor="taskDescription">{t('tasks.fields.description')}</label>
                <input
                    id="taskDescription"
                    type="text"
                    value={formData.description}
                    className={descError ? 'error-input' : ''}
                    onChange={(e) => {
                        onChange({ description: e.target.value });
                        if (descError) setDescError('');
                    }}
                    onBlur={() => validateField('description')}
                    required
                    placeholder="e.g. Load and start the dishwasher"
                />
                {descError && <small className="error-text">{descError}</small>}
            </div>
            <div className="form-group">
                <label htmlFor="taskBasePoints">{t('tasks.fields.basePoints')}</label>
                <input
                    id="taskBasePoints"
                    type="number"
                    value={formData.basePoints}
                    className={pointsError ? 'error-input' : ''}
                    onChange={(e) => {
                        onChange({ basePoints: Number(e.target.value) });
                        if (pointsError) setPointsError('');
                    }}
                    onBlur={() => validateField('basePoints')}
                    min={1}
                    max={1000}
                    required
                />
                {pointsError && <small className="error-text">{pointsError}</small>}
            </div>
            <div className="form-group">
                <label htmlFor="taskAssignedTo">{t('tasks.fields.assignedTo')}</label>
                <select
                    id="taskAssignedTo"
                    value={formData.assignedRoleId || 0}
                    onChange={(e) => {
                        const value = Number(e.target.value);
                        onChange({ assignedRoleId: value === 0 ? 0 : value });
                    }}
                >
                    <option value={0}>🏠 {t('tasks.assignedToAll')}</option>
                    {roles.map(role => (
                        <option key={role.id} value={role.id}>
                            {role.name}
                        </option>
                    ))}
                </select>
                <small className="help-text">{t('tasks.assignedToHint')}</small>
            </div>
            <div className="form-group">
                <label htmlFor="taskScheduleType">{t('tasks.fields.scheduleType')}</label>
                <select
                    id="taskScheduleType"
                    value={formData.scheduleType}
                    onChange={(e) => {
                        const newType = e.target.value;
                        const updates: Partial<TaskFormData> = { scheduleType: newType };
                        if (newType === 'daily') {
                            updates.defaultDueTime = '17:00';
                        } else if (newType === 'weekly') {
                            updates.defaultDueTime = 'Monday';
                        } else {
                            updates.defaultDueTime = 'recurring';
                        }
                        onChange(updates);
                    }}
                    className="schedule-select"
                >
                    <option value="daily">📅 {t('tasks.scheduleTypes.daily')}</option>
                    <option value="weekly">📆 {t('tasks.scheduleTypes.weekly')}</option>
                    <option value="recurring">🔄 {t('tasks.scheduleTypes.recurring')}</option>
                </select>
                <small className="help-text-block">
                    {formData.scheduleType === 'daily' && `⏰ ${t('tasks.scheduleInfo.daily')}`}
                    {formData.scheduleType === 'weekly' && `🗓️ ${t('tasks.scheduleInfo.weekly')}`}
                    {formData.scheduleType === 'recurring' && `⏳ ${t('tasks.scheduleInfo.recurring')}`}
                </small>
            </div>

            {formData.scheduleType === 'recurring' ? (
                <div className="recurring-fields-container">
                    <h4 className="recurring-header">
                        🔄 {t('tasks.cooldownSettings')}
                    </h4>

                    <div className="recurring-grid">
                        <div className="form-group form-group-no-margin">
                            <label htmlFor="taskMinDays">{t('tasks.fields.minDays')} ⏱️</label>
                            <input
                                id="taskMinDays"
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
                                onBlur={() => validateField('recurrenceMinDays')}
                                min={1}
                                max={365}
                                required
                            />
                            {minDaysError && <small className="error-text">{minDaysError}</small>}
                            <small className="help-text">
                                {t('tasks.waitAtLeast')} <strong>{formData.recurrenceMinDays}</strong>{' '}
                                {t('tasks.days_count', { count: formData.recurrenceMinDays })}{' '}
                                {t('tasks.afterCompletion')}
                            </small>
                        </div>

                        <div className="form-group form-group-no-margin">
                            <label htmlFor="taskMaxDays">{t('tasks.fields.maxDays')} ⌛</label>
                            <input
                                id="taskMaxDays"
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
                                {t('tasks.shouldBeDoneWithin')} <strong>{formData.recurrenceMaxDays}</strong>{' '}
                                {t('tasks.days_count', { count: formData.recurrenceMaxDays })}
                            </small>
                        </div>
                    </div>
                </div>
            ) : (
                <div className="form-group">
                    <label htmlFor="taskDueTime">
                        {formData.scheduleType === 'daily' ? t('tasks.fields.dueTime') : t('tasks.fields.dueDay')}
                    </label>
                    {formData.scheduleType === 'daily' ? (
                        <input
                            id="taskDueTime"
                            type="time"
                            value={formData.defaultDueTime}
                            onChange={(e) => onChange({ defaultDueTime: e.target.value })}
                            required
                        />
                    ) : (
                        <select
                            id="taskDueTime"
                            value={formData.defaultDueTime}
                            onChange={(e) => onChange({ defaultDueTime: e.target.value })}
                            required
                        >
                            {WEEKDAY_OPTIONS.map(({ value, label }) => (
                                <option key={value} value={value}>{label}</option>
                            ))}
                        </select>
                    )}
                    <small className="help-text">
                        {formData.scheduleType === 'daily' ? t('tasks.dueTimeHint') : t('tasks.dueDayHint')}
                    </small>
                </div>
            )}

            <div className="form-actions form-actions-full">
                {onCancel && (
                    <button type="button" className="btn btn-secondary" onClick={onCancel}>
                        {t('common.cancel')}
                    </button>
                )}
                <button type="submit" className="btn btn-primary" disabled={submitting}>
                    {submitting ? t('tasks.saving') : (submitButtonText ?? t('tasks.createTask'))}
                </button>
            </div>

            {error && <div className="error-message error-message-full">{error}</div>}
        </form>
    );
};

export default TaskForm;
