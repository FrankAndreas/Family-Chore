import React, { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import { getUsers, createUser, getRoles, penalizeUser, updateUser, resetUserPassword, deleteUser } from '../../api';
import type { User, Role } from '../../types';
import LoadingSpinner from '../../components/LoadingSpinner';
import './Dashboard.css';

const UserManagement: React.FC = () => {
    const { currentUser } = useOutletContext<{ currentUser: User }>();
    const [users, setUsers] = useState<User[]>([]);
    const [roles, setRoles] = useState<Role[]>([]);
    const [loading, setLoading] = useState(true);
    const [showAddForm, setShowAddForm] = useState(false);

    // Form state
    const [nickname, setNickname] = useState('');
    const [pin, setPin] = useState('');
    const [roleId, setRoleId] = useState<number>(0);
    const [error, setError] = useState('');

    // Penalty state
    const [selectedUserForPenalty, setSelectedUserForPenalty] = useState<User | null>(null);
    const [penaltyPoints, setPenaltyPoints] = useState<number | ''>('');
    const [penaltyReason, setPenaltyReason] = useState<string>('');
    const [penaltyError, setPenaltyError] = useState<string>('');

    // Edit/Delete state
    const [selectedUserForEdit, setSelectedUserForEdit] = useState<User | null>(null);
    const [editNickname, setEditNickname] = useState('');
    const [editRoleId, setEditRoleId] = useState<number>(0);
    const [editNewPin, setEditNewPin] = useState('');
    const [editError, setEditError] = useState('');

    const [selectedUserForDelete, setSelectedUserForDelete] = useState<User | null>(null);
    const [deleteError, setDeleteError] = useState('');

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const [usersRes, rolesRes] = await Promise.all([getUsers(), getRoles()]);
            setUsers(usersRes.data);
            setRoles(rolesRes.data);
            if (rolesRes.data.length > 0) {
                setRoleId(rolesRes.data[0].id);
            }
        } catch (err) {
            console.error('Failed to fetch data', err);
        } finally {
            setLoading(false);
        }
    };

    const handleCreateUser = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        if (pin.length !== 4 || !/^\d+$/.test(pin)) {
            setError('PIN must be exactly 4 digits');
            return;
        }

        try {
            await createUser(nickname, pin, roleId);
            setShowAddForm(false);
            setNickname('');
            setPin('');
            fetchData(); // Refresh list
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to create user');
        }
    };

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

    const handleEditClick = (user: User) => {
        setSelectedUserForEdit(user);
        setEditNickname(user.nickname);
        setEditRoleId(user.role?.id || roles[0]?.id || 0);
        setEditNewPin('');
        setEditError('');
    };

    const handleUpdateUser = async (e: React.FormEvent) => {
        e.preventDefault();
        setEditError('');

        if (!selectedUserForEdit) return;

        try {
            // Update profile
            await updateUser(selectedUserForEdit.id, {
                nickname: editNickname,
                role_id: editRoleId
            });

            // Update PIN if provided
            if (editNewPin) {
                if (editNewPin.length !== 4 || !/^\d+$/.test(editNewPin)) {
                    setEditError('New PIN must be exactly 4 digits');
                    return;
                }
                await resetUserPassword(selectedUserForEdit.id, editNewPin);
            }

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
            setSelectedUserForDelete(null);
            fetchData();
        } catch (err: unknown) {
            const errorObj = err as { response?: { data?: { detail?: string } } };
            setDeleteError(errorObj.response?.data?.detail || 'Failed to delete user');
        }
    };

    if (loading) return <LoadingSpinner fullPage />;

    return (
        <div className="page-container fade-in">
            <header className="page-header">
                <div className="header-content">
                    <div>
                        <h1 className="page-title">User Management</h1>
                        <p className="page-subtitle">Manage family members and their roles</p>
                    </div>
                    <button
                        className="btn btn-primary"
                        onClick={() => setShowAddForm(!showAddForm)}
                    >
                        {showAddForm ? 'Cancel' : 'Add New User'}
                    </button>
                </div>
            </header>

            {showAddForm && (
                <div className="section glass-panel mb-xl fade-in">
                    <h2>Add New User</h2>
                    <form onSubmit={handleCreateUser} className="form-grid">
                        <div className="form-group">
                            <label>Nickname</label>
                            <input
                                type="text"
                                value={nickname}
                                onChange={(e) => setNickname(e.target.value)}
                                required
                                placeholder="e.g. Alice"
                            />
                        </div>
                        <div className="form-group">
                            <label>4-Digit PIN</label>
                            <input
                                type="password"
                                value={pin}
                                onChange={(e) => setPin(e.target.value)}
                                maxLength={4}
                                required
                                placeholder="****"
                            />
                        </div>
                        <div className="form-group">
                            <label>Role</label>
                            <select
                                value={roleId}
                                onChange={(e) => setRoleId(Number(e.target.value))}
                            >
                                {roles.map(role => (
                                    <option key={role.id} value={role.id}>
                                        {role.name} (x{role.multiplier_value})
                                    </option>
                                ))}
                            </select>
                        </div>
                        <div className="form-actions">
                            <button type="submit" className="btn btn-primary">Create User</button>
                        </div>
                        {error && <div className="error-message">{error}</div>}
                    </form>
                </div>
            )}

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
                            <button
                                className="btn btn-secondary btn-sm"
                                onClick={() => handleEditClick(user)}
                            >
                                Edit
                            </button>
                            <button
                                className="btn btn-secondary btn-sm"
                                onClick={() => setSelectedUserForDelete(user)}
                                disabled={user.id === currentUser.id}
                                title={user.id === currentUser.id ? "Cannot delete yourself" : ""}
                            >
                                Delete
                            </button>
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

            {/* Penalty Modal */}
            {selectedUserForPenalty && (
                <div className="modal-overlay fade-in" onClick={() => setSelectedUserForPenalty(null)}>
                    <div className="modal-content glass-panel" onClick={e => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2>Deduct Points</h2>
                            <button className="close-btn" onClick={() => setSelectedUserForPenalty(null)}>×</button>
                        </div>

                        <div className="modal-body">
                            <p style={{ marginBottom: '1.5rem', color: 'var(--text-secondary)' }}>
                                Deducting points from <strong>{selectedUserForPenalty.nickname}</strong>.
                                Current balance: <strong>{selectedUserForPenalty.current_points}</strong> pts.
                            </p>

                            <form onSubmit={handlePenalize} className="form-grid">
                                <div className="form-group">
                                    <label>Points to Deduct</label>
                                    <input
                                        type="number"
                                        value={penaltyPoints}
                                        onChange={(e) => setPenaltyPoints(e.target.value ? Number(e.target.value) : '')}
                                        required
                                        min="1"
                                        placeholder="e.g. 50"
                                    />
                                </div>
                                <div className="form-group" style={{ gridColumn: '1 / -1' }}>
                                    <label>Reason</label>
                                    <input
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
                            <button className="close-btn" onClick={() => setSelectedUserForEdit(null)}>×</button>
                        </div>

                        <div className="modal-body">
                            <form onSubmit={handleUpdateUser} className="form-grid">
                                <div className="form-group">
                                    <label>Nickname</label>
                                    <input
                                        type="text"
                                        value={editNickname}
                                        onChange={(e) => setEditNickname(e.target.value)}
                                        required
                                    />
                                </div>
                                <div className="form-group">
                                    <label>Role</label>
                                    <select
                                        value={editRoleId}
                                        onChange={(e) => setEditRoleId(Number(e.target.value))}
                                    >
                                        {roles.map(role => (
                                            <option key={role.id} value={role.id}>
                                                {role.name} (x{role.multiplier_value})
                                            </option>
                                        ))}
                                    </select>
                                </div>
                                <div className="form-group" style={{ gridColumn: '1 / -1' }}>
                                    <label>Reset PIN (Leave blank to keep current)</label>
                                    <input
                                        type="password"
                                        value={editNewPin}
                                        onChange={(e) => setEditNewPin(e.target.value)}
                                        maxLength={4}
                                        placeholder="****"
                                    />
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
                            <button className="close-btn" onClick={() => setSelectedUserForDelete(null)}>×</button>
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
