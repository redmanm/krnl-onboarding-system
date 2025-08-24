"use client";

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Heart,
  RefreshCw,
  Activity,
  Database,
  Server,
  Cpu,
  HardDrive,
  Network,
  AlertTriangle,
  CheckCircle,
  Clock,
  Zap,
  BarChart3,
  TrendingUp,
  TrendingDown,
  Minus,
} from "lucide-react";
import { DashboardLayout } from "@/components/navigation";
import { useNotifications } from "@/lib/notifications";
import { useLoadingState } from "@/lib/loading";
import {
  getSystemHealth,
  getAgentPerformance,
  formatTime,
  getStatusClass,
  type SystemHealth,
  type AgentMetrics,
} from "@/lib/api";

export default function SystemHealthPage() {
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [agentPerformance, setAgentPerformance] = useState<AgentMetrics[]>([]);
  const [lastUpdated, setLastUpdated] = useState<string>("");

  const { showError, showSuccess } = useNotifications();
  const [isHealthLoading, setHealthLoading] = useLoadingState("health");
  const [isAgentsLoading, setAgentsLoading] = useLoadingState("agents");

  // Load system health
  const loadSystemHealth = async () => {
    try {
      setHealthLoading(true);
      const healthData = await getSystemHealth();
      setSystemHealth(healthData);
      setLastUpdated(new Date().toISOString());
    } catch (error) {
      showError("Failed to load system health");
      console.error("System health error:", error);
    } finally {
      setHealthLoading(false);
    }
  };

  // Load agent performance
  const loadAgentPerformance = async () => {
    try {
      setAgentsLoading(true);
      const agentData = await getAgentPerformance();
      setAgentPerformance(agentData);
    } catch (error) {
      showError("Failed to load agent performance");
      console.error("Agent performance error:", error);
    } finally {
      setAgentsLoading(false);
    }
  };

  // Load all data
  const loadAllData = async () => {
    await Promise.all([loadSystemHealth(), loadAgentPerformance()]);
    showSuccess("System health data refreshed");
  };

  useEffect(() => {
    loadAllData();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(loadAllData, 30000);
    
    return () => clearInterval(interval);
  }, []);

  // Get status variant for badges
  const getStatusVariant = (status: string) => {
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

  // Get health status color
  const getHealthStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case "healthy":
      case "online":
        return "text-green-400";
      case "degraded":
      case "warning":
        return "text-yellow-400";
      case "unhealthy":
      case "offline":
      case "error":
        return "text-red-400";
      default:
        return "text-gray-400";
    }
  };

  // Get health status icon
  const getHealthStatusIcon = (status: string) => {
    switch (status?.toLowerCase()) {
      case "healthy":
      case "online":
        return <CheckCircle className="h-5 w-5 text-green-400" />;
      case "degraded":
      case "warning":
        return <AlertTriangle className="h-5 w-5 text-yellow-400" />;
      case "unhealthy":
      case "offline":
      case "error":
        return <AlertTriangle className="h-5 w-5 text-red-400" />;
      default:
        return <Clock className="h-5 w-5 text-gray-400" />;
    }
  };

  // Mock system metrics (in a real app, these would come from the API)
  const systemMetrics = {
    cpu: { usage: 45, status: "healthy" },
    memory: { usage: 67, status: "healthy" },
    disk: { usage: 34, status: "healthy" },
    network: { usage: 23, status: "healthy" },
  };

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6 max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">System Health Monitor</h1>
            <p className="text-muted-foreground">
              Real-time system health and performance metrics
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <div className="text-sm text-muted-foreground">
              Last updated: {lastUpdated ? formatTime(lastUpdated) : "Never"}
            </div>
            <Button variant="outline" onClick={loadAllData} disabled={isHealthLoading || isAgentsLoading}>
              <RefreshCw className={`h-4 w-4 mr-2 ${(isHealthLoading || isAgentsLoading) ? "animate-spin" : ""}`} />
              Refresh
            </Button>
          </div>
        </div>

        {/* System Status Overview */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Heart className="h-5 w-5" />
                <span>System Status Overview</span>
              </CardTitle>
              <CardDescription>Current status of all system components</CardDescription>
            </CardHeader>
            <CardContent>
              {isHealthLoading ? (
                <div className="space-y-6">
                  <div className="flex items-center justify-center">
                    <Skeleton className="h-24 w-24 rounded-full" />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <Skeleton className="h-20" />
                    <Skeleton className="h-20" />
                  </div>
                </div>
              ) : systemHealth ? (
                <div className="space-y-6">
                  {/* Main Status */}
                  <div className="text-center">
                    <div className="flex items-center justify-center mb-4">
                      {getHealthStatusIcon(systemHealth.system_status)}
                    </div>
                    <h3 className="text-2xl font-bold mb-2">System {systemHealth.system_status}</h3>
                    <p className="text-muted-foreground">
                      Overall system health based on recent activity
                    </p>
                  </div>

                  {/* Workflow Metrics */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="text-center p-4 bg-muted/30 rounded-lg">
                      <div className="text-2xl font-bold text-green-400">
                        {systemHealth.workflow_metrics?.success_rate?.toFixed(1) || 0}%
                      </div>
                      <div className="text-sm text-muted-foreground">Success Rate</div>
                    </div>
                    <div className="text-center p-4 bg-muted/30 rounded-lg">
                      <div className="text-2xl font-bold">
                        {systemHealth.workflow_metrics?.total_workflows || 0}
                      </div>
                      <div className="text-sm text-muted-foreground">Total Workflows</div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <Heart className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground">Unable to load system status</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Quick Stats */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Stats</CardTitle>
              <CardDescription>Key system metrics at a glance</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Database className="h-4 w-4 text-blue-400" />
                  <span className="text-sm">Active Agents</span>
                </div>
                <span className="font-medium">{agentPerformance.length}</span>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Activity className="h-4 w-4 text-green-400" />
                  <span className="text-sm">Completed Workflows</span>
                </div>
                <span className="font-medium">{systemHealth?.workflow_metrics?.completed_workflows || 0}</span>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <AlertTriangle className="h-4 w-4 text-red-400" />
                  <span className="text-sm">Failed Workflows</span>
                </div>
                <span className="font-medium">{systemHealth?.workflow_metrics?.failed_workflows || 0}</span>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Clock className="h-4 w-4 text-yellow-400" />
                  <span className="text-sm">Uptime</span>
                </div>
                <span className="font-medium">99.9%</span>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Detailed Metrics */}
        <Tabs defaultValue="infrastructure" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="infrastructure">Infrastructure</TabsTrigger>
            <TabsTrigger value="agents">Agent Health</TabsTrigger>
            <TabsTrigger value="performance">Performance</TabsTrigger>
          </TabsList>

          {/* Infrastructure Tab */}
          <TabsContent value="infrastructure" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">CPU Usage</CardTitle>
                  <Cpu className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{systemMetrics.cpu.usage}%</div>
                  <Progress value={systemMetrics.cpu.usage} className="mt-2" />
                  <p className="text-xs text-muted-foreground mt-2">
                    Status: <span className={getHealthStatusColor(systemMetrics.cpu.status)}>
                      {systemMetrics.cpu.status}
                    </span>
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Memory Usage</CardTitle>
                  <Server className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{systemMetrics.memory.usage}%</div>
                  <Progress value={systemMetrics.memory.usage} className="mt-2" />
                  <p className="text-xs text-muted-foreground mt-2">
                    Status: <span className={getHealthStatusColor(systemMetrics.memory.status)}>
                      {systemMetrics.memory.status}
                    </span>
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Disk Usage</CardTitle>
                  <HardDrive className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{systemMetrics.disk.usage}%</div>
                  <Progress value={systemMetrics.disk.usage} className="mt-2" />
                  <p className="text-xs text-muted-foreground mt-2">
                    Status: <span className={getHealthStatusColor(systemMetrics.disk.status)}>
                      {systemMetrics.disk.status}
                    </span>
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Network I/O</CardTitle>
                  <Network className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{systemMetrics.network.usage}%</div>
                  <Progress value={systemMetrics.network.usage} className="mt-2" />
                  <p className="text-xs text-muted-foreground mt-2">
                    Status: <span className={getHealthStatusColor(systemMetrics.network.status)}>
                      {systemMetrics.network.status}
                    </span>
                  </p>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Agent Health Tab */}
          <TabsContent value="agents" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {isAgentsLoading ? (
                Array.from({ length: 4 }).map((_, i) => (
                  <Card key={i}>
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <Skeleton className="h-6 w-32" />
                        <Skeleton className="h-6 w-16" />
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <Skeleton className="h-4 w-full" />
                      <Skeleton className="h-2 w-full" />
                      <div className="grid grid-cols-3 gap-4">
                        <Skeleton className="h-8" />
                        <Skeleton className="h-8" />
                        <Skeleton className="h-8" />
                      </div>
                    </CardContent>
                  </Card>
                ))
              ) : (
                agentPerformance.map((agent) => {
                  const successRate = agent.metrics?.success_rate || 0;
                  const isHealthy = successRate >= 90;
                  
                  return (
                    <Card key={agent.agent_type}>
                      <CardHeader>
                        <div className="flex items-center justify-between">
                          <CardTitle className="capitalize">
                            {agent.agent_type.replace('_', ' ')} Agent
                          </CardTitle>
                          <Badge variant={isHealthy ? "default" : "destructive"}>
                            {isHealthy ? "Healthy" : "Degraded"}
                          </Badge>
                        </div>
                        <CardDescription>
                          {agent.agent_type === "validator" && "Validates and cleans employee data"}
                          {agent.agent_type === "account_setup" && "Creates system accounts and permissions"}
                          {agent.agent_type === "scheduler" && "Schedules orientation and meetings"}
                          {agent.agent_type === "notifier" && "Sends notifications and confirmations"}
                        </CardDescription>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        <div className="flex items-center justify-between">
                          <span className="text-sm">Health Score</span>
                          <span className="font-medium">{successRate.toFixed(1)}%</span>
                        </div>
                        <Progress value={successRate} className="h-2" />
                        
                        <div className="grid grid-cols-3 gap-4 text-center">
                          <div>
                            <div className="text-lg font-bold">{agent.metrics?.total_executions || 0}</div>
                            <div className="text-xs text-muted-foreground">Total</div>
                          </div>
                          <div>
                            <div className="text-lg font-bold text-green-400">
                              {agent.metrics?.successful_executions || 0}
                            </div>
                            <div className="text-xs text-muted-foreground">Success</div>
                          </div>
                          <div>
                            <div className="text-lg font-bold text-red-400">
                              {agent.metrics?.failed_executions || 0}
                            </div>
                            <div className="text-xs text-muted-foreground">Failed</div>
                          </div>
                        </div>

                        <div className="pt-2 border-t">
                          <div className="flex items-center justify-between text-sm">
                            <span>Avg Response Time</span>
                            <span>{(agent.metrics?.average_execution_time_ms || 0).toFixed(0)}ms</span>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })
              )}
            </div>
          </TabsContent>

          {/* Performance Tab */}
          <TabsContent value="performance" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Workflow Performance</CardTitle>
                  <CardDescription>System-wide workflow execution metrics</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {systemHealth ? (
                    <>
                      <div className="flex items-center justify-between">
                        <span>Total Workflows Processed</span>
                        <span className="font-medium">{systemHealth.workflow_metrics?.total_workflows || 0}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span>Success Rate</span>
                        <span className="font-medium text-green-400">
                          {systemHealth.workflow_metrics?.success_rate?.toFixed(1) || 0}%
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span>Completed Successfully</span>
                        <span className="font-medium">{systemHealth.workflow_metrics?.completed_workflows || 0}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span>Failed Workflows</span>
                        <span className="font-medium text-red-400">{systemHealth.workflow_metrics?.failed_workflows || 0}</span>
                      </div>
                      <Progress 
                        value={systemHealth.workflow_metrics?.success_rate || 0} 
                        className="mt-4"
                      />
                    </>
                  ) : (
                    <div className="space-y-2">
                      <Skeleton className="h-4 w-full" />
                      <Skeleton className="h-4 w-full" />
                      <Skeleton className="h-4 w-full" />
                      <Skeleton className="h-4 w-full" />
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>System Trends</CardTitle>
                  <CardDescription>Performance trends over time</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span>Response Time Trend</span>
                    <div className="flex items-center text-green-400">
                      <TrendingDown className="h-4 w-4 mr-1" />
                      <span className="text-sm">-12% faster</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Success Rate Trend</span>
                    <div className="flex items-center text-green-400">
                      <TrendingUp className="h-4 w-4 mr-1" />
                      <span className="text-sm">+2.3% improvement</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Error Rate Trend</span>
                    <div className="flex items-center text-green-400">
                      <TrendingDown className="h-4 w-4 mr-1" />
                      <span className="text-sm">-15% reduction</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Throughput Trend</span>
                    <div className="flex items-center text-gray-400">
                      <Minus className="h-4 w-4 mr-1" />
                      <span className="text-sm">Stable</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Performance Chart Placeholder */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <BarChart3 className="h-5 w-5" />
                  <span>Performance Metrics Over Time</span>
                </CardTitle>
                <CardDescription>Historical performance data visualization</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-64 flex items-center justify-center bg-muted/30 rounded-lg">
                  <div className="text-center">
                    <BarChart3 className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                    <p className="text-muted-foreground">Performance charts would be displayed here</p>
                    <p className="text-sm text-muted-foreground">Integration with charting library required</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  );
}