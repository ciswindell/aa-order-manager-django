'use client';

import { ThemeToggle } from '@/components/theme-toggle';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useAuth } from '@/hooks/useAuth';
import { DashboardData, getDashboard } from '@/lib/api/dashboard';
import { connectBasecamp, connectDropbox } from '@/lib/api/integrations';
import { ExternalLink } from 'lucide-react';
import Link from 'next/link';
import { useEffect, useState } from 'react';
import { toast } from 'sonner';

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [connectingProvider, setConnectingProvider] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboard = async () => {
      const response = await getDashboard();
      if (response.data) {
        setDashboardData(response.data);
      }
      setLoading(false);
    };

    if (user) {
      fetchDashboard();
    }
  }, [user]);

  const handleIntegrationConnect = async (provider: string) => {
    setConnectingProvider(provider);
    try {
      const response =
        provider === 'dropbox' ? await connectDropbox() : await connectBasecamp();

      if (response.data?.authorize_url) {
        // Redirect to OAuth URL
        window.location.href = response.data.authorize_url;
      } else if (response.error) {
        toast.error('Connection Failed', {
          description: response.error,
        });
        setConnectingProvider(null);
      }
    } catch (error) {
      toast.error('Connection Failed', {
        description: 'An unexpected error occurred',
      });
      setConnectingProvider(null);
    }
  };

  if (!user || loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-muted-foreground">Loading...</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <ThemeToggle />
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {/* Welcome Card */}
        <Card>
          <CardHeader>
            <CardTitle>Welcome back, {user.username}!</CardTitle>
            <CardDescription>{user.email}</CardDescription>
          </CardHeader>
          <CardContent>
            {user.is_staff && (
              <p className="text-sm font-semibold text-primary">Staff Member</p>
            )}
          </CardContent>
        </Card>

        {/* Integration Status Cards */}
        {dashboardData?.integrations.map((integration) => (
          <Card key={integration.provider}>
            <CardHeader>
              <CardTitle className="capitalize">{integration.provider}</CardTitle>
              <CardDescription>
                {integration.is_connected && integration.is_authenticated ? (
                  <span className="text-green-600 dark:text-green-400">✓ Connected</span>
                ) : integration.blocking_problem ? (
                  <span className="text-red-600 dark:text-red-400">⚠ {integration.reason}</span>
                ) : (
                  <span className="text-muted-foreground">Not connected</span>
                )}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {integration.cta_label && (
                <Button
                  variant="outline"
                  size="sm"
                  className="w-full"
                  onClick={() => handleIntegrationConnect(integration.provider)}
                  disabled={connectingProvider === integration.provider}
                >
                  {connectingProvider === integration.provider
                    ? 'Connecting...'
                    : integration.cta_label}
                </Button>
              )}
            </CardContent>
          </Card>
        ))}

        {/* Quick Links Card */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Links</CardTitle>
            <CardDescription>Access key features</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            <Link href="/dashboard/orders">
              <Button variant="outline" size="sm" className="w-full">
                Manage Orders
              </Button>
            </Link>
            <Link href="/dashboard/reports">
              <Button variant="outline" size="sm" className="w-full">
                Manage Reports
              </Button>
            </Link>
            <Link href="/dashboard/leases">
              <Button variant="outline" size="sm" className="w-full">
                Manage Leases
              </Button>
            </Link>
            {user.is_staff && (
              <Link href="/dashboard/integrations">
                <Button variant="outline" size="sm" className="w-full">
                  Manage Integrations
                </Button>
              </Link>
            )}
          </CardContent>
        </Card>

        {/* Admin Actions Card (if staff) */}
        {user.is_staff && (
          <Card>
            <CardHeader>
              <CardTitle>Admin Actions</CardTitle>
              <CardDescription>Administrative tools and settings</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              <a
                href="http://localhost:8000/admin/"
                target="_blank"
                rel="noopener noreferrer"
                className="block"
              >
                <Button variant="outline" size="sm" className="w-full justify-between">
                  Django Admin
                  <ExternalLink className="h-4 w-4" />
                </Button>
              </a>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}

