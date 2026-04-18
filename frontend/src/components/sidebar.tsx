"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  MessageCircle,
  BarChart3,
  BookOpen,
  Brain,
  Settings,
  LogOut,
  Menu,
  X,
  Heart,
  Library,
  CalendarDays,
} from "lucide-react";
import { useAuth } from "@/context/auth";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

const navItems = [
  { href: "/chat", label: "Chat", icon: MessageCircle, description: "Talk with MindMate" },
  { href: "/dashboard", label: "Mood", icon: BarChart3, description: "Track your moods" },
  { href: "/journal", label: "Journal", icon: BookOpen, description: "Write & reflect" },
  { href: "/therapy", label: "Therapy", icon: Brain, description: "Session notes" },
  { href: "/summary", label: "Summary", icon: CalendarDays, description: "Weekly recap" },
  { href: "/knowledge", label: "Knowledge", icon: Library, description: "PDF library" },
  { href: "/settings", label: "Settings", icon: Settings, description: "Preferences" },
];

function NavContent({ pathname, email, logout, onNavigate }: {
  pathname: string;
  email: string;
  logout: () => void;
  onNavigate?: () => void;
}) {
  const initials = email.slice(0, 2).toUpperCase();

  return (
    <>
      <div className="mb-8 px-2">
        <div className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-primary/20 to-primary/5">
            <Heart className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h1 className="text-base font-semibold tracking-tight">MindMate</h1>
            <p className="text-[11px] text-muted-foreground leading-none">Mental Health Companion</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 space-y-1 px-1">
        {navItems.map(({ href, label, icon: Icon, description }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              onClick={onNavigate}
              className={`flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition-all ${
                active
                  ? "bg-primary text-primary-foreground shadow-sm"
                  : "text-muted-foreground hover:bg-accent hover:text-foreground"
              }`}
            >
              <Icon className="h-4 w-4 shrink-0" />
              <div className="min-w-0">
                <div className="font-medium">{label}</div>
                {!active && (
                  <div className="text-[11px] text-muted-foreground/70 truncate">{description}</div>
                )}
              </div>
            </Link>
          );
        })}
      </nav>

      <Separator className="my-4" />

      <div className="px-2 space-y-3">
        <div className="flex items-center gap-2.5">
          <Avatar className="h-8 w-8">
            <AvatarFallback className="text-xs bg-muted">{initials}</AvatarFallback>
          </Avatar>
          <p className="truncate text-xs text-muted-foreground flex-1">{email}</p>
        </div>
        <Button
          variant="ghost"
          size="sm"
          className="w-full justify-start gap-2 text-muted-foreground hover:text-destructive"
          onClick={logout}
        >
          <LogOut className="h-4 w-4" />
          Logout
        </Button>
      </div>
    </>
  );
}

export function Sidebar() {
  const pathname = usePathname();
  const { email, logout } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);

  if (!email) return null;

  return (
    <>
      {/* Mobile top bar */}
      <div className="md:hidden fixed top-0 left-0 right-0 z-40 flex items-center gap-3 border-b bg-background/95 backdrop-blur px-4 py-3">
        <Button variant="ghost" size="icon" onClick={() => setMobileOpen(true)}>
          <Menu className="h-5 w-5" />
        </Button>
        <div className="flex items-center gap-2">
          <Heart className="h-4 w-4 text-primary" />
          <span className="font-semibold text-sm">MindMate</span>
        </div>
      </div>

      {/* Mobile overlay */}
      {mobileOpen && (
        <div className="md:hidden fixed inset-0 z-50 flex">
          <div
            className="absolute inset-0 bg-black/40 backdrop-blur-sm"
            onClick={() => setMobileOpen(false)}
          />
          <aside className="relative z-10 flex w-72 flex-col bg-background p-4 shadow-xl">
            <div className="flex justify-end mb-2">
              <Button variant="ghost" size="icon" onClick={() => setMobileOpen(false)}>
                <X className="h-5 w-5" />
              </Button>
            </div>
            <NavContent
              pathname={pathname}
              email={email}
              logout={logout}
              onNavigate={() => setMobileOpen(false)}
            />
          </aside>
        </div>
      )}

      {/* Desktop sidebar */}
      <aside className="hidden md:flex w-60 flex-col border-r bg-muted/30 p-4">
        <NavContent pathname={pathname} email={email} logout={logout} />
      </aside>
    </>
  );
}
