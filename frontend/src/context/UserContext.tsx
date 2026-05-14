import { createContext, useContext } from 'react';
import type { User } from '../types';

interface UserContextType {
    currentUser: User;
    refreshUser: () => Promise<void>;
    logout: () => void;
}

export const UserContext = createContext<UserContextType | undefined>(undefined);

export function useUser() {
    const context = useContext(UserContext);
    if (context === undefined) {
        throw new Error('useUser must be used within a UserContext.Provider');
    }
    return context;
}
