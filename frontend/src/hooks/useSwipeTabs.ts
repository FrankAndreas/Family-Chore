import { useRef, useCallback } from 'react';

interface SwipeHandlers {
    onTouchStart: (e: React.TouchEvent) => void;
    onTouchMove: (e: React.TouchEvent) => void;
    onTouchEnd: () => void;
}

/**
 * Custom hook for swipe-based tab navigation on mobile devices.
 *
 * @param tabs - Ordered array of tab identifiers (e.g. ['tasks', 'redeem', 'history'])
 * @param activeTab - The currently active tab
 * @param setActiveTab - State setter to change the active tab
 * @param threshold - Minimum horizontal swipe distance in pixels (default: 50)
 * @returns Touch event handlers to spread onto the swipeable container
 */
export function useSwipeTabs<T extends string>(
    tabs: readonly T[],
    activeTab: T,
    setActiveTab: (tab: T) => void,
    threshold = 50
): SwipeHandlers {
    const touchStartX = useRef<number>(0);
    const touchStartY = useRef<number>(0);
    const lastTouchX = useRef<number>(0);
    const isSwiping = useRef<boolean>(false);

    const onTouchStart = useCallback((e: React.TouchEvent) => {
        touchStartX.current = e.touches[0].clientX;
        touchStartY.current = e.touches[0].clientY;
        lastTouchX.current = e.touches[0].clientX;
        isSwiping.current = true;
    }, []);

    const onTouchMove = useCallback((e: React.TouchEvent) => {
        if (!isSwiping.current) return;

        lastTouchX.current = e.touches[0].clientX;
        const deltaX = e.touches[0].clientX - touchStartX.current;
        const deltaY = e.touches[0].clientY - touchStartY.current;

        // If vertical movement exceeds horizontal, cancel the swipe
        // to allow normal page scrolling
        if (Math.abs(deltaY) > Math.abs(deltaX)) {
            isSwiping.current = false;
        }
    }, []);

    const onTouchEnd = useCallback(() => {
        if (!isSwiping.current) return;
        isSwiping.current = false;

        const deltaX = lastTouchX.current - touchStartX.current;
        if (Math.abs(deltaX) < threshold) return;

        const currentIndex = tabs.indexOf(activeTab);
        if (currentIndex === -1) return;

        if (deltaX < -threshold && currentIndex < tabs.length - 1) {
            // Swipe left → next tab
            setActiveTab(tabs[currentIndex + 1]);
        } else if (deltaX > threshold && currentIndex > 0) {
            // Swipe right → previous tab
            setActiveTab(tabs[currentIndex - 1]);
        }
    }, [tabs, activeTab, setActiveTab, threshold]);

    return { onTouchStart, onTouchMove, onTouchEnd };
}
