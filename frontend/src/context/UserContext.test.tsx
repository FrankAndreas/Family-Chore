import React from 'react';
import { render, screen } from '@testing-library/react';
import { UserContext, useUser } from './UserContext';
import { describe, it, expect } from 'vitest';

const TestComponent = () => {
    const { currentUser } = useUser();
    return (
        <div data-testid="test-child">
            {currentUser ? currentUser.nickname : 'No User'}
        </div>
    );
};

describe('UserContext', () => {
    it('renders children correctly', () => {
        // @ts-expect-error - Mock user for testing
        const mockValue = { currentUser: { nickname: 'TestUser' }, refreshUser: async () => {}, logout: () => {} };
        render(
            <UserContext.Provider value={mockValue}>
                <TestComponent />
            </UserContext.Provider>
        );
        expect(screen.getByTestId('test-child')).toHaveTextContent('TestUser');
    });
});
