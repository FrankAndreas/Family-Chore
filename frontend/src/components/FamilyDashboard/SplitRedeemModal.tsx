import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import Modal from '../Modal';
import type { User, Reward } from '../../types';

export interface SplitRedeemModalProps {
    reward: Reward;
    users: User[];
    onConfirm: (contributions: { user_id: number; points: number }[]) => void;
    onClose: () => void;
    redeeming: boolean;
}

export default function SplitRedeemModal({ reward, users, onConfirm, onClose, redeeming }: SplitRedeemModalProps) {
    const { t } = useTranslation();
    const [contributions, setContributions] = useState<{ [userId: number]: number }>(
        () => Object.fromEntries(users.map(u => [u.id, 0]))
    );

    const totalContribution = Object.values(contributions).reduce((sum, pts) => sum + pts, 0);
    const remaining = reward.cost_points - totalContribution;
    const isExact = remaining === 0;

    const updateContribution = (userId: number, points: number) => {
        const user = users.find(u => u.id === userId);
        if (!user) return;
        const clamped = Math.max(0, Math.min(points, user.current_points));
        setContributions(prev => ({ ...prev, [userId]: clamped }));
    };

    const handleSplitEvenly = () => {
        const eligibleUsers = users.filter(u => u.current_points > 0);
        if (eligibleUsers.length === 0) return;

        const perUser = Math.floor(reward.cost_points / eligibleUsers.length);
        let leftover = reward.cost_points % eligibleUsers.length;

        const newContribs: { [userId: number]: number } = {};
        users.forEach(u => {
            if (u.current_points === 0) {
                newContribs[u.id] = 0;
            } else {
                let contrib = Math.min(perUser, u.current_points);
                if (leftover > 0 && contrib < u.current_points) {
                    contrib++;
                    leftover--;
                }
                newContribs[u.id] = contrib;
            }
        });
        setContributions(newContribs);
    };

    const handleMaxFromEach = () => {
        let remainingPts = reward.cost_points;
        const newContribs: { [userId: number]: number } = {};
        const sorted = [...users].sort((a, b) => b.current_points - a.current_points);

        sorted.forEach(user => {
            const take = Math.min(user.current_points, remainingPts);
            newContribs[user.id] = take;
            remainingPts -= take;
        });

        setContributions(newContribs);
    };

    const handleConfirm = () => {
        const contribs = Object.entries(contributions).map(([userId, points]) => ({
            user_id: parseInt(userId),
            points
        }));
        onConfirm(contribs);
    };

    return (
        <Modal isOpen={true} onClose={onClose} title={t('dashboard.splitRedemption')} size="large">
            <p className="reward-title"><strong>{reward.name}</strong> — {reward.cost_points} {t('common.pts')}</p>

            <div className="preset-buttons">
                <button className="btn btn-secondary btn-small" onClick={handleSplitEvenly}>
                    {t('dashboard.splitEvenly')}
                </button>
                <button className="btn btn-secondary btn-small" onClick={handleMaxFromEach}>
                    {t('dashboard.maxFromEach')}
                </button>
            </div>

            <div className="contribution-list">
                {users.map(user => (
                    <div key={user.id} className="contribution-row">
                        <span className="contrib-user">
                            {user.nickname}
                            <span className="contrib-available">({user.current_points} {t('common.pts')})</span>
                        </span>
                        <input
                            type="number"
                            min={0}
                            max={user.current_points}
                            value={contributions[user.id] || 0}
                            onChange={e => updateContribution(user.id, parseInt(e.target.value) || 0)}
                            onKeyDown={(e) => {
                                if (e.key === '-' || e.key === 'e' || e.key === '+') {
                                    e.preventDefault();
                                }
                            }}
                            className="contrib-input"
                        />
                    </div>
                ))}
            </div>

            <div className={`total-display ${isExact ? 'exact' : remaining < 0 ? 'over' : 'under'}`}>
                {t('dashboard.total', 'Total')}: {totalContribution}/{reward.cost_points} {t('common.pts', 'pts')}
                {isExact ? ' ✅' : remaining > 0 ? ` (${t('dashboard.needMore', { count: remaining, defaultValue: `need ${remaining} more` })})` : ` (${t('dashboard.over', { count: -remaining, defaultValue: `${-remaining} over!` })})`}
            </div>

            <div className="modal-actions">
                <button className="btn btn-secondary" onClick={onClose} disabled={redeeming}>
                    {t('dashboard.cancel', 'Cancel')}
                </button>
                <button
                    className="btn btn-success"
                    onClick={handleConfirm}
                    disabled={!isExact || redeeming}
                >
                    {redeeming ? t('dashboard.redeeming', 'Redeeming...') : t('dashboard.redeemAction', '🎉 Redeem!')}
                </button>
            </div>
        </Modal>
    );
}
