import React, { useState, useEffect } from 'react';
import { getRoles, updateRole, createRole, deleteRole, getRoleUsers } from '../../api';
import type { Role } from '../../types';
import './Dashboard.css';

interface RoleUser {
    id: number;
    nickname: string;
}

interface DeleteModalProps {
    role: Role;
    users: RoleUser[];
    roles: Role[];
    onConfirm: (reassignToRoleId: number) => void;
    onCancel: () => void;
}

function DeleteRoleModal({ role, users, roles, onConfirm, onCancel }: DeleteModalProps) {
    const [selectedRoleId, setSelectedRoleId] = useState<number | null>(null);
    const availableRoles = roles.filter(r => r.id !== role.id);

    return (
        <div className="modal-overlay" onClick={onCancel}>
            <div className="modal-content glass-card" onClick={e => e.stopPropagation()} style={{ maxWidth: '500px' }}>
                <h2 style={{ color: '#ef4444', marginBottom: '1rem' }}>⚠️ Delete Role: {role.name}</h2>

                {users.length > 0 ? (
                    <>
                        <p style={{ marginBottom: '1rem' }}>
                            This role has <strong>{users.length} user(s)</strong> assigned:
                        </p>
                        <div style={{
                            background: 'rgba(255,255,255,0.05)',
                            borderRadius: '8px',
                            padding: '0.75rem',
                            marginBottom: '1rem'
                        }}>
                            {users.map(u => (
                                <span key={u.id} style={{
                                    display: 'inline-block',
                                    background: 'rgba(139, 92, 246, 0.2)',
                                    padding: '0.25rem 0.5rem',
                                    borderRadius: '12px',
                                    marginRight: '0.5rem',
                                    marginBottom: '0.25rem'
                                }}>
                                    {u.nickname}
                                </span>
                            ))}
                        </div>

                        <p style={{ marginBottom: '0.5rem' }}>
                            <strong>Select a new role</strong> for these users:
                        </p>
                        <select
                            value={selectedRoleId || ''}
                            onChange={e => setSelectedRoleId(Number(e.target.value))}
                            style={{
                                width: '100%',
                                padding: '0.75rem',
                                marginBottom: '1.5rem',
                                borderRadius: '8px',
                                background: '#1e1e2e',
                                border: '1px solid rgba(255,255,255,0.3)',
                                color: '#ffffff',
                                fontSize: '1rem'
                            }}
                        >
                            <option value="" style={{ background: '#1e1e2e', color: '#ffffff' }}>-- Select Role --</option>
                            {availableRoles.map(r => (
                                <option key={r.id} value={r.id} style={{ background: '#1e1e2e', color: '#ffffff' }}>
                                    {r.name} (×{r.multiplier_value})
                                </option>
                            ))}
                        </select>
                    </>
                ) : (
                    <p style={{ marginBottom: '1.5rem' }}>
                        No users are assigned to this role. It can be deleted safely.
                    </p>
                )}

                <div style={{ display: 'flex', gap: '1rem' }}>
                    <button
                        className="btn btn-secondary"
                        onClick={onCancel}
                        style={{ flex: 1 }}
                    >
                        Cancel
                    </button>
                    <button
                        className="btn btn-primary"
                        onClick={() => {
                            if (users.length === 0) {
                                onConfirm(0); // No reassignment needed
                            } else if (selectedRoleId) {
                                onConfirm(selectedRoleId);
                            }
                        }}
                        disabled={users.length > 0 && !selectedRoleId}
                        style={{
                            flex: 1,
                            background: '#ef4444',
                            opacity: (users.length > 0 && !selectedRoleId) ? 0.5 : 1
                        }}
                    >
                        🗑️ Delete Role
                    </button>
                </div>
            </div>
        </div>
    );
}

const RoleManagement: React.FC = () => {
    const [roles, setRoles] = useState<Role[]>([]);
    const [loading, setLoading] = useState(true);
    const [editingId, setEditingId] = useState<number | null>(null);
    const [editValue, setEditValue] = useState<string>('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    // Add role form
    const [showAddForm, setShowAddForm] = useState(false);
    const [newRoleName, setNewRoleName] = useState('');
    const [newRoleMultiplier, setNewRoleMultiplier] = useState('1.0');

    // Delete modal
    const [deleteTarget, setDeleteTarget] = useState<Role | null>(null);
    const [deleteUsers, setDeleteUsers] = useState<RoleUser[]>([]);

    useEffect(() => {
        fetchRoles();
    }, []);

    const fetchRoles = async () => {
        try {
            const response = await getRoles();
            setRoles(response.data);
        } catch (err) {
            console.error('Failed to fetch roles', err);
        } finally {
            setLoading(false);
        }
    };

    const startEditing = (role: Role) => {
        setEditingId(role.id);
        setEditValue(role.multiplier_value.toString());
        setError('');
        setSuccess('');
    };

    const cancelEditing = () => {
        setEditingId(null);
        setEditValue('');
        setError('');
    };

    const handleUpdate = async (roleId: number) => {
        const value = parseFloat(editValue);
        if (isNaN(value) || value < 0.1) {
            setError('Multiplier must be at least 0.1');
            return;
        }

        try {
            await updateRole(roleId, value);
            setSuccess('Multiplier updated successfully');
            setEditingId(null);
            fetchRoles();
            setTimeout(() => setSuccess(''), 3000);
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to update multiplier');
        }
    };

    const handleCreateRole = async () => {
        if (!newRoleName.trim()) {
            setError('Role name is required');
            return;
        }
        const value = parseFloat(newRoleMultiplier);
        if (isNaN(value) || value < 0.1) {
            setError('Multiplier must be at least 0.1');
            return;
        }

        try {
            await createRole(newRoleName.trim(), value);
            setSuccess(`Role "${newRoleName}" created successfully`);
            setNewRoleName('');
            setNewRoleMultiplier('1.0');
            setShowAddForm(false);
            fetchRoles();
            setTimeout(() => setSuccess(''), 3000);
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to create role');
        }
    };

    const initiateDelete = async (role: Role) => {
        try {
            const response = await getRoleUsers(role.id);
            setDeleteUsers(response.data.users);
            setDeleteTarget(role);
        } catch {
            setError('Failed to check role usage');
        }
    };

    const handleDeleteRole = async (reassignToRoleId: number) => {
        if (!deleteTarget) return;

        try {
            await deleteRole(deleteTarget.id, reassignToRoleId || undefined);
            setSuccess(`Role "${deleteTarget.name}" deleted successfully`);
            setDeleteTarget(null);
            setDeleteUsers([]);
            fetchRoles();
            setTimeout(() => setSuccess(''), 3000);
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to delete role');
            setDeleteTarget(null);
        }
    };

    if (loading) return <div className="loading">Loading...</div>;

    return (
        <div className="page-container fade-in">
            <header className="page-header">
                <div>
                    <h1 className="page-title">Role Management</h1>
                    <p className="page-subtitle">Configure point multipliers for each family role</p>
                </div>
                <button
                    className="btn btn-primary"
                    onClick={() => setShowAddForm(!showAddForm)}
                >
                    {showAddForm ? '✕ Cancel' : '+ Add Role'}
                </button>
            </header>

            {success && <div className="success-message mb-lg fade-in">{success}</div>}
            {error && <div className="error-message mb-lg fade-in">{error}</div>}

            {/* Add Role Form */}
            {showAddForm && (
                <div className="glass-panel mb-lg fade-in" style={{ padding: '1.5rem' }}>
                    <h3 style={{ marginBottom: '1rem' }}>➕ Create New Role</h3>
                    <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                        <div style={{ flex: '2', minWidth: '200px' }}>
                            <label className="form-label">Role Name</label>
                            <input
                                type="text"
                                className="form-input"
                                placeholder="e.g., Grandparent"
                                value={newRoleName}
                                onChange={e => setNewRoleName(e.target.value)}
                            />
                        </div>
                        <div style={{ flex: '1', minWidth: '120px' }}>
                            <label className="form-label">Multiplier</label>
                            <input
                                type="number"
                                step="0.1"
                                min="0.1"
                                className="form-input"
                                value={newRoleMultiplier}
                                onChange={e => setNewRoleMultiplier(e.target.value)}
                            />
                        </div>
                        <div style={{ display: 'flex', alignItems: 'flex-end' }}>
                            <button className="btn btn-primary" onClick={handleCreateRole}>
                                Create Role
                            </button>
                        </div>
                    </div>
                </div>
            )}

            <div className="roles-grid">
                {roles.map(role => (
                    <div key={role.id} className="role-card glass-panel">
                        <div className="role-header">
                            <div className="role-icon">
                                {role.name === 'Admin' ? '👑' :
                                    role.name === 'Teenager' ? '🎧' :
                                        role.name === 'Child' ? '🧸' :
                                            role.name === 'Contributor' ? '👤' : '🏷️'}
                            </div>
                            <h3>{role.name}</h3>
                            <button
                                className="btn btn-ghost btn-sm"
                                onClick={() => initiateDelete(role)}
                                title="Delete Role"
                                style={{ marginLeft: 'auto', color: '#ef4444' }}
                            >
                                🗑️
                            </button>
                        </div>

                        <div className="role-content">
                            <div className="multiplier-section">
                                <span className="label">Point Multiplier</span>
                                {editingId === role.id ? (
                                    <div className="edit-controls">
                                        <input
                                            type="number"
                                            step="0.1"
                                            min="0.1"
                                            value={editValue}
                                            onChange={(e) => setEditValue(e.target.value)}
                                            className="multiplier-input"
                                        />
                                        <div className="btn-group">
                                            <button
                                                className="btn btn-sm btn-primary"
                                                onClick={() => handleUpdate(role.id)}
                                            >
                                                Save
                                            </button>
                                            <button
                                                className="btn btn-sm btn-secondary"
                                                onClick={cancelEditing}
                                            >
                                                Cancel
                                            </button>
                                        </div>
                                    </div>
                                ) : (
                                    <div className="display-controls">
                                        <span className="multiplier-value">x{role.multiplier_value}</span>
                                        <button
                                            className="btn-icon"
                                            onClick={() => startEditing(role)}
                                            title="Edit Multiplier"
                                        >
                                            ✏️
                                        </button>
                                    </div>
                                )}
                            </div>
                            <p className="role-description">
                                {role.name === 'Admin' ? 'System administrators with full access.' :
                                    role.name === 'Teenager' ? 'Older children with higher responsibility.' :
                                        role.name === 'Child' ? 'Younger children with basic chores.' :
                                            role.name === 'Contributor' ? 'Standard contributors.' :
                                                'Custom role with configurable permissions.'}
                            </p>
                        </div>
                    </div>
                ))}
            </div>

            {/* Delete Confirmation Modal */}
            {deleteTarget && (
                <DeleteRoleModal
                    role={deleteTarget}
                    users={deleteUsers}
                    roles={roles}
                    onConfirm={handleDeleteRole}
                    onCancel={() => {
                        setDeleteTarget(null);
                        setDeleteUsers([]);
                    }}
                />
            )}
        </div>
    );
};

export default RoleManagement;
