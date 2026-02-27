import React, { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from 'react';
import {
    getUserNotifications, markNotificationRead, markAllNotificationsRead,
    getVapidPublicKey, subscribePush, unsubscribePush
} from '../api';
import type { Notification, User } from '../types';
import { useToast } from './ToastContext';

// Helper to convert VAPID key
function urlBase64ToUint8Array(base64String: string) {
    const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
    const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

interface NotificationContextType {
    notifications: Notification[];
    unreadCount: number;
    markAsRead: (id: number) => Promise<void>;
    markAllAsRead: () => Promise<void>;
    refreshNotifications: () => Promise<void>;
    isPushSupported: boolean;
    pushSubscribed: boolean;
    subscribeToPush: () => Promise<boolean>;
    unsubscribeFromPush: () => Promise<boolean>;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

interface NotificationProviderProps {
    children: ReactNode;
    currentUser: User | null;
}

export const NotificationProvider: React.FC<NotificationProviderProps> = ({ children, currentUser }) => {
    const [notifications, setNotifications] = useState<Notification[]>([]);
    const [isPushSupported, setIsPushSupported] = useState(false);
    const [pushSubscribed, setPushSubscribed] = useState(false);
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

    // Check Push support & existing subscription
    useEffect(() => {
        if ('serviceWorker' in navigator && 'PushManager' in window) {
            setIsPushSupported(true);
            navigator.serviceWorker.register('/sw.js').then((registration) => {
                registration.pushManager.getSubscription().then((sub) => {
                    setPushSubscribed(!!sub);
                });
            });
        }
    }, []);

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

    // Push Notification Logic
    const subscribeToPush = async () => {
        if (!isPushSupported) return false;
        try {
            const registration = await navigator.serviceWorker.ready;
            // Get public key from backend
            const { data } = await getVapidPublicKey();

            const subscription = await registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: urlBase64ToUint8Array(data.public_key)
            });

            // Send to backend
            const subData = JSON.parse(JSON.stringify(subscription));
            await subscribePush({
                endpoint: subData.endpoint,
                p256dh: subData.keys.p256dh,
                auth: subData.keys.auth
            });

            setPushSubscribed(true);
            showToast("Successfully subscribed to notifications!", "success");
            return true;
        } catch (error) {
            console.error("Push subscription failed", error);
            showToast("Failed to enable push notifications", "error");
            return false;
        }
    };

    const unsubscribeFromPush = async () => {
        if (!isPushSupported) return false;
        try {
            const registration = await navigator.serviceWorker.ready;
            const subscription = await registration.pushManager.getSubscription();
            if (subscription) {
                await subscription.unsubscribe();
                await unsubscribePush(subscription.endpoint);
            }
            setPushSubscribed(false);
            showToast("Notifications disabled", "info");
            return true;
        } catch (error) {
            console.error("Push unsubscription failed", error);
            return false;
        }
    };

    return (
        <NotificationContext.Provider value={{
            notifications,
            unreadCount,
            markAsRead,
            markAllAsRead,
            refreshNotifications,
            isPushSupported,
            pushSubscribed,
            subscribeToPush,
            unsubscribeFromPush
        }}>
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
