"use client";

import React, { createContext, useContext, useReducer, useCallback } from "react";

// Loading state interface
interface LoadingState {
  [key: string]: boolean;
}

// Loading context interface
interface LoadingContextType {
  loadingStates: LoadingState;
  setLoading: (key: string, isLoading: boolean) => void;
  isLoading: (key: string) => boolean;
  isAnyLoading: () => boolean;
}

// Actions for the loading reducer
type LoadingAction =
  | { type: "SET_LOADING"; key: string; isLoading: boolean }
  | { type: "CLEAR_ALL" };

// Loading reducer
function loadingReducer(state: LoadingState, action: LoadingAction): LoadingState {
  switch (action.type) {
    case "SET_LOADING":
      return {
        ...state,
        [action.key]: action.isLoading,
      };
    case "CLEAR_ALL":
      return {};
    default:
      return state;
  }
}

// Create the context
const LoadingContext = createContext<LoadingContextType | undefined>(undefined);

// Loading provider component
export function LoadingProvider({ children }: { children: React.ReactNode }) {
  const [loadingStates, dispatch] = useReducer(loadingReducer, {});

  const setLoading = useCallback((key: string, isLoading: boolean) => {
    dispatch({ type: "SET_LOADING", key, isLoading });
  }, []);

  const isLoading = useCallback(
    (key: string) => {
      return loadingStates[key] || false;
    },
    [loadingStates]
  );

  const isAnyLoading = useCallback(() => {
    return Object.values(loadingStates).some(Boolean);
  }, [loadingStates]);

  const value: LoadingContextType = {
    loadingStates,
    setLoading,
    isLoading,
    isAnyLoading,
  };

  return <LoadingContext.Provider value={value}>{children}</LoadingContext.Provider>;
}

// Hook to use loading state
export function useLoading(): LoadingContextType {
  const context = useContext(LoadingContext);
  if (context === undefined) {
    throw new Error("useLoading must be used within a LoadingProvider");
  }
  return context;
}

// Convenience hook for managing a specific loading state
export function useLoadingState(key: string) {
  const { setLoading, isLoading } = useLoading();
  
  const setLoadingForKey = useCallback(
    (loading: boolean) => {
      setLoading(key, loading);
    },
    [key, setLoading]
  );

  const isLoadingForKey = isLoading(key);

  return [isLoadingForKey, setLoadingForKey] as const;
}

// Higher-order function to wrap async operations with loading state
export function withLoading<T extends (...args: any[]) => Promise<any>>(
  asyncFn: T,
  loadingKey: string,
  setLoading: (key: string, loading: boolean) => void
): (...args: Parameters<T>) => Promise<ReturnType<T>> {
  return async (...args: Parameters<T>) => {
    try {
      setLoading(loadingKey, true);
      const result = await asyncFn(...args);
      return result;
    } finally {
      setLoading(loadingKey, false);
    }
  };
}