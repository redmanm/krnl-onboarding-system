"use client";

import React, { useState, useEffect } from "react";
import { usePathname } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import {
  Sheet,
  SheetContent,
  SheetTrigger,
} from "@/components/ui/sheet";
import {
  Activity,
  Users,
  UserPlus,
  Database,
  ClipboardCheck,
  Heart,
  Search,
  Menu,
  Rocket,
  Upload,
  Building,
  Circle,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { checkAPIConnectivity } from "@/lib/api";

// Navigation items configuration
const navigationItems = [
  {
    name: "Dashboard",
    href: "/",
    icon: Activity,
    description: "Overview and metrics",
  },
  {
    name: "Employee Management",
    href: "/employee-management",
    icon: UserPlus,
    description: "Add and manage employees",
  },
  {
    name: "Employee List",
    href: "/employees",
    icon: Users,
    description: "View all employees",
  },
  {
    name: "Audit Logs",
    href: "/audit",
    icon: ClipboardCheck,
    description: "System logs and analytics",
  },
  {
    name: "System Health",
    href: "/system-health",
    icon: Heart,
    description: "System status monitoring",
  },
];

// System status component
function SystemStatus() {
  const [status, setStatus] = useState<"online" | "offline" | "checking">("checking");

  useEffect(() => {
    const checkStatus = async () => {
      try {
        await checkAPIConnectivity();
        setStatus("online");
      } catch {
        setStatus("offline");
      }
    };

    checkStatus();
    const interval = setInterval(checkStatus, 30000); // Check every 30 seconds

    return () => clearInterval(interval);
  }, []);

  const getStatusConfig = () => {
    switch (status) {
      case "online":
        return {
          color: "text-green-400",
          text: "System Online",
          bgColor: "bg-green-400",
        };
      case "offline":
        return {
          color: "text-red-400",
          text: "System Offline",
          bgColor: "bg-red-400",
        };
      default:
        return {
          color: "text-yellow-400",
          text: "Checking...",
          bgColor: "bg-yellow-400",
        };
    }
  };

  const statusConfig = getStatusConfig();

  return (
    <div className="flex items-center space-x-2">
      <Circle className={`h-2 w-2 ${statusConfig.bgColor} rounded-full`} />
      <span className={`text-sm ${statusConfig.color}`}>
        {statusConfig.text}
      </span>
    </div>
  );
}

// Header component
export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 max-w-screen-2xl items-center justify-between">
        {/* Mobile menu trigger */}
        <div className="flex items-center space-x-4">
          <Sheet>
            <SheetTrigger asChild>
              <Button variant="ghost" size="sm" className="lg:hidden">
                <Menu className="h-5 w-5" />
                <span className="sr-only">Toggle menu</span>
              </Button>
            </SheetTrigger>
            <SheetContent side="left" className="w-64">
              <Sidebar isMobile />
            </SheetContent>
          </Sheet>

          {/* Logo */}
          <Link href="/" className="flex items-center space-x-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 shadow-lg">
              {/* <Rocket className="h-5 w-5 text-white" /> */}
              <img src="/krnl.jpg" alt="Logo" className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 shadow-lg" />
            </div>
            <div className="hidden sm:block">
              <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                KRNL
              </h1>
              <p className="text-xs text-muted-foreground">Onboarding System</p>
            </div>
          </Link>
        </div>

        {/* Search and actions */}
        <div className="flex items-center space-x-4">
          {/* <div className="hidden md:flex relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search anything..."
              className="w-64 pl-10 bg-muted/30 border-muted"
            />
          </div> */}

          {/* <div className="hidden sm:flex items-center space-x-2">
            <Button variant="outline" size="sm">
              <Upload className="h-4 w-4 mr-2" />
              Upload
            </Button>
            <Button size="sm">
              <UserPlus className="h-4 w-4 mr-2" />
              Add Employee
            </Button>
          </div> */}

          <SystemStatus />
        </div>
      </div>
    </header>
  );
}

// Sidebar component
interface SidebarProps {
  isMobile?: boolean;
}

export function Sidebar({ isMobile = false }: SidebarProps) {
  const pathname = usePathname();

  return (
    <div className={cn(
      "flex flex-col h-full bg-background border-r border-border",
      !isMobile && "w-64"
    )}>
      {/* Workspace info */}
      <div className="p-6 border-b border-border">
        <div className="flex items-center space-x-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-muted">
            <Building className="h-5 w-5 text-muted-foreground" />
          </div>
          <div>
            <h3 className="text-sm font-medium">Main Workspace</h3>
            <p className="text-xs text-muted-foreground">KRNL Enterprise</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 p-4">
        {navigationItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "group flex items-center rounded-lg px-3 py-2 text-sm font-medium transition-all hover:bg-accent hover:text-accent-foreground",
                isActive
                  ? "bg-accent text-accent-foreground shadow-sm"
                  : "text-muted-foreground"
              )}
            >
              <item.icon className="mr-3 h-4 w-4" />
              <div className="flex-1">
                <div>{item.name}</div>
                <div className="text-xs text-muted-foreground group-hover:text-accent-foreground/70">
                  {item.description}
                </div>
              </div>
              {isActive && (
                <div className="ml-auto h-2 w-2 rounded-full bg-blue-500" />
              )}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-border">
        <div className="text-xs text-muted-foreground text-center">
          <p>KRNL Onboarding System</p>
          <p>v2.0.0 - Next.js Edition</p>
        </div>
      </div>
    </div>
  );
}

// Main layout wrapper
interface DashboardLayoutProps {
  children: React.ReactNode;
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <div className="flex">
        <aside className="hidden lg:block">
          <Sidebar />
        </aside>
        <main className="flex-1">
          {children}
        </main>
      </div>
    </div>
  );
}