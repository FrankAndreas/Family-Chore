import React, { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from 'react';
import { getUserNotifications, markNotificationRead, markAllNotificationsRead } from '../api';
import type { Notification, User } from '../types';
import { useToast } from './ToastContext';

interface NotificationContextType {
    notifications: Notification[];
    unreadCount: number;
    markAsRead: (id: number) => Promise<void>;
    markAllAsRead: () => Promise<void>;
    refreshNotifications: () => Promise<void>;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

interface NotificationProviderProps {
    children: ReactNode;
    currentUser: User | null;
}

export const NotificationProvider: React.FC<NotificationProviderProps> = ({ children, currentUser }) => {
    const [notifications, setNotifications] = useState<Notification[]>([]);
    const { showToast } = useToast();

    const refreshNotifications = useCallback(async () => {
        if (!currentUser) return;
        try {
            const res = await getUserNotifications(currentUser.id, false);
            setNotifications(res.data);
        } catch (error) {
            console.error("Failed to fetch notifications", error);
        }
    }, [currentUser]);

    // Initial load
    useEffect(() => {
        refreshNotifications();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    // SSE Connection
    useEffect(() => {
        if (!currentUser) return;

        const eventSource = new EventSource(`${API_BASE}/events`);

        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);

            // Check if the event is strictly a notification refresh signal 
            // OR if it's a specific event that concerns the user (like task_completed for them)
            // The backend broadcasts "notification" event specifically for this.

            if (data.type === 'notification' && data.data?.user_id === currentUser.id) {
                refreshNotifications();
                // Optional: Play sound or show toast if not already handled by other listeners
            } else if (data.type === 'task_assigned' && data.data?.user_id === currentUser.id) {
                showToast(`New task assigned: ${data.data.task_name}`, 'info');
                refreshNotifications();
            }
        };

        return () => {
            eventSource.close();
        };
    }, [currentUser, refreshNotifications, showToast]);

    const markAsRead = async (id: number) => {
        if (!currentUser) return;
        try {
            await markNotificationRead(id, currentUser.id);
            setNotifications(prev => prev.map(n => n.id === id ? { ...n, read: 1 } : n));
        } catch (error) {
            console.error("Failed to mark as read", error);
        }
    };

    const markAllAsRead = async () => {
        if (!currentUser) return;
        try {
            await markAllNotificationsRead(currentUser.id);
            setNotifications(prev => prev.map(n => ({ ...n, read: 1 })));
        } catch (error) {
            console.error("Failed to mark all as read", error);
        }
    };

    const unreadCount = notifications.filter(n => n.read === 0).length;

    return (
        <NotificationContext.Provider value={{ notifications, unreadCount, markAsRead, markAllAsRead, refreshNotifications }}>
            {children}
        </NotificationContext.Provider>
    );
};

// eslint-disable-next-line react-refresh/only-export-components
export const useNotifications = () => {
    const context = useContext(NotificationContext);
    if (!context) {
        throw new Error('useNotifications must be used within a NotificationProvider');
    }
    return context;
};
