import type React from 'react';
import { useTranslation } from 'react-i18next';

export interface RewardFormData {
    name: string;
    description: string;
    cost_points: number;
    tier_level: number;
}

interface RewardFormProps {
    formData: RewardFormData;
    onChange: (data: RewardFormData) => void;
    onSubmit: (e: React.FormEvent) => void;
    onCancel: () => void;
    submitting: boolean;
    submitButtonText?: string;
}

export default function RewardForm({ formData, onChange, onSubmit, onCancel, submitting, submitButtonText }: RewardFormProps) {
    const { t } = useTranslation();

    return (
        <form onSubmit={onSubmit} className="create-reward-form">
            <div className="form-grid">
                <div className="form-group">
                    <label>{t('rewards.create_form.name_label')}</label>
                    <input
                        type="text"
                        required
                        value={formData.name}
                        onChange={(e) => onChange({ ...formData, name: e.target.value })}
                        placeholder={t('rewards.create_form.name_placeholder')}
                    />
                </div>

                <div className="form-group">
                    <label>{t('rewards.create_form.cost_label')}</label>
                    <input
                        type="number"
                        required
                        min="1"
                        value={formData.cost_points}
                        onChange={(e) => onChange({ ...formData, cost_points: parseInt(e.target.value) })}
                        placeholder="50"
                    />
                </div>

                <div className="form-group">
                    <label>{t('rewards.create_form.tier_label')}</label>
                    <select
                        value={formData.tier_level}
                        onChange={(e) => onChange({ ...formData, tier_level: parseInt(e.target.value) })}
                    >
                        <option value={1}>{t('rewards.create_form.tiers.bronze', '🥉 Bronze (Small rewards)')}</option>
                        <option value={2}>{t('rewards.create_form.tiers.silver', '🥈 Silver (Medium rewards)')}</option>
                        <option value={3}>{t('rewards.create_form.tiers.gold', '🥇 Gold (Big rewards)')}</option>
                    </select>
                </div>

                <div className="form-group full-width">
                    <label>{t('rewards.create_form.description_label')}</label>
                    <textarea
                        value={formData.description}
                        onChange={(e) => onChange({ ...formData, description: e.target.value })}
                        placeholder={t('rewards.create_form.description_placeholder')}
                        rows={3}
                    />
                </div>
            </div>

            <div className="form-actions">
                <button type="button" className="btn btn-secondary" onClick={onCancel} disabled={submitting}>
                    {t('rewards.cancel_button')}
                </button>
                <button type="submit" className="btn btn-primary" disabled={submitting}>
                    {submitting
                        ? t('rewards.create_form.submitting')
                        : (submitButtonText || t('rewards.create_form.submit_button'))
                    }
                </button>
            </div>
        </form>
    );
}
