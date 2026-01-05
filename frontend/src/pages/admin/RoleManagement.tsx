import React, { useState, useEffect } from 'react';
import { getRoles, updateRoleMultiplier } from '../../api';
import type { Role } from '../../types';
import './Dashboard.css';

const RoleManagement: React.FC = () => {
    const [roles, setRoles] = useState<Role[]>([]);
    const [loading, setLoading] = useState(true);
    const [editingId, setEditingId] = useState<number | null>(null);
    const [editValue, setEditValue] = useState<string>('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

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
            await updateRoleMultiplier(roleId, value);
            setSuccess('Multiplier updated successfully');
            setEditingId(null);
            fetchRoles(); // Refresh list

            // Clear success message after 3 seconds
            setTimeout(() => setSuccess(''), 3000);
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to update multiplier');
        }
    };

    if (loading) return <div className="loading">Loading...</div>;

    return (
        <div className="page-container fade-in">
            <header className="page-header">
                <h1 className="page-title">Role Management</h1>
                <p className="page-subtitle">Configure point multipliers for each family role</p>
            </header>

            {success && <div className="success-message mb-lg fade-in">{success}</div>}
            {error && <div className="error-message mb-lg fade-in">{error}</div>}

            <div className="roles-grid">
                {roles.map(role => (
                    <div key={role.id} className="role-card glass-panel">
                        <div className="role-header">
                            <div className="role-icon">
                                {role.name === 'Admin' ? '👑' :
                                    role.name === 'Teenager' ? '🎧' :
                                        role.name === 'Child' ? '🧸' : '👤'}
                            </div>
                            <h3>{role.name}</h3>
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
                                            'Standard contributors.'}
                            </p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default RoleManagement;
