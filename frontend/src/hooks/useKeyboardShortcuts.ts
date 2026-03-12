import { useEffect, useCallback, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';

interface ShortcutConfig {
    key: string;
    altKey?: boolean;
    ctrlKey?: boolean;
    description: string;
    action: () => void;
}

/**
 * Hook that registers global keyboard shortcuts for dashboard navigation.
 *
 * Shortcuts:
 * - Alt+1: Go to Dashboard (My Tasks)
 * - Alt+2: Go to Rewards
 * - Alt+3: Go to Settings
 * - Alt+4: Go to Admin Dashboard (admin only)
 * - Alt+5: Go to Users (admin only)
 * - ?: Show shortcut help (via callback)
 *
 * Shortcuts are suppressed when focus is inside an input, textarea, or select.
 */
export function useKeyboardShortcuts(
    isAdmin: boolean,
    onShowHelp?: () => void
) {
    const navigate = useNavigate();

    const shortcuts: ShortcutConfig[] = useMemo(() => [
        { key: '1', altKey: true, description: 'Go to My Tasks', action: () => navigate('/dashboard') },
        { key: '2', altKey: true, description: 'Go to Rewards', action: () => navigate('/rewards') },
        { key: '3', altKey: true, description: 'Go to Settings', action: () => navigate('/settings') },
        ...(isAdmin ? [
            { key: '4', altKey: true, description: 'Go to Admin Dashboard', action: () => navigate('/admin') },
            { key: '5', altKey: true, description: 'Go to Users', action: () => navigate('/admin/users') },
        ] : []),
    ], [isAdmin, navigate]);

    const handleKeyDown = useCallback((event: KeyboardEvent) => {
        // Don't trigger shortcuts when typing in form fields
        const target = event.target as HTMLElement;
        const isInputFocused = ['INPUT', 'TEXTAREA', 'SELECT'].includes(target.tagName) ||
            target.isContentEditable;

        if (isInputFocused) return;

        // ? key to show help (no modifiers)
        if (event.key === '?' && !event.altKey && !event.ctrlKey && !event.metaKey) {
            event.preventDefault();
            onShowHelp?.();
            return;
        }

        for (const shortcut of shortcuts) {
            const altMatch = shortcut.altKey ? event.altKey : !event.altKey;
            const ctrlMatch = shortcut.ctrlKey ? event.ctrlKey : !event.ctrlKey;

            if (event.key === shortcut.key && altMatch && ctrlMatch) {
                event.preventDefault();
                shortcut.action();
                return;
            }
        }
    }, [shortcuts, onShowHelp]);

    useEffect(() => {
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [handleKeyDown]);

    return shortcuts;
}
