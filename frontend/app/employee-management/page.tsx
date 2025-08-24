"use client";

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Skeleton } from "@/components/ui/skeleton";
import {
  UserPlus,
  Upload,
  Download,
  Users,
  Clock,
  RefreshCw,
  CheckCircle,
  FileText,
  Calendar,
  Shield,
} from "lucide-react";
import { DashboardLayout } from "@/components/navigation";
import { useNotifications } from "@/lib/notifications";
import { useLoadingState } from "@/lib/loading";
import {
  getDashboardStats,
  getRecentActivity,
  createEmployee,
  uploadEmployeeCSV,
  formatTime,
  type DashboardStats,
  type RecentActivity,
  type Employee,
} from "@/lib/api";

// Employee form data interface
interface EmployeeFormData {
  name: string;
  email: string;
  role: string;
  department: string;
  start_date: string;
}

export default function EmployeeManagementPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([]);
  const [isAddEmployeeOpen, setIsAddEmployeeOpen] = useState(false);
  const [isBulkUploadOpen, setIsBulkUploadOpen] = useState(false);
  const [csvFile, setCsvFile] = useState<File | null>(null);
  const [csvPreview, setCsvPreview] = useState<string[][]>([]);
  const [employeeForm, setEmployeeForm] = useState<EmployeeFormData>({
    name: "",
    email: "",
    role: "",
    department: "",
    start_date: "",
  });

  const { showError, showSuccess, showWarning } = useNotifications();
  const [isStatsLoading, setStatsLoading] = useLoadingState("stats");
  const [isActivityLoading, setActivityLoading] = useLoadingState("activity");
  const [isSubmitting, setSubmitting] = useLoadingState("submit");
  const [isUploading, setUploading] = useLoadingState("upload");

  // Load dashboard stats
  const loadStats = async () => {
    try {
      setStatsLoading(true);
      const dashboardStats = await getDashboardStats();
      setStats(dashboardStats);
    } catch (error) {
      showError("Failed to load statistics");
      console.error("Stats error:", error);
    } finally {
      setStatsLoading(false);
    }
  };

  // Load recent activity
  const loadRecentActivity = async () => {
    try {
      setActivityLoading(true);
      const activityData = await getRecentActivity(10);
      setRecentActivity(activityData.recent_activity || []);
    } catch (error) {
      showError("Failed to load recent additions");
      console.error("Activity error:", error);
    } finally {
      setActivityLoading(false);
    }
  };

  useEffect(() => {
    loadStats();
    loadRecentActivity();
  }, []);

  // Handle employee form submission
  const handleAddEmployee = async () => {
    if (!employeeForm.name || !employeeForm.email || !employeeForm.role || !employeeForm.department || !employeeForm.start_date) {
      showWarning("Please fill in all required fields");
      return;
    }

    try {
      setSubmitting(true);
      await createEmployee(employeeForm);
      showSuccess(`Employee ${employeeForm.name} added successfully!`);
      setEmployeeForm({
        name: "",
        email: "",
        role: "",
        department: "",
        start_date: "",
      });
      setIsAddEmployeeOpen(false);
      loadStats();
      loadRecentActivity();
    } catch (error) {
      showError("Failed to add employee");
      console.error("Add employee error:", error);
    } finally {
      setSubmitting(false);
    }
  };

  // Handle CSV file selection and preview
  const handleCSVFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) {
      setCsvFile(null);
      setCsvPreview([]);
      return;
    }

    if (!file.name.endsWith('.csv')) {
      showError("Please select a CSV file");
      event.target.value = '';
      return;
    }

    setCsvFile(file);

    // Read and preview CSV
    const reader = new FileReader();
    reader.onload = (e) => {
      const csv = e.target?.result as string;
      const lines = csv.split('\n').slice(0, 6); // Header + 5 rows
      
      if (lines.length < 2) {
        showError("CSV file appears to be empty");
        return;
      }

      const headers = lines[0].split(',').map(h => h.trim());
      const requiredHeaders = ['name', 'email', 'role', 'department', 'start_date'];
      const hasAllHeaders = requiredHeaders.every(h => headers.includes(h));

      if (!hasAllHeaders) {
        showError(`CSV is missing required headers: ${requiredHeaders.join(', ')}`);
        return;
      }

      const previewData = lines.map(line => line.split(',').map(cell => cell.trim()));
      setCsvPreview(previewData);
    };

    reader.readAsText(file);
  };

  // Handle CSV upload
  const handleBulkUpload = async () => {
    if (!csvFile) {
      showWarning("Please select a CSV file");
      return;
    }

    try {
      setUploading(true);
      const result = await uploadEmployeeCSV(csvFile);
      showSuccess(`Bulk upload completed: ${result.successful} successful, ${result.failed} failed`);
      setIsBulkUploadOpen(false);
      setCsvFile(null);
      setCsvPreview([]);
      loadStats();
      loadRecentActivity();
    } catch (error) {
      showError("Bulk upload failed");
      console.error("Bulk upload error:", error);
    } finally {
      setUploading(false);
    }
  };

  // Download CSV template
  const downloadCSVTemplate = () => {
    const csvContent = `name,email,role,department,start_date
John Doe,john.doe@company.com,Software Engineer,Engineering,2024-01-15
Jane Smith,jane.smith@company.com,Product Manager,Product,2024-01-16`;
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    
    if (link.download !== undefined) {
      const url = URL.createObjectURL(blob);
      link.setAttribute('href', url);
      link.setAttribute('download', 'employee_template.csv');
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
    
    showSuccess('CSV template downloaded successfully');
  };

  const roles = [
    "Software Engineer",
    "Product Manager",
    "Designer",
    "QA Engineer", 
    "DevOps Engineer",
    "Data Scientist",
    "Marketing Manager",
    "Sales Representative",
    "HR Specialist",
    "Finance Analyst"
  ];

  const departments = [
    "Engineering",
    "Product", 
    "Design",
    "QA",
    "DevOps",
    "Data Science",
    "Marketing",
    "Sales",
    "HR",
    "Finance"
  ];

  return (
    <DashboardLayout>
      <div className="p-6 space-y-6 max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Employee Management</h1>
            <p className="text-muted-foreground">
              Add new employees individually or in bulk to streamline your onboarding process
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <div className="flex flex-col sm:flex-row gap-2">
              <div className="text-center">
                <div className="text-2xl font-bold">{stats?.total_employees || 0}</div>
                <div className="text-xs text-muted-foreground">Total Employees</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-yellow-400">{stats?.pending_onboarding || 0}</div>
                <div className="text-xs text-muted-foreground">Pending</div>
              </div>
            </div>
          </div>
        </div>

        {/* Management Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Add Single Employee Card */}
          <Card className="relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-purple-500/10" />
            <CardHeader className="relative">
              <div className="flex items-center space-x-3">
                <div className="p-2 rounded-lg bg-blue-500/20">
                  <UserPlus className="h-6 w-6 text-blue-400" />
                </div>
                <div>
                  <CardTitle>Add Single Employee</CardTitle>
                  <CardDescription>Add one employee at a time with detailed information</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="relative space-y-4">
              <div className="space-y-2">
                <div className="flex items-center text-sm">
                  <CheckCircle className="h-4 w-4 text-green-400 mr-2" />
                  Real-time validation
                </div>
                <div className="flex items-center text-sm">
                  <CheckCircle className="h-4 w-4 text-green-400 mr-2" />
                  Instant workflow trigger
                </div>
                <div className="flex items-center text-sm">
                  <CheckCircle className="h-4 w-4 text-green-400 mr-2" />
                  Complete audit trail
                </div>
              </div>
              <Dialog open={isAddEmployeeOpen} onOpenChange={setIsAddEmployeeOpen}>
                <DialogTrigger asChild>
                  <Button className="w-full">
                    <UserPlus className="h-4 w-4 mr-2" />
                    Add New Employee
                  </Button>
                </DialogTrigger>
                <DialogContent className="sm:max-w-[425px]">
                  <DialogHeader>
                    <DialogTitle>Add New Employee</DialogTitle>
                    <DialogDescription>
                      Enter the employee details to start the onboarding process.
                    </DialogDescription>
                  </DialogHeader>
                  <div className="grid gap-4 py-4">
                    <div className="grid grid-cols-4 items-center gap-4">
                      <Label htmlFor="name" className="text-right">Name</Label>
                      <Input
                        id="name"
                        value={employeeForm.name}
                        onChange={(e) => setEmployeeForm(prev => ({ ...prev, name: e.target.value }))}
                        className="col-span-3"
                        placeholder="Full Name"
                      />
                    </div>
                    <div className="grid grid-cols-4 items-center gap-4">
                      <Label htmlFor="email" className="text-right">Email</Label>
                      <Input
                        id="email"
                        type="email"
                        value={employeeForm.email}
                        onChange={(e) => setEmployeeForm(prev => ({ ...prev, email: e.target.value }))}
                        className="col-span-3"
                        placeholder="email@company.com"
                      />
                    </div>
                    <div className="grid grid-cols-4 items-center gap-4">
                      <Label htmlFor="role" className="text-right">Role</Label>
                      <Select value={employeeForm.role} onValueChange={(value) => setEmployeeForm(prev => ({ ...prev, role: value }))}>
                        <SelectTrigger className="col-span-3">
                          <SelectValue placeholder="Select Role" />
                        </SelectTrigger>
                        <SelectContent>
                          {roles.map((role) => (
                            <SelectItem key={role} value={role}>
                              {role}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="grid grid-cols-4 items-center gap-4">
                      <Label htmlFor="department" className="text-right">Department</Label>
                      <Select value={employeeForm.department} onValueChange={(value) => setEmployeeForm(prev => ({ ...prev, department: value }))}>
                        <SelectTrigger className="col-span-3">
                          <SelectValue placeholder="Select Department" />
                        </SelectTrigger>
                        <SelectContent>
                          {departments.map((dept) => (
                            <SelectItem key={dept} value={dept}>
                              {dept}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="grid grid-cols-4 items-center gap-4">
                      <Label htmlFor="start_date" className="text-right">Start Date</Label>
                      <Input
                        id="start_date"
                        type="date"
                        value={employeeForm.start_date}
                        onChange={(e) => setEmployeeForm(prev => ({ ...prev, start_date: e.target.value }))}
                        className="col-span-3"
                      />
                    </div>
                  </div>
                  <DialogFooter>
                    <Button variant="outline" onClick={() => setIsAddEmployeeOpen(false)}>
                      Cancel
                    </Button>
                    <Button onClick={handleAddEmployee} disabled={isSubmitting}>
                      {isSubmitting && <RefreshCw className="h-4 w-4 mr-2 animate-spin" />}
                      Add Employee
                    </Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            </CardContent>
          </Card>

          {/* Bulk Upload Card */}
          <Card className="relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-green-500/10 to-emerald-500/10" />
            <CardHeader className="relative">
              <div className="flex items-center space-x-3">
                <div className="p-2 rounded-lg bg-green-500/20">
                  <Upload className="h-6 w-6 text-green-400" />
                </div>
                <div>
                  <CardTitle>Bulk Upload</CardTitle>
                  <CardDescription>Upload multiple employees using CSV files</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="relative space-y-4">
              <div className="space-y-2">
                <div className="flex items-center text-sm">
                  <CheckCircle className="h-4 w-4 text-green-400 mr-2" />
                  CSV format support
                </div>
                <div className="flex items-center text-sm">
                  <CheckCircle className="h-4 w-4 text-green-400 mr-2" />
                  Batch processing
                </div>
                <div className="flex items-center text-sm">
                  <CheckCircle className="h-4 w-4 text-green-400 mr-2" />
                  Error reporting
                </div>
              </div>
              <Dialog open={isBulkUploadOpen} onOpenChange={setIsBulkUploadOpen}>
                <DialogTrigger asChild>
                  <Button variant="outline" className="w-full">
                    <Upload className="h-4 w-4 mr-2" />
                    Upload CSV File
                  </Button>
                </DialogTrigger>
                <DialogContent className="sm:max-w-[600px]">
                  <DialogHeader>
                    <DialogTitle>Bulk Employee Upload</DialogTitle>
                    <DialogDescription>
                      Upload a CSV file to add multiple employees at once.
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="csv-file">Choose CSV File</Label>
                      <Input
                        id="csv-file"
                        type="file"
                        accept=".csv"
                        onChange={handleCSVFileSelect}
                      />
                    </div>
                    
                    {csvPreview.length > 0 && (
                      <div className="space-y-2">
                        <Label>Preview (first 5 rows):</Label>
                        <div className="border rounded-lg p-4 max-h-64 overflow-auto">
                          <table className="w-full text-sm">
                            <thead>
                              <tr className="border-b">
                                {csvPreview[0]?.map((header, index) => (
                                  <th key={index} className="text-left p-2 font-medium">
                                    {header}
                                  </th>
                                ))}
                              </tr>
                            </thead>
                            <tbody>
                              {csvPreview.slice(1).map((row, rowIndex) => (
                                <tr key={rowIndex} className="border-b">
                                  {row.map((cell, cellIndex) => (
                                    <td key={cellIndex} className="p-2">
                                      {cell}
                                    </td>
                                  ))}
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    )}
                  </div>
                  <DialogFooter>
                    <Button variant="outline" onClick={() => setIsBulkUploadOpen(false)}>
                      Cancel
                    </Button>
                    <Button onClick={handleBulkUpload} disabled={!csvFile || isUploading}>
                      {isUploading && <RefreshCw className="h-4 w-4 mr-2 animate-spin" />}
                      Upload
                    </Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            </CardContent>
          </Card>
        </div>

        {/* Recent Additions */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Recent Additions</CardTitle>
                <CardDescription>Last 10 employees added to the system</CardDescription>
              </div>
              <Button variant="outline" size="sm" onClick={loadRecentActivity}>
                <RefreshCw className={`h-4 w-4 mr-2 ${isActivityLoading ? "animate-spin" : ""}`} />
                Refresh
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {isActivityLoading ? (
              <div className="space-y-4">
                {Array.from({ length: 5 }).map((_, i) => (
                  <div key={i} className="flex items-center space-x-4">
                    <Skeleton className="h-10 w-10 rounded-full" />
                    <div className="flex-1">
                      <Skeleton className="h-4 w-32 mb-1" />
                      <Skeleton className="h-3 w-48" />
                    </div>
                    <Skeleton className="h-6 w-20" />
                    <Skeleton className="h-3 w-16" />
                  </div>
                ))}
              </div>
            ) : recentActivity.length > 0 ? (
              <div className="space-y-4">
                {recentActivity.map((activity, index) => (
                  <div key={index} className="flex items-center space-x-4 p-3 rounded-lg border">
                    <div className="h-10 w-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center">
                      <Users className="h-5 w-5 text-white" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium">{activity.employee_name}</p>
                      <p className="text-xs text-muted-foreground truncate">
                        {activity.employee_email} • {activity.current_step}
                      </p>
                    </div>
                    <Badge variant="outline">{activity.status}</Badge>
                    <div className="text-xs text-muted-foreground">
                      {formatTime(activity.created_at).split(' ')[1]}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <Users className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                <p className="text-sm text-muted-foreground">No recent additions found</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Upload Guidelines */}
        <Card>
          <CardHeader>
            <CardTitle>Upload Guidelines</CardTitle>
            <CardDescription>Important information for CSV uploads</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <FileText className="h-5 w-5 text-blue-400" />
                  <h4 className="font-medium">CSV Format</h4>
                </div>
                <p className="text-sm text-muted-foreground">
                  Use comma-separated values with headers: name, email, role, department, start_date
                </p>
              </div>
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <Calendar className="h-5 w-5 text-green-400" />
                  <h4 className="font-medium">Date Format</h4>
                </div>
                <p className="text-sm text-muted-foreground">
                  Use YYYY-MM-DD format for start dates (e.g., 2024-01-15)
                </p>
              </div>
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <Shield className="h-5 w-5 text-purple-400" />
                  <h4 className="font-medium">Data Validation</h4>
                </div>
                <p className="text-sm text-muted-foreground">
                  All entries are automatically validated for completeness and accuracy
                </p>
              </div>
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <Download className="h-5 w-5 text-orange-400" />
                  <h4 className="font-medium">Sample Template</h4>
                </div>
                <Button
                  variant="link"
                  className="p-0 h-auto text-sm text-orange-400 hover:text-orange-300"
                  onClick={downloadCSVTemplate}
                >
                  <Download className="h-3 w-3 mr-1" />
                  Download CSV template
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}