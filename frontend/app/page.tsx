"use client";

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Users,
  UserPlus,
  Clock,
  CheckCircle,
  Activity,
  RefreshCw,
  TrendingUp,
  TrendingDown,
  Minus,
} from "lucide-react";
import { DashboardLayout } from "@/components/navigation";
import { useNotifications } from "@/lib/notifications";
import { useLoadingState } from "@/lib/loading";
import {
  getDashboardStats,
  getRecentActivity,
  getSystemHealth,
  getAgentPerformance,
  formatTime,
  getStatusClass,
  type DashboardStats,
  type RecentActivity,
  type SystemHealth,
  type AgentMetrics,
} from "@/lib/api";

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([]);
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [agentPerformance, setAgentPerformance] = useState<AgentMetrics[]>([]);
  
  const { showError, showSuccess } = useNotifications();
  const [isDashboardLoading, setDashboardLoading] = useLoadingState("dashboard");
  const [isActivityLoading, setActivityLoading] = useLoadingState("activity");
  const [isHealthLoading, setHealthLoading] = useLoadingState("health");
  const [isAgentsLoading, setAgentsLoading] = useLoadingState("agents");

  // Load dashboard data
  const loadDashboardData = async () => {
    try {
      setDashboardLoading(true);
      const dashboardStats = await getDashboardStats();
      setStats(dashboardStats);
    } catch (error) {
      showError("Failed to load dashboard statistics");
      console.error("Dashboard stats error:", error);
    } finally {
      setDashboardLoading(false);
    }
  };

  // Load recent activity
  const loadRecentActivity = async () => {
    try {
      setActivityLoading(true);
      const activityData = await getRecentActivity(10);
      setRecentActivity(activityData.recent_activity || []);
    } catch (error) {
      showError("Failed to load recent activity");
      console.error("Recent activity error:", error);
    } finally {
      setActivityLoading(false);
    }
  };

  // Load all data on component mount
  useEffect(() => {
    loadDashboardData();
    loadRecentActivity();
  }, []);

  // Get status color for badges
  const getStatusColor = (status: string) => {
    const statusClass = getStatusClass(status);
    switch (statusClass) {
      case "completed":
        return "default";
      case "pending":
        return "secondary";
      case "failed":
        return "destructive";
      default:
        return "outline";
    }
  };

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6 max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Dashboard Overview</h1>
            <p className="text-muted-foreground">
              Monitor your onboarding workflows and system performance
            </p>
          </div>
          <Button
            variant="outline"
            onClick={loadDashboardData}
            disabled={isDashboardLoading}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isDashboardLoading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Employees</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              {isDashboardLoading ? (
                <Skeleton className="h-8 w-16" />
              ) : (
                <div className="text-2xl font-bold">{stats?.total_employees || 0}</div>
              )}
              <p className="text-xs text-muted-foreground">All employees</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Pending</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              {isDashboardLoading ? (
                <Skeleton className="h-8 w-16" />
              ) : (
                <div className="text-2xl font-bold">{stats?.pending_onboarding || 0}</div>
              )}
              <p className="text-xs text-muted-foreground">In progress</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Completed</CardTitle>
              <CheckCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              {isDashboardLoading ? (
                <Skeleton className="h-8 w-16" />
              ) : (
                <div className="text-2xl font-bold">{stats?.completed_onboarding || 0}</div>
              )}
              <p className="text-xs text-muted-foreground">Successfully onboarded</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Failed</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              {isDashboardLoading ? (
                <Skeleton className="h-8 w-16" />
              ) : (
                <div className="text-2xl font-bold">{stats?.failed_onboarding || 0}</div>
              )}
              <p className="text-xs text-muted-foreground">Requires attention</p>
            </CardContent>
          </Card>
        </div>

        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>Latest onboarding events</CardDescription>
          </CardHeader>
          <CardContent>
            {isActivityLoading ? (
              <div className="space-y-4">
                {Array.from({ length: 5 }).map((_, i) => (
                  <div key={i} className="flex items-center space-x-4">
                    <Skeleton className="h-2 w-2 rounded-full" />
                    <div className="flex-1">
                      <Skeleton className="h-4 w-32 mb-1" />
                      <Skeleton className="h-3 w-48" />
                    </div>
                    <Skeleton className="h-3 w-16" />
                  </div>
                ))}
              </div>
            ) : recentActivity.length > 0 ? (
              <div className="space-y-4">
                {recentActivity.slice(0, 5).map((activity, index) => {
                  const statusClass = getStatusClass(activity.status);
                  return (
                    <div key={index} className="flex items-center space-x-4">
                      <div 
                        className={`h-2 w-2 rounded-full ${
                          statusClass === 'completed' ? 'bg-green-500' :
                          statusClass === 'pending' ? 'bg-yellow-500' :
                          statusClass === 'failed' ? 'bg-red-500' : 'bg-gray-500'
                        }`} 
                      />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">{activity.employee_name}</p>
                        <p className="text-xs text-muted-foreground truncate">
                          {activity.current_step}
                        </p>
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {formatTime(activity.created_at).split(' ')[1]}
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="text-center py-8">
                <Activity className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                <p className="text-sm text-muted-foreground">No recent activity</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
