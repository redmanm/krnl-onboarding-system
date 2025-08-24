"use client";

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  ClipboardCheck,
  Search,
  RefreshCw,
  Download,
  Filter,
  Play,
  Pause,
  RotateCcw,
  Save,
  CheckCircle,
  AlertCircle,
  Clock,
  Activity,
  Database,
  TrendingUp,
  TrendingDown,
  Minus,
} from "lucide-react";
import { DashboardLayout } from "@/components/navigation";
import { useNotifications } from "@/lib/notifications";
import { useLoadingState } from "@/lib/loading";
import {
  getAgentPerformance,
  searchLogs,
  formatTime,
  getStatusClass,
  type AgentMetrics,
  type LogEntry,
  type SearchFilters,
} from "@/lib/api";

export default function AuditLogsPage() {
  const [agentPerformance, setAgentPerformance] = useState<AgentMetrics[]>([]);
  const [searchResults, setSearchResults] = useState<LogEntry[]>([]);
  const [resultCount, setResultCount] = useState(0);
  const [isActivityPaused, setIsActivityPaused] = useState(false);
  const [activityFeedInterval, setActivityFeedInterval] = useState<NodeJS.Timeout | null>(null);
  
  // Search filters state
  const [searchFilters, setSearchFilters] = useState<SearchFilters>({
    agent_type: "all_agents",
    status: "all_status",
    priority: "all_priorities",
    start_date: "",
    end_date: "",
    search_term: "",
    limit: 50,
  });

  const { showError, showSuccess, showInfo } = useNotifications();
  const [isAgentsLoading, setAgentsLoading] = useLoadingState("agents");
  const [isSearchLoading, setSearchLoading] = useLoadingState("search");
  const [isActivityLoading, setActivityLoading] = useLoadingState("activity");

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

  // Perform log search
  const performLogSearch = async () => {
    try {
      setSearchLoading(true);
      
      // Remove empty filters and placeholder values
      const cleanFilters = Object.fromEntries(
        Object.entries(searchFilters).filter(([_, value]) => {
          if (value === '' || value === undefined) return false;
          // Exclude placeholder values
          if (value === 'all_agents' || value === 'all_status' || value === 'all_priorities') return false;
          return true;
        })
      );
      
      const results = await searchLogs(cleanFilters);
      setSearchResults(results.logs || []);
      setResultCount(results.result_count || 0);
      
      if (results.logs?.length === 0) {
        showInfo("No log entries match your search criteria");
      }
    } catch (error) {
      showError("Failed to search logs");
      console.error("Log search error:", error);
      setSearchResults([]);
      setResultCount(0);
    } finally {
      setSearchLoading(false);
    }
  };

  // Load realtime activity (simplified for now)
  const loadRealtimeActivity = async () => {
    if (isActivityPaused) return;
    
    try {
      // This would normally load recent activity
      // For now, we'll use the search results as activity
      const recentFilters = {
        limit: 10,
        // Get recent entries only
      };
      
      const results = await searchLogs(recentFilters);
      // Update activity feed here if needed
    } catch (error) {
      console.error("Failed to load realtime activity:", error);
    }
  };

  // Toggle activity feed pause
  const toggleActivityPause = () => {
    setIsActivityPaused(!isActivityPaused);
    
    if (!isActivityPaused) {
      // Pausing
      if (activityFeedInterval) {
        clearInterval(activityFeedInterval);
        setActivityFeedInterval(null);
      }
      showInfo("Activity feed paused");
    } else {
      // Resuming
      const interval = setInterval(loadRealtimeActivity, 5000);
      setActivityFeedInterval(interval);
      showInfo("Activity feed resumed");
    }
  };

  // Reset search filters
  const resetSearchFilters = () => {
    setSearchFilters({
      agent_type: "all_agents",
      status: "all_status",
      priority: "all_priorities",
      start_date: "",
      end_date: "",
      search_term: "",
      limit: 50,
    });
    setSearchResults([]);
    setResultCount(0);
    showInfo("Search filters reset");
  };

  // Save search preset (mock implementation)
  const saveSearchPreset = () => {
    const presetName = prompt('Enter a name for this search preset:');
    if (presetName) {
      const presets = JSON.parse(localStorage.getItem('auditSearchPresets') || '{}');
      presets[presetName] = searchFilters;
      localStorage.setItem('auditSearchPresets', JSON.stringify(presets));
      showSuccess(`Search preset "${presetName}" saved successfully`);
    }
  };

  // Export search results (mock implementation)
  const exportSearchResults = () => {
    showInfo("Generating audit report...");
    setTimeout(() => {
      showSuccess("Audit report exported successfully");
    }, 2000);
  };

  useEffect(() => {
    loadAgentPerformance();
    
    // Set default dates
    const today = new Date().toISOString().split('T')[0];
    const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
    setSearchFilters(prev => ({
      ...prev,
      start_date: weekAgo,
      end_date: today,
    }));

    // Start activity feed
    const interval = setInterval(loadRealtimeActivity, 5000);
    setActivityFeedInterval(interval);

    return () => {
      if (interval) clearInterval(interval);
    };
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

  // Get trend indicator
  const getTrendIndicator = (value: number, isPositive: boolean) => {
    const Icon = isPositive ? TrendingUp : value === 0 ? Minus : TrendingDown;
    const colorClass = isPositive ? "text-green-400" : value === 0 ? "text-gray-400" : "text-red-400";
    
    return (
      <div className={`flex items-center ${colorClass} text-sm`}>
        <Icon className="h-3 w-3 mr-1" />
        <span>{isPositive ? '+' : ''}{value}%</span>
      </div>
    );
  };

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6 max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Audit Logs & Analytics</h1>
            <p className="text-muted-foreground">
              Comprehensive monitoring and analytics for your onboarding workflows
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <Button variant="outline" onClick={loadAgentPerformance} disabled={isAgentsLoading}>
              <RefreshCw className={`h-4 w-4 mr-2 ${isAgentsLoading ? "animate-spin" : ""}`} />
              Refresh
            </Button>
            <Button onClick={exportSearchResults}>
              <Download className="h-4 w-4 mr-2" />
              Export Report
            </Button>
          </div>
        </div>

        {/* Overview Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-6">
          <Card className="relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-green-500/10 to-emerald-500/10" />
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 relative">
              <CardTitle className="text-sm font-medium">Successful Operations</CardTitle>
              <CheckCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent className="relative">
              <div className="text-2xl font-bold">
                {agentPerformance.reduce((sum, agent) => sum + (agent.metrics?.successful_executions || 0), 0)}
              </div>
              <div className="flex items-center justify-between">
                <p className="text-xs text-muted-foreground">Total successful</p>
                {getTrendIndicator(15, true)}
              </div>
            </CardContent>
          </Card>

          <Card className="relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-red-500/10 to-pink-500/10" />
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 relative">
              <CardTitle className="text-sm font-medium">Failed Operations</CardTitle>
              <AlertCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent className="relative">
              <div className="text-2xl font-bold">
                {agentPerformance.reduce((sum, agent) => sum + (agent.metrics?.failed_executions || 0), 0)}
              </div>
              <div className="flex items-center justify-between">
                <p className="text-xs text-muted-foreground">Total failed</p>
                {getTrendIndicator(-8, false)}
              </div>
            </CardContent>
          </Card>

          <Card className="relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-purple-500/10" />
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 relative">
              <CardTitle className="text-sm font-medium">Avg Response Time</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent className="relative">
              <div className="text-2xl font-bold">
                {agentPerformance.length > 0
                  ? Math.round(agentPerformance.reduce((sum, agent) => sum + (agent.metrics?.average_execution_time_ms || 0), 0) / agentPerformance.length)
                  : 0}ms
              </div>
              <div className="flex items-center justify-between">
                <p className="text-xs text-muted-foreground">Average execution</p>
                {getTrendIndicator(-12, true)}
              </div>
            </CardContent>
          </Card>

          <Card className="relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-yellow-500/10 to-orange-500/10" />
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 relative">
              <CardTitle className="text-sm font-medium">Active Agents</CardTitle>
              <Database className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent className="relative">
              <div className="text-2xl font-bold">{agentPerformance.length}</div>
              <div className="flex items-center justify-between">
                <p className="text-xs text-muted-foreground">Currently running</p>
                {getTrendIndicator(0, false)}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Content Tabs */}
        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="search">Log Search</TabsTrigger>
            <TabsTrigger value="activity">Real-time Activity</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Agent Performance Dashboard</CardTitle>
                <CardDescription>Real-time monitoring of all system agents</CardDescription>
              </CardHeader>
              <CardContent>
                {isAgentsLoading ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {Array.from({ length: 4 }).map((_, i) => (
                      <div key={i} className="space-y-4 p-4 border rounded-lg">
                        <div className="flex items-center justify-between">
                          <Skeleton className="h-6 w-32" />
                          <Skeleton className="h-6 w-16" />
                        </div>
                        <Skeleton className="h-2 w-full" />
                        <div className="grid grid-cols-3 gap-4">
                          <div className="text-center">
                            <Skeleton className="h-6 w-8 mx-auto mb-1" />
                            <Skeleton className="h-3 w-16 mx-auto" />
                          </div>
                          <div className="text-center">
                            <Skeleton className="h-6 w-8 mx-auto mb-1" />
                            <Skeleton className="h-3 w-16 mx-auto" />
                          </div>
                          <div className="text-center">
                            <Skeleton className="h-6 w-8 mx-auto mb-1" />
                            <Skeleton className="h-3 w-16 mx-auto" />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {agentPerformance.map((agent) => {
                      const successRate = agent.metrics?.success_rate || 0;
                      return (
                        <div key={agent.agent_type} className="p-4 border rounded-lg bg-muted/20">
                          <div className="flex items-center justify-between mb-4">
                            <h3 className="font-semibold capitalize">
                              {agent.agent_type.replace('_', ' ')} Agent
                            </h3>
                            <Badge variant="outline" className="bg-green-500/10 text-green-400 border-green-500/20">
                              Active
                            </Badge>
                          </div>
                          
                          <div className="space-y-4">
                            <div className="flex justify-between items-center">
                              <span className="text-sm">Success Rate</span>
                              <span className="font-medium">{successRate.toFixed(1)}%</span>
                            </div>
                            <Progress value={successRate} className="h-2" />
                            
                            <div className="grid grid-cols-3 gap-4 text-center">
                              <div>
                                <div className="text-lg font-bold">{agent.metrics?.total_executions || 0}</div>
                                <div className="text-xs text-muted-foreground">Total</div>
                              </div>
                              <div>
                                <div className="text-lg font-bold text-green-400">{agent.metrics?.successful_executions || 0}</div>
                                <div className="text-xs text-muted-foreground">Success</div>
                              </div>
                              <div>
                                <div className="text-lg font-bold text-red-400">{agent.metrics?.failed_executions || 0}</div>
                                <div className="text-xs text-muted-foreground">Failed</div>
                              </div>
                            </div>
                            
                            <div className="text-center pt-2 border-t">
                              <div className="text-sm text-muted-foreground">Avg Response Time</div>
                              <div className="font-medium">{(agent.metrics?.average_execution_time_ms || 0).toFixed(0)}ms</div>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Log Search Tab */}
          <TabsContent value="search" className="space-y-6">
            {/* Search Filters */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Advanced Log Search</CardTitle>
                    <CardDescription>Search and filter through detailed audit logs</CardDescription>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Button variant="outline" size="sm" onClick={resetSearchFilters}>
                      <RotateCcw className="h-4 w-4 mr-2" />
                      Reset
                    </Button>
                    <Button variant="outline" size="sm" onClick={saveSearchPreset}>
                      <Save className="h-4 w-4 mr-2" />
                      Save Preset
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label>Agent Type</Label>
                    <Select value={searchFilters.agent_type || "all_agents"} onValueChange={(value) => setSearchFilters(prev => ({ ...prev, agent_type: value }))}>
                      <SelectTrigger>
                        <SelectValue placeholder="All Agents" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all_agents">All Agents</SelectItem>
                        <SelectItem value="validator">Validator Agent</SelectItem>
                        <SelectItem value="account_setup">Account Setup Agent</SelectItem>
                        <SelectItem value="scheduler">Scheduler Agent</SelectItem>
                        <SelectItem value="notifier">Notifier Agent</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="space-y-2">
                    <Label>Status</Label>
                    <Select value={searchFilters.status || "all_status"} onValueChange={(value) => setSearchFilters(prev => ({ ...prev, status: value }))}>
                      <SelectTrigger>
                        <SelectValue placeholder="All Status" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all_status">All Status</SelectItem>
                        <SelectItem value="success">Success</SelectItem>
                        <SelectItem value="failed">Failed</SelectItem>
                        <SelectItem value="warning">Warning</SelectItem>
                        <SelectItem value="info">Info</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="space-y-2">
                    <Label>Priority</Label>
                    <Select value={searchFilters.priority || "all_priorities"} onValueChange={(value) => setSearchFilters(prev => ({ ...prev, priority: value }))}>
                      <SelectTrigger>
                        <SelectValue placeholder="All Priorities" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all_priorities">All Priorities</SelectItem>
                        <SelectItem value="high">High</SelectItem>
                        <SelectItem value="medium">Medium</SelectItem>
                        <SelectItem value="low">Low</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label>Start Date</Label>
                    <Input
                      type="datetime-local"
                      value={searchFilters.start_date || ""}
                      onChange={(e) => setSearchFilters(prev => ({ ...prev, start_date: e.target.value }))}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label>End Date</Label>
                    <Input
                      type="datetime-local"
                      value={searchFilters.end_date || ""}
                      onChange={(e) => setSearchFilters(prev => ({ ...prev, end_date: e.target.value }))}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label>Search Term</Label>
                    <Input
                      placeholder="Search in logs..."
                      value={searchFilters.search_term || ""}
                      onChange={(e) => setSearchFilters(prev => ({ ...prev, search_term: e.target.value }))}
                    />
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <Button onClick={performLogSearch} disabled={isSearchLoading}>
                    {isSearchLoading ? (
                      <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    ) : (
                      <Search className="h-4 w-4 mr-2" />
                    )}
                    Search Logs
                  </Button>
                  <Button variant="outline" onClick={resetSearchFilters}>
                    <Filter className="h-4 w-4 mr-2" />
                    Clear
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Search Results */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Search Results</CardTitle>
                    <CardDescription>
                      {resultCount > 0 ? `Found ${resultCount} log entries` : 'No search performed yet'}
                    </CardDescription>
                  </div>
                  {searchResults.length > 0 && (
                    <Button variant="outline" size="sm" onClick={exportSearchResults}>
                      <Download className="h-4 w-4 mr-2" />
                      Export
                    </Button>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                {isSearchLoading ? (
                  <div className="space-y-4">
                    {Array.from({ length: 5 }).map((_, i) => (
                      <div key={i} className="border rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center space-x-2">
                            <Skeleton className="h-4 w-20" />
                            <Skeleton className="h-4 w-16" />
                          </div>
                          <Skeleton className="h-4 w-24" />
                        </div>
                        <Skeleton className="h-4 w-full mb-1" />
                        <Skeleton className="h-3 w-2/3" />
                      </div>
                    ))}
                  </div>
                ) : searchResults.length > 0 ? (
                  <div className="space-y-4">
                    {searchResults.map((log, index) => (
                      <div key={index} className="border rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center space-x-2">
                            <Badge variant="outline">{log.agent_type}</Badge>
                            <Badge variant={getStatusVariant(log.status)}>{log.status}</Badge>
                          </div>
                          <div className="text-sm text-muted-foreground">
                            {formatTime(log.created_at)}
                          </div>
                        </div>
                        <div className="space-y-1">
                          <p className="font-medium">{log.action}</p>
                          <p className="text-sm text-muted-foreground">
                            Workflow ID: {log.workflow_id}
                            {log.execution_time_ms && ` • Duration: ${log.execution_time_ms}ms`}
                          </p>
                          {log.error_message && (
                            <div className="text-sm text-red-400 bg-red-500/10 rounded p-2 mt-2">
                              <strong>Error:</strong> {log.error_message}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <Search className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                    <h3 className="text-lg font-medium mb-2">Ready to Search</h3>
                    <p className="text-muted-foreground">
                      Use the filters above to search through audit logs and find specific events or operations.
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Real-time Activity Tab */}
          <TabsContent value="activity" className="space-y-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Real-time Activity Feed</CardTitle>
                    <CardDescription>Live system events and operations</CardDescription>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Button variant="outline" size="sm" onClick={toggleActivityPause}>
                      {isActivityPaused ? (
                        <Play className="h-4 w-4 mr-2" />
                      ) : (
                        <Pause className="h-4 w-4 mr-2" />
                      )}
                      {isActivityPaused ? 'Resume' : 'Pause'}
                    </Button>
                    <Select defaultValue="all_events">
                      <SelectTrigger className="w-32">
                        <SelectValue placeholder="Filter" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all_events">All Events</SelectItem>
                        <SelectItem value="success">Success Only</SelectItem>
                        <SelectItem value="error">Errors Only</SelectItem>
                        <SelectItem value="warning">Warnings</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-center py-12">
                  <Activity className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-medium mb-2">Real-time Feed</h3>
                  <p className="text-muted-foreground">
                    {isActivityPaused 
                      ? "Activity feed is paused. Click Resume to start monitoring live events."
                      : "Monitoring live system events. New activities will appear here automatically."
                    }
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  );
}