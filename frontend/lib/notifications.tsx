"use client";

import React, { createContext, useContext, useCallback } from "react";
import { toast } from "sonner";
import { CheckCircle, XCircle, AlertCircle, Info } from "lucide-react";

// Notification types
export type NotificationType = "success" | "error" | "warning" | "info";

export interface NotificationOptions {
  duration?: number;
  position?: "top-center" | "top-right" | "bottom-center" | "bottom-right";
  dismissible?: boolean;
}

// Notification context interface
interface NotificationContextType {
  showNotification: (
    message: string,
    type?: NotificationType,
    options?: NotificationOptions
  ) => void;
  showSuccess: (message: string, options?: NotificationOptions) => void;
  showError: (message: string, options?: NotificationOptions) => void;
  showWarning: (message: string, options?: NotificationOptions) => void;
  showInfo: (message: string, options?: NotificationOptions) => void;
}

// Create the context
const NotificationContext = createContext<NotificationContextType | undefined>(
  undefined
);

// Notification provider component
export function NotificationProvider({ children }: { children: React.ReactNode }) {
  const showNotification = useCallback(
    (
      message: string,
      type: NotificationType = "info",
      options: NotificationOptions = {}
    ) => {
      const { duration = 5000, dismissible = true } = options;

      // Get the appropriate icon and styling based on type
      const getNotificationConfig = (type: NotificationType) => {
        switch (type) {
          case "success":
            return {
              icon: <CheckCircle className="h-4 w-4" />,
              className: "border-green-500/20 bg-green-500/10 text-green-400",
            };
          case "error":
            return {
              icon: <XCircle className="h-4 w-4" />,
              className: "border-red-500/20 bg-red-500/10 text-red-400",
            };
          case "warning":
            return {
              icon: <AlertCircle className="h-4 w-4" />,
              className: "border-yellow-500/20 bg-yellow-500/10 text-yellow-400",
            };
          case "info":
          default:
            return {
              icon: <Info className="h-4 w-4" />,
              className: "border-blue-500/20 bg-blue-500/10 text-blue-400",
            };
        }
      };

      const config = getNotificationConfig(type);

      toast(message, {
        duration,
        dismissible,
        icon: config.icon,
        className: `${config.className} border backdrop-blur-sm`,
        style: {
          background: "var(--background)",
          border: "1px solid var(--border)",
          color: "var(--foreground)",
        },
      });
    },
    []
  );

  const showSuccess = useCallback(
    (message: string, options?: NotificationOptions) => {
      showNotification(message, "success", options);
    },
    [showNotification]
  );

  const showError = useCallback(
    (message: string, options?: NotificationOptions) => {
      showNotification(message, "error", options);
    },
    [showNotification]
  );

  const showWarning = useCallback(
    (message: string, options?: NotificationOptions) => {
      showNotification(message, "warning", options);
    },
    [showNotification]
  );

  const showInfo = useCallback(
    (message: string, options?: NotificationOptions) => {
      showNotification(message, "info", options);
    },
    [showNotification]
  );

  const value: NotificationContextType = {
    showNotification,
    showSuccess,
    showError,
    showWarning,
    showInfo,
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
}

// Hook to use notifications
export function useNotifications(): NotificationContextType {
  const context = useContext(NotificationContext);
  if (context === undefined) {
    throw new Error(
      "useNotifications must be used within a NotificationProvider"
    );
  }
  return context;
}

// Convenience hooks for specific notification types
export function useSuccessNotification() {
  const { showSuccess } = useNotifications();
  return showSuccess;
}

export function useErrorNotification() {
  const { showError } = useNotifications();
  return showError;
}

export function useWarningNotification() {
  const { showWarning } = useNotifications();
  return showWarning;
}

export function useInfoNotification() {
  const { showInfo } = useNotifications();
  return showInfo;
}