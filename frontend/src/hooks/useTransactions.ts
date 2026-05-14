import { useState, useCallback, useRef, useEffect } from 'react';
import api from '../api';
import type { Transaction } from '../types';

const getAllTransactionsPublic = (params: Record<string, unknown> = {}) =>
    api.get('/transactions', { params: { skip: 0, limit: 100, ...params }, skipAuthRedirect: true });

export function useTransactions() {
    const [transactions, setTransactions] = useState<Transaction[]>([]);
    const [historyPage, setHistoryPage] = useState(1);
    const [hasMoreHistory, setHasMoreHistory] = useState(true);
    const [filters, setFilters] = useState<Record<string, unknown>>({});

    const stateRef = useRef({ filters, historyPage });
    useEffect(() => {
        stateRef.current = { filters, historyPage };
    }, [filters, historyPage]);

    const refreshTransactions = useCallback(async (newFilters = {}, reset = false) => {
        const { filters: currentFilters, historyPage: currentPageState } = stateRef.current;
        const updatedFilters = { ...currentFilters, ...newFilters };
        setFilters(updatedFilters);
        const currentPage = reset ? 1 : currentPageState;
        if (reset) setHistoryPage(1);

        try {
            const limit = 50;
            const transactionsRes = await getAllTransactionsPublic({
                skip: (currentPage - 1) * limit,
                limit,
                ...updatedFilters
            });

            if (reset) {
                setTransactions(transactionsRes.data);
            } else {
                setTransactions(prev => [...prev, ...transactionsRes.data]);
            }

            setHasMoreHistory(transactionsRes.data.length === limit);
        } catch (error) {
            console.error("Failed to refresh transactions", error);
        }
    }, []);

    const loadMoreHistory = useCallback(() => {
        setHistoryPage(prev => prev + 1);
    }, []);

    return {
        transactions,
        historyPage,
        hasMoreHistory,
        filters,
        setFilters,
        refreshTransactions,
        loadMoreHistory
    };
}
