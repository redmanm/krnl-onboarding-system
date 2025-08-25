// API Configuration and Utility Functions for KRNL Onboarding System

const API_BASE_URL = typeof window !== 'undefined' && 
  (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') 
  ? 'http://localhost:8000' 
  : 'http://localhost:8000'; // Change this for production

// Types
export interface Employee {
  id: string;
  name: string;
  email: string;
  role: string;
  department: string;
  start_date: string;
  status?: string;
  workflow_status?: string;
}

export interface DashboardStats {
  total_employees: number;
  pending_onboarding: number;
  completed_onboarding: number;
  failed_onboarding: number;
}

export interface RecentActivity {
  employee_name: string;
  employee_email: string;
  current_step: string;
  status: string;
  created_at: string;
}

export interface AgentMetrics {
  agent_type: string;
  metrics: {
    total_executions: number;
    successful_executions: number;
    failed_executions: number;
    success_rate: number;
    average_execution_time_ms: number;
  };
}

export interface SystemHealth {
  system_status: string;
  workflow_metrics: {
    total_workflows: number;
    completed_workflows: number;
    failed_workflows: number;
    success_rate: number;
  };
  agent_metrics: Record<string, any>;
  timestamp: string;
}

export interface LogEntry {
  id: string;
  agent_type: string;
  action: string;
  workflow_id: string;
  status: string;
  created_at: string;
  execution_time_ms?: number;
  error_message?: string;
}

export interface SearchFilters {
  agent_type?: string;
  status?: string;
  priority?: string;
  start_date?: string;
  end_date?: string;
  search_term?: string;
  limit?: number;
}

// Custom error class for API errors
export class APIError extends Error {
  constructor(
    message: string,
    public status?: number,
    public statusText?: string
  ) {
    super(message);
    this.name = 'APIError';
  }
}

// Main API call function with retry logic and error handling
export async function apiCall<T = any>(
  endpoint: string, 
  options: RequestInit = {}
): Promise<T> {
  const maxRetries = 3;
  let lastError: Error = new Error('Unknown error');
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
      
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          ...options.headers,
        },
        signal: controller.signal,
        ...options,
      });
      
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        throw new APIError(
          `HTTP ${response.status}: ${response.statusText}`,
          response.status,
          response.statusText
        );
      }
      
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      } else {
        throw new APIError('Server returned non-JSON response');
      }
      
    } catch (error) {
      lastError = error as Error;
      console.error(`API call attempt ${attempt} failed:`, error);
      
      if (error instanceof APIError) {
        throw error; // Don't retry on HTTP errors
      }
      
      if (error instanceof Error && error.name === 'AbortError') {
        throw new APIError('Request timeout - server may be down');
      }
      
      if (error instanceof TypeError && error.message.includes('fetch')) {
        lastError = new APIError('Network error - unable to connect to server');
      }
      
      // Don't retry on certain errors or if this is the last attempt
      if (error instanceof APIError || attempt === maxRetries) {
        break;
      }
      
      // Wait before retry (exponential backoff)
      await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt - 1) * 1000));
    }
  }
  
  throw lastError;
}

// API Functions

// Health check
export async function checkAPIConnectivity(): Promise<any> {
  return apiCall('/health');
}

// Dashboard APIs
export async function getDashboardStats(): Promise<DashboardStats> {
  return apiCall('/api/v1/dashboard/stats');
}

export async function getRecentActivity(limit?: number): Promise<{ recent_activity: RecentActivity[] }> {
  const params = limit ? `?limit=${limit}` : '';
  return apiCall(`/api/v1/dashboard/recent-activity${params}`);
}

// Employee APIs
export async function getEmployees(): Promise<Employee[]> {
  return apiCall('/api/v1/employees');
}

export async function getEmployeeDetails(employeeId: string): Promise<any> {
  return apiCall(`/api/v1/employees/${employeeId}`);
}

export async function createEmployee(employeeData: Omit<Employee, 'id'>): Promise<any> {
  return apiCall('/api/v1/employees', {
    method: 'POST',
    body: JSON.stringify(employeeData),
  });
}

export async function updateEmployee(employeeId: string, employeeData: Omit<Employee, 'id'>): Promise<any> {
  return apiCall(`/api/v1/employees/${employeeId}`, {
    method: 'PUT',
    body: JSON.stringify(employeeData),
  });
}

export async function deleteEmployee(employeeId: string): Promise<any> {
  return apiCall(`/api/v1/employees/${employeeId}`, {
    method: 'DELETE',
  });
}

export async function deleteAllEmployees(): Promise<any> {
  return apiCall('/api/v1/employees/all?confirm=true', {
    method: 'DELETE',
  });
}

export async function uploadEmployeeCSV(file: File): Promise<any> {
  const formData = new FormData();
  formData.append('file', file);
  
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 60000); // 60 second timeout for file upload
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/employees/upload-csv`, {
      method: 'POST',
      body: formData,
      headers: {
        'Accept': 'application/json',
        // Don't set Content-Type for FormData - browser will set it with boundary
      },
      signal: controller.signal,
    });
    
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      const errorText = await response.text();
      let errorMessage;
      try {
        const errorJson = JSON.parse(errorText);
        errorMessage = errorJson.detail || errorJson.message || `HTTP ${response.status}: ${response.statusText}`;
      } catch {
        errorMessage = `HTTP ${response.status}: ${response.statusText}`;
      }
      throw new APIError(errorMessage, response.status, response.statusText);
    }
    
    return await response.json();
  } catch (error) {
    clearTimeout(timeoutId);
    
    if (error instanceof Error && error.name === 'AbortError') {
      throw new APIError('Upload timeout - file may be too large or server is slow');
    } else if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new APIError('Network error - unable to connect to server');
    } else {
      throw error;
    }
  }
}

// Agent Performance APIs
export async function getAgentPerformance(agentType?: string): Promise<AgentMetrics[]> {
  if (agentType) {
    const result = await apiCall(`/api/v1/audit/agent-performance/${agentType}`);
    return [result];
  } else {
    const agents = ['validator', 'account_setup', 'scheduler', 'notifier'];
    const performanceData = await Promise.all(
      agents.map(agent => apiCall(`/api/v1/audit/agent-performance/${agent}`))
    );
    return performanceData;
  }
}

// System Health APIs
export async function getSystemHealth(): Promise<SystemHealth> {
  return apiCall('/api/v1/audit/system-health');
}

// Audit Log APIs
export async function searchLogs(filters: SearchFilters): Promise<{ logs: LogEntry[]; result_count: number }> {
  // Remove empty filters
  const cleanFilters = Object.fromEntries(
    Object.entries(filters).filter(([_, value]) => value !== '' && value !== undefined)
  );
  
  return apiCall('/api/v1/audit/search-logs', {
    method: 'POST',
    body: JSON.stringify(cleanFilters),
  });
}

// Utility functions for data formatting
export function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString();
}

export function formatTime(dateString: string): string {
  return new Date(dateString).toLocaleString();
}

export function getStatusClass(status: string): string {
  if (!status) return 'unknown';
  
  const statusLower = status.toLowerCase();
  if (statusLower.includes('completed') || statusLower === 'success') return 'completed';
  if (statusLower.includes('failed') || statusLower === 'failed') return 'failed';
  if (statusLower.includes('pending') || statusLower.includes('progress')) return 'pending';
  return 'unknown';
}

export function getSuccessRateClass(rate: number): string {
  if (rate >= 90) return 'high';
  if (rate >= 70) return 'medium';
  return 'low';
}

// Debounce utility for search inputs
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: any;
  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}