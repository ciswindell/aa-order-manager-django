'use client';

import { Button } from '@/components/ui/button';
import { useAuth } from '@/hooks/useAuth';
import { cn } from '@/lib/utils';
import {
    FileText,
    FolderOpen,
    Home,
    LayoutDashboard,
    LogOut,
    Settings,
} from 'lucide-react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

interface NavLinkProps {
  href: string;
  icon: React.ReactNode;
  label: string;
  isActive: boolean;
}

function NavLink({ href, icon, label, isActive }: NavLinkProps) {
  return (
    <Link href={href}>
      <Button
        variant={isActive ? 'default' : 'ghost'}
        className={cn('w-full justify-start', isActive && 'bg-primary text-primary-foreground')}
      >
        {icon}
        <span className="ml-2">{label}</span>
      </Button>
    </Link>
  );
}

export function Navigation() {
  const { user, logout } = useAuth();
  const pathname = usePathname();

  if (!user) {
    return null;
  }

  const navLinks = [
    {
      href: '/dashboard',
      icon: <Home className="h-4 w-4" />,
      label: 'Dashboard',
      exact: true,
    },
    {
      href: '/dashboard/orders',
      icon: <FolderOpen className="h-4 w-4" />,
      label: 'Orders',
    },
    {
      href: '/dashboard/reports',
      icon: <FileText className="h-4 w-4" />,
      label: 'Reports',
    },
    {
      href: '/dashboard/leases',
      icon: <LayoutDashboard className="h-4 w-4" />,
      label: 'Leases',
    },
  ];

  const adminLinks = user.is_staff
    ? [
        {
          href: '/dashboard/integrations',
          icon: <Settings className="h-4 w-4" />,
          label: 'Integrations',
        },
      ]
    : [];

  const isLinkActive = (href: string, exact?: boolean) => {
    if (exact) {
      return pathname === href;
    }
    return pathname.startsWith(href);
  };

  return (
    <nav className="flex flex-col gap-2 p-4 border-r bg-card min-h-screen w-64">
      <div className="mb-4 px-2">
        <h2 className="text-lg font-semibold">Order Manager</h2>
        <p className="text-sm text-muted-foreground">{user.username}</p>
      </div>

      <div className="flex flex-col gap-1">
        {navLinks.map((link) => (
          <NavLink
            key={link.href}
            href={link.href}
            icon={link.icon}
            label={link.label}
            isActive={isLinkActive(link.href, link.exact)}
          />
        ))}

        {adminLinks.length > 0 && (
          <>
            <div className="my-2 border-t" />
            <p className="px-2 text-xs font-semibold text-muted-foreground uppercase">Admin</p>
            {adminLinks.map((link) => (
              <NavLink
                key={link.href}
                href={link.href}
                icon={link.icon}
                label={link.label}
                isActive={isLinkActive(link.href)}
              />
            ))}
          </>
        )}
      </div>

      <div className="mt-auto pt-4 border-t">
        <Button variant="ghost" className="w-full justify-start" onClick={logout}>
          <LogOut className="h-4 w-4" />
          <span className="ml-2">Logout</span>
        </Button>
      </div>
    </nav>
  );
}

