"use client";

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Users,
  Search,
  Filter,
  Eye,
  Edit,
  MoreVertical,
  RefreshCw,
  CheckCircle,
  Clock,
  AlertCircle,
  User,
} from "lucide-react";
import { DashboardLayout } from "@/components/navigation";
import { useNotifications } from "@/lib/notifications";
import { useLoadingState } from "@/lib/loading";
import {
  getEmployees,
  getEmployeeDetails,
  formatDate,
  formatTime,
  getStatusClass,
  debounce,
  type Employee,
} from "@/lib/api";

// Employee details interface
interface EmployeeDetails {
  employee: Employee;
  workflows: any[];
  summary: {
    completed_workflows: number;
    failed_workflows: number;
  };
}

export default function EmployeesPage() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [filteredEmployees, setFilteredEmployees] = useState<Employee[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedEmployee, setSelectedEmployee] = useState<EmployeeDetails | null>(null);
  const [isDetailsOpen, setIsDetailsOpen] = useState(false);

  const { showError, showSuccess } = useNotifications();
  const [isLoading, setLoading] = useLoadingState("employees");
  const [isDetailsLoading, setDetailsLoading] = useLoadingState("employee-details");

  // Load employees
  const loadEmployees = async () => {
    try {
      setLoading(true);
      const employeeData = await getEmployees();
      setEmployees(employeeData);
      setFilteredEmployees(employeeData);
    } catch (error) {
      showError("Failed to load employees");
      console.error("Load employees error:", error);
    } finally {
      setLoading(false);
    }
  };

  // Load employee details
  const loadEmployeeDetails = async (employeeId: string) => {
    try {
      setDetailsLoading(true);
      const details = await getEmployeeDetails(employeeId);
      setSelectedEmployee(details);
      setIsDetailsOpen(true);
    } catch (error) {
      showError("Failed to load employee details");
      console.error("Load employee details error:", error);
    } finally {
      setDetailsLoading(false);
    }
  };

  // Filter employees based on search term
  const debouncedFilter = debounce((term: string) => {
    if (!term) {
      setFilteredEmployees(employees);
      return;
    }

    const filtered = employees.filter(emp =>
      emp.name.toLowerCase().includes(term.toLowerCase()) ||
      emp.email.toLowerCase().includes(term.toLowerCase()) ||
      emp.role.toLowerCase().includes(term.toLowerCase()) ||
      emp.department.toLowerCase().includes(term.toLowerCase())
    );
    setFilteredEmployees(filtered);
  }, 300);

  useEffect(() => {
    loadEmployees();
  }, []);

  useEffect(() => {
    debouncedFilter(searchTerm);
  }, [searchTerm, employees]);

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

  // Get status icon
  const getStatusIcon = (status: string) => {
    const statusClass = getStatusClass(status);
    switch (statusClass) {
      case "completed":
        return <CheckCircle className="h-4 w-4 text-green-400" />;
      case "pending":
        return <Clock className="h-4 w-4 text-yellow-400" />;
      case "failed":
        return <AlertCircle className="h-4 w-4 text-red-400" />;
      default:
        return <User className="h-4 w-4 text-gray-400" />;
    }
  };

  // Calculate workflow progress
  const calculateProgress = (employee: Employee) => {
    // This would normally come from the employee data
    // For now, we'll use status to determine progress
    const status = employee.workflow_status || employee.status;
    if (!status) return 0;
    
    const statusClass = getStatusClass(status);
    switch (statusClass) {
      case "completed":
        return 100;
      case "pending":
        return Math.floor(Math.random() * 50) + 25; // Random between 25-75
      case "failed":
        return Math.floor(Math.random() * 30) + 10; // Random between 10-40
      default:
        return 0;
    }
  };

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6 max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Employee List</h1>
            <p className="text-muted-foreground">
              View and manage employee onboarding status
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <Button variant="outline" onClick={loadEmployees} disabled={isLoading}>
              <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? "animate-spin" : ""}`} />
              Refresh
            </Button>
          </div>
        </div>

        {/* Search and Filters */}
        <Card>
          <CardHeader>
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <CardTitle>Employee Directory</CardTitle>
                <CardDescription>
                  {filteredEmployees.length} of {employees.length} employees
                </CardDescription>
              </div>
              <div className="flex items-center space-x-2">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    placeholder="Search employees..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 w-64"
                  />
                </div>
                <Button variant="outline" size="sm">
                  <Filter className="h-4 w-4 mr-2" />
                  Filter
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="space-y-4">
                {Array.from({ length: 5 }).map((_, i) => (
                  <div key={i} className="flex items-center space-x-4 p-4 border rounded-lg">
                    <Skeleton className="h-10 w-10 rounded-full" />
                    <div className="flex-1">
                      <Skeleton className="h-4 w-32 mb-2" />
                      <Skeleton className="h-3 w-48" />
                    </div>
                    <Skeleton className="h-4 w-20" />
                    <Skeleton className="h-6 w-16" />
                    <Skeleton className="h-8 w-20" />
                  </div>
                ))}
              </div>
            ) : filteredEmployees.length > 0 ? (
              <div className="rounded-lg border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Employee</TableHead>
                      <TableHead>Role</TableHead>
                      <TableHead>Department</TableHead>
                      <TableHead>Start Date</TableHead>
                      <TableHead>Progress</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredEmployees.map((employee) => {
                      const progress = calculateProgress(employee);
                      const status = employee.workflow_status || employee.status || "unknown";
                      
                      return (
                        <TableRow key={employee.id} className="hover:bg-muted/50">
                          <TableCell>
                            <div className="flex items-center space-x-3">
                              <div className="h-10 w-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center">
                                <span className="text-sm font-medium text-white">
                                  {employee.name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)}
                                </span>
                              </div>
                              <div>
                                <div className="font-medium">{employee.name}</div>
                                <div className="text-sm text-muted-foreground truncate max-w-[200px]">
                                  {employee.email}
                                </div>
                              </div>
                            </div>
                          </TableCell>
                          <TableCell className="font-medium">{employee.role}</TableCell>
                          <TableCell>{employee.department}</TableCell>
                          <TableCell>{formatDate(employee.start_date)}</TableCell>
                          <TableCell>
                            <div className="flex items-center space-x-2">
                              <Progress value={progress} className="w-16 h-2" />
                              <span className="text-sm text-muted-foreground whitespace-nowrap">
                                {progress}%
                              </span>
                            </div>
                          </TableCell>
                          <TableCell>
                            <Badge variant={getStatusVariant(status)} className="flex items-center space-x-1">
                              {getStatusIcon(status)}
                              <span className="capitalize">{status}</span>
                            </Badge>
                          </TableCell>
                          <TableCell className="text-right">
                            <DropdownMenu>
                              <DropdownMenuTrigger asChild>
                                <Button variant="ghost" size="sm">
                                  <MoreVertical className="h-4 w-4" />
                                </Button>
                              </DropdownMenuTrigger>
                              <DropdownMenuContent align="end">
                                <DropdownMenuItem 
                                  onClick={() => loadEmployeeDetails(employee.id)}
                                  disabled={isDetailsLoading}
                                >
                                  <Eye className="h-4 w-4 mr-2" />
                                  View Details
                                </DropdownMenuItem>
                                <DropdownMenuItem>
                                  <Edit className="h-4 w-4 mr-2" />
                                  Edit Employee
                                </DropdownMenuItem>
                                <DropdownMenuSeparator />
                                <DropdownMenuItem className="text-red-400">
                                  <AlertCircle className="h-4 w-4 mr-2" />
                                  Remove Employee
                                </DropdownMenuItem>
                              </DropdownMenuContent>
                            </DropdownMenu>
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </div>
            ) : (
              <div className="text-center py-12">
                <Users className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">No employees found</h3>
                <p className="text-muted-foreground">
                  {searchTerm
                    ? `No employees match "${searchTerm}". Try adjusting your search.`
                    : "No employees have been added yet. Add your first employee to get started."
                  }
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Employee Details Modal */}
        <Dialog open={isDetailsOpen} onOpenChange={setIsDetailsOpen}>
          <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Employee Onboarding Details</DialogTitle>
              <DialogDescription>
                Detailed information about the employee's onboarding progress
              </DialogDescription>
            </DialogHeader>
            
            {isDetailsLoading ? (
              <div className="space-y-6 py-6">
                <div className="flex items-center space-x-4">
                  <Skeleton className="h-16 w-16 rounded-full" />
                  <div className="space-y-2">
                    <Skeleton className="h-6 w-48" />
                    <Skeleton className="h-4 w-64" />
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <Skeleton className="h-6 w-32" />
                    <Skeleton className="h-20 w-full" />
                  </div>
                  <div className="space-y-4">
                    <Skeleton className="h-6 w-32" />
                    <Skeleton className="h-20 w-full" />
                  </div>
                </div>
              </div>
            ) : selectedEmployee ? (
              <div className="space-y-6 py-6">
                {/* Employee Summary */}
                <div className="flex items-center space-x-4 p-4 bg-muted/50 rounded-lg">
                  <div className="h-16 w-16 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center">
                    <span className="text-lg font-bold text-white">
                      {selectedEmployee.employee.name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)}
                    </span>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl font-semibold">{selectedEmployee.employee.name}</h3>
                    <p className="text-muted-foreground">{selectedEmployee.employee.email}</p>
                    <div className="flex items-center space-x-4 mt-2">
                      <Badge variant="outline">{selectedEmployee.employee.role}</Badge>
                      <Badge variant="outline">{selectedEmployee.employee.department}</Badge>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-muted-foreground">Start Date</p>
                    <p className="font-medium">{formatDate(selectedEmployee.employee.start_date)}</p>
                  </div>
                </div>

                {/* Workflow Summary */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Workflow Summary</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="flex justify-between">
                        <span>Total Workflows:</span>
                        <span className="font-medium">{selectedEmployee.workflows?.length || 0}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Completed:</span>
                        <span className="font-medium text-green-400">
                          {selectedEmployee.summary?.completed_workflows || 0}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>Failed:</span>
                        <span className="font-medium text-red-400">
                          {selectedEmployee.summary?.failed_workflows || 0}
                        </span>
                      </div>
                      <div className="pt-2">
                        <Progress 
                          value={
                            selectedEmployee.workflows?.length > 0 
                              ? ((selectedEmployee.summary?.completed_workflows || 0) / selectedEmployee.workflows.length) * 100
                              : 0
                          } 
                          className="h-2"
                        />
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Current Status</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="flex items-center space-x-2">
                        {getStatusIcon(selectedEmployee.employee.workflow_status || selectedEmployee.employee.status || "unknown")}
                        <Badge variant={getStatusVariant(selectedEmployee.employee.workflow_status || selectedEmployee.employee.status || "unknown")}>
                          {selectedEmployee.employee.workflow_status || selectedEmployee.employee.status || "Unknown"}
                        </Badge>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">Last Activity</p>
                        <p className="font-medium">
                          {selectedEmployee.workflows?.length > 0 
                            ? formatTime(selectedEmployee.workflows[0]?.workflow?.created_at || "")
                            : "No activity recorded"
                          }
                        </p>
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Workflow Timeline */}
                {selectedEmployee.workflows && selectedEmployee.workflows.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Workflow Timeline</CardTitle>
                      <CardDescription>Detailed progression through onboarding steps</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {selectedEmployee.workflows.map((workflow, index) => (
                          <div key={index} className="border rounded-lg p-4">
                            <div className="flex items-center justify-between mb-3">
                              <h4 className="font-medium">
                                Workflow {workflow.workflow?.id?.slice(0, 8) || `#${index + 1}`}
                              </h4>
                              <Badge variant={getStatusVariant(workflow.workflow?.status || "unknown")}>
                                {workflow.workflow?.status || "Unknown"}
                              </Badge>
                            </div>
                            
                            {workflow.metrics && (
                              <div className="grid grid-cols-3 gap-4 text-sm mb-3">
                                <div>
                                  <span className="text-muted-foreground">Total Steps:</span>
                                  <div className="font-medium">{workflow.metrics.total_steps || 0}</div>
                                </div>
                                <div>
                                  <span className="text-muted-foreground">Success Rate:</span>
                                  <div className="font-medium">
                                    {workflow.metrics.total_steps > 0 
                                      ? ((workflow.metrics.successful_steps / workflow.metrics.total_steps) * 100).toFixed(1)
                                      : 0
                                    }%
                                  </div>
                                </div>
                                <div>
                                  <span className="text-muted-foreground">Duration:</span>
                                  <div className="font-medium">{workflow.metrics.total_execution_time_ms || 0}ms</div>
                                </div>
                              </div>
                            )}

                            {workflow.timeline && workflow.timeline.length > 0 && (
                              <div className="space-y-2">
                                <h5 className="text-sm font-medium text-muted-foreground">Timeline Steps:</h5>
                                {workflow.timeline.slice(0, 5).map((step: any, stepIndex: number) => (
                                  <div key={stepIndex} className="flex items-center space-x-3 text-sm">
                                    <div className={`h-2 w-2 rounded-full ${
                                      step.status === 'completed' ? 'bg-green-400' :
                                      step.status === 'failed' ? 'bg-red-400' : 'bg-yellow-400'
                                    }`} />
                                    <span className="font-medium">{step.agent_type}</span>
                                    <span className="text-muted-foreground">•</span>
                                    <span>{step.action}</span>
                                    <span className="text-muted-foreground">•</span>
                                    <span className="text-xs">{step.execution_time_ms || 0}ms</span>
                                  </div>
                                ))}
                                {workflow.timeline.length > 5 && (
                                  <div className="text-xs text-muted-foreground">
                                    ... and {workflow.timeline.length - 5} more steps
                                  </div>
                                )}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            ) : null}
          </DialogContent>
        </Dialog>
      </div>
    </DashboardLayout>
  );
}