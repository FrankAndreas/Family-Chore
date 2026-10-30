import React, { useState, useEffect, useCallback } from 'react';
import { ADMIN_ROLE_NAME } from '../../constants';
import { getUsersAdmin, getRemovedUsers, getRoles, penalizeUser, updateUser, deleteUser } from '../../api';
import type { User, Role } from '../../types';
import { SkeletonLoader } from '../../components/SkeletonLoader';
import { useTranslation } from 'react-i18next';
import { useToast } from '../../context/ToastContext';
import '../../styles/SharedDashboard.css';
import './Dashboard.css';

const UserManagement: React.FC = () => {
    const { t } = useTranslation();
    const { showToast } = useToast();
    const [users, setUsers] = useState<User[]>([]);
    // Removed in the family hub: hidden with points and history until deleted here
    const [removed, setRemoved] = useState<User[]>([]);
    const [roles, setRoles] = useState<Role[]>([]);
    const [loading, setLoading] = useState(true);

    // Form state

    // Penalty state
    const [selectedUserForPenalty, setSelectedUserForPenalty] = useState<User | null>(null);
    const [penaltyPoints, setPenaltyPoints] = useState<number | ''>('');
    const [penaltyReason, setPenaltyReason] = useState<string>('');
    const [penaltyError, setPenaltyError] = useState<string>('');


    // Edit/Delete state
    const [selectedUserForEdit, setSelectedUserForEdit] = useState<User | null>(null);
    const [editRoleId, setEditRoleId] = useState<number>(0);
    const [editError, setEditError] = useState('');

    const [selectedUserForDelete, setSelectedUserForDelete] = useState<User | null>(null);
    const [deleteError, setDeleteError] = useState('');

    const loadData = () => Promise.all([getUsersAdmin(), getRoles(), getRemovedUsers()]);

    const applyData = useCallback(([usersRes, rolesRes, removedRes]: Awaited<ReturnType<typeof loadData>>) => {
        setUsers(usersRes.data);
        setRoles(rolesRes.data);
        setRemoved(removedRes.data);
    }, []);

    const fetchData = async () => {
        try {
            applyData(await loadData());
        } catch (err) {
            console.error('Failed to fetch data', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        let ignore = false;
        loadData()
            .then((data) => {
                if (!ignore) applyData(data);
            })
            .catch((err) => console.error('Failed to fetch data', err))
            .finally(() => {
                if (!ignore) setLoading(false);
            });
        return () => {
            ignore = true;
        };
    }, [applyData]);

    const handlePenalize = async (e: React.FormEvent) => {
        e.preventDefault();
        setPenaltyError('');

        if (!selectedUserForPenalty) return;

        if (!penaltyPoints || penaltyPoints <= 0) {
            setPenaltyError('Points must be greater than 0');
            return;
        }

        if (!penaltyReason.trim()) {
            setPenaltyError('Reason is required');
            return;
        }

        try {
            await penalizeUser(selectedUserForPenalty.id, Number(penaltyPoints), penaltyReason);
            setSelectedUserForPenalty(null);
            setPenaltyPoints(0);
            setPenaltyReason('');
            fetchData(); // Refresh list to get updated points
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } catch (err: any) {
            setPenaltyError(err.response?.data?.detail || 'Failed to penalize user');
        }
    };

    // The Admin role belongs to the family hub's parents: a child gets one of the others
    const gameRoles = roles.filter(role => role.name !== ADMIN_ROLE_NAME);

    const handleEditClick = (user: User) => {
        setSelectedUserForEdit(user);
        setEditRoleId(user.role?.id || gameRoles[0]?.id || 0);
        setEditError('');
    };

    const handleUpdateUser = async (e: React.FormEvent) => {
        e.preventDefault();
        setEditError('');

        if (!selectedUserForEdit) return;

        try {
            // A child's game role; the name, the PIN and who is Admin (a parent) come from the family hub
            await updateUser(selectedUserForEdit.id, { role_id: editRoleId });

            showToast(`${selectedUserForEdit.nickname} updated successfully`, 'success');
            setSelectedUserForEdit(null);
            fetchData();
        } catch (err: unknown) {
            const errorObj = err as { response?: { data?: { detail?: string } } };
            setEditError(errorObj.response?.data?.detail || 'Failed to update user');
        }
    };

    const handleDeleteUser = async () => {
        setDeleteError('');
        if (!selectedUserForDelete) return;

        try {
            await deleteUser(selectedUserForDelete.id);
            showToast(`${selectedUserForDelete.nickname} deleted`, 'success');
            setSelectedUserForDelete(null);
            fetchData();
        } catch (err: unknown) {
            const errorObj = err as { response?: { data?: { detail?: string } } };
            setDeleteError(errorObj.response?.data?.detail || 'Failed to delete user');
        }
    };

    if (loading) {
        return (
            <div className="page-container fade-in">
                <header className="page-header">
                    <SkeletonLoader type="title" className="mb-2" />
                    <SkeletonLoader type="text" className="w-64" />
                </header>
                <div className="users-grid">
                    <SkeletonLoader type="card" count={4} />
                </div>
            </div>
        );
    }

    return (
        <div className="page-container fade-in">
            <header className="page-header">
                <div className="header-content">
                    <div>
                        <h1 className="page-title">User Management</h1>
                        <p className="page-subtitle">{t('users.subtitle', 'Manage family members and their roles')}</p>
                    </div>
                </div>
            </header>

            <p className="text-secondary mb-3">{t('users.fromHub')}</p>

            <div className="users-grid">
                {users.map(user => (
                    <div key={user.id} className="user-card glass-panel">
                        <div className="user-card-header">
                            <div className="user-avatar-large">{user.nickname[0]}</div>
                            <div className="user-details">
                                <h3>{user.nickname}</h3>
                                <span className="role-badge">{user.role?.name || 'Unknown Role'}</span>
                            </div>
                        </div>
                        <div className="user-stats">
                            <div className="stat-item">
                                <span className="label">Current Points</span>
                                <span className="value">{user.current_points}</span>
                            </div>
                            <div className="stat-item">
                                <span className="label">Lifetime Points</span>
                                <span className="value">{user.lifetime_points}</span>
                            </div>
                        </div>
                        <div className="user-card-actions" style={{ marginTop: '1rem', borderTop: '1px solid var(--border-color)', paddingTop: '1rem', display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
                            {user.role?.name !== ADMIN_ROLE_NAME && (
                                <button
                                    className="btn btn-secondary btn-sm"
                                    onClick={() => handleEditClick(user)}
                                >
                                    Edit
                                </button>
                            )}
                            <button
                                className="btn btn-secondary btn-sm"
                                onClick={() => setSelectedUserForPenalty(user)}
                            >
                                Deduct Points
                            </button>
                        </div>
                    </div>
                ))}
            </div>

            {removed.length > 0 && (
                <section className="section glass-panel mt-3">
                    <h2>{t('users.removedTitle')}</h2>
                    <p className="text-secondary mb-3">{t('users.removedHint')}</p>
                    <ul>
                        {removed.map(user => (
                            <li key={user.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.5rem 0' }}>
                                <span>{user.nickname} ({user.current_points} pts)</span>
                                <button className="btn btn-secondary btn-sm" onClick={() => setSelectedUserForDelete(user)}>
                                    {t('users.deleteData', { name: user.nickname })}
                                </button>
                            </li>
                        ))}
                    </ul>
                </section>
            )}

            {/* Penalty Modal */}
            {selectedUserForPenalty && (
                <div className="modal-overlay fade-in" onClick={() => setSelectedUserForPenalty(null)}>
                    <div className="modal-content glass-panel" onClick={e => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2>Deduct Points</h2>
                            <button className="close-btn" onClick={() => setSelectedUserForPenalty(null)} aria-label="Close modal">×</button>
                        </div>

                        <div className="modal-body">
                            <p style={{ marginBottom: '1.5rem', color: 'var(--text-secondary)' }}>
                                Deducting points from <strong>{selectedUserForPenalty.nickname}</strong>.
                                Current balance: <strong>{selectedUserForPenalty.current_points}</strong> pts.
                            </p>

                            <form onSubmit={handlePenalize} className="form-grid">
                                <div className="form-group">
                                    <label htmlFor="penaltyPoints">Points to Deduct</label>
                                    <input
                                        id="penaltyPoints"
                                        type="number"
                                        value={penaltyPoints}
                                        onChange={(e) => setPenaltyPoints(e.target.value ? Number(e.target.value) : '')}
                                        required
                                        min="1"
                                        placeholder="e.g. 50"
                                    />
                                </div>
                                <div className="form-group" style={{ gridColumn: '1 / -1' }}>
                                    <label htmlFor="penaltyReason">Reason</label>
                                    <input
                                        id="penaltyReason"
                                        type="text"
                                        value={penaltyReason}
                                        onChange={(e) => setPenaltyReason(e.target.value)}
                                        required
                                        placeholder="e.g. Missed taking out the trash"
                                    />
                                </div>

                                {penaltyError && <div className="error-message" style={{ gridColumn: '1 / -1' }}>{penaltyError}</div>}

                                <div className="form-actions" style={{ gridColumn: '1 / -1', marginTop: '1rem' }}>
                                    <button type="button" className="btn btn-secondary" onClick={() => setSelectedUserForPenalty(null)}>
                                        Cancel
                                    </button>
                                    <button type="submit" className="btn btn-primary" style={{ background: 'var(--warning-gradient)', border: 'none', color: '#fff' }}>
                                        Deduct {penaltyPoints || 0} Points
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            )}
            {/* Edit User Modal */}
            {selectedUserForEdit && (
                <div className="modal-overlay fade-in" onClick={() => setSelectedUserForEdit(null)}>
                    <div className="modal-content glass-panel" onClick={e => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2>Edit User: {selectedUserForEdit.nickname}</h2>
                            <button className="close-btn" onClick={() => setSelectedUserForEdit(null)} aria-label="Close modal">×</button>
                        </div>

                        <div className="modal-body">
                            <form onSubmit={handleUpdateUser} className="form-grid">
                                <div className="form-group">
                                    <label htmlFor="editUserRole">Role</label>
                                    <select
                                        id="editUserRole"
                                        value={editRoleId}
                                        onChange={(e) => setEditRoleId(Number(e.target.value))}
                                    >
                                        {gameRoles.map(role => (
                                            <option key={role.id} value={role.id}>
                                                {role.name} (x{role.multiplier_value})
                                            </option>
                                        ))}
                                    </select>
                                </div>
                                {editError && <div className="error-message" style={{ gridColumn: '1 / -1' }}>{editError}</div>}

                                <div className="form-actions" style={{ gridColumn: '1 / -1', marginTop: '1rem' }}>
                                    <button type="button" className="btn btn-secondary" onClick={() => setSelectedUserForEdit(null)}>
                                        Cancel
                                    </button>
                                    <button type="submit" className="btn btn-primary">
                                        Save Changes
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            )}

            {/* Delete Confirmation Modal */}
            {selectedUserForDelete && (
                <div className="modal-overlay fade-in" onClick={() => setSelectedUserForDelete(null)}>
                    <div className="modal-content glass-panel" onClick={e => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2 style={{ color: '#1a1a2e' }}>Delete User</h2>
                            <button className="close-btn" onClick={() => setSelectedUserForDelete(null)} aria-label="Close modal">×</button>
                        </div>
                        <div className="modal-body">
                            <div className="alert-box" style={{
                                backgroundColor: 'rgba(245, 101, 101, 0.1)',
                                padding: '1.25rem',
                                borderRadius: 'var(--radius-md)',
                                marginBottom: '1.5rem',
                                border: '1px solid rgba(245, 101, 101, 0.3)'
                            }}>
                                <strong style={{ color: '#c53030', display: 'block', marginBottom: '0.5rem', fontSize: '1.1rem' }}>Warning: Permanent Action</strong>
                                <p style={{ color: '#333', lineHeight: '1.5' }}>
                                    Are you sure you want to delete <strong style={{ color: '#1a1a2e' }}>{selectedUserForDelete.nickname}</strong>?
                                    This will permanently remove their profile, assigned tasks, and entire transaction history.
                                </p>
                            </div>

                            {deleteError && <div className="error-message">{deleteError}</div>}

                            <div className="form-actions space-between" style={{ marginTop: '2rem' }}>
                                <button className="btn btn-secondary" onClick={() => setSelectedUserForDelete(null)}>
                                    Cancel
                                </button>
                                <button className="btn btn-primary" style={{ backgroundColor: '#e53e3e', border: 'none', color: '#fff' }} onClick={handleDeleteUser}>
                                    Yes, Delete User
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default UserManagement;
