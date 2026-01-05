import React, { useState, useEffect } from 'react';
import { getUsers, createUser, getRoles } from '../../api';
import type { User, Role } from '../../types';
import './Dashboard.css';

const UserManagement: React.FC = () => {
    const [users, setUsers] = useState<User[]>([]);
    const [roles, setRoles] = useState<Role[]>([]);
    const [loading, setLoading] = useState(true);
    const [showAddForm, setShowAddForm] = useState(false);

    // Form state
    const [nickname, setNickname] = useState('');
    const [pin, setPin] = useState('');
    const [roleId, setRoleId] = useState<number>(0);
    const [error, setError] = useState('');

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

    if (loading) return <div className="loading">Loading...</div>;

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
                    </div>
                ))}
            </div>
        </div>
    );
};

export default UserManagement;
