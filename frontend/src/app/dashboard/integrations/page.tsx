'use client';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from '@/components/ui/dialog';
import { useAuth } from '@/hooks/useAuth';
import {
    connectBasecamp,
    connectDropbox,
    disconnectBasecamp,
    disconnectDropbox,
    getIntegrationStatus,
} from '@/lib/api/integrations';
import { IntegrationStatus } from '@/lib/api/types';
import { format } from 'date-fns';
import { ArrowLeft, CheckCircle2, XCircle } from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { toast } from 'sonner';

export default function IntegrationsPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [integrations, setIntegrations] = useState<IntegrationStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [disconnectDialogOpen, setDisconnectDialogOpen] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    const fetchIntegrations = async () => {
      const response = await getIntegrationStatus();
      if (response.data) {
        setIntegrations(response.data);
      }
      setLoading(false);
    };

    if (user) {
      fetchIntegrations();
    }
  }, [user]);

  const handleConnect = async (provider: string) => {
    setActionLoading(true);
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
      }
    } catch (error) {
      toast.error('Connection Failed', {
        description: 'An unexpected error occurred',
      });
    } finally {
      setActionLoading(false);
    }
  };

  const handleDisconnectClick = (provider: string) => {
    setSelectedProvider(provider);
    setDisconnectDialogOpen(true);
  };

  const handleDisconnectConfirm = async () => {
    if (!selectedProvider) return;

    setActionLoading(true);
    try {
      const response = selectedProvider === 'basecamp' 
        ? await disconnectBasecamp()
        : await disconnectDropbox();
      
      if (response.data) {
        toast.success('Disconnected', {
          description: response.data.message || 'Successfully disconnected',
          duration: 5000,
        });
        // Refresh integrations
        const refreshResponse = await getIntegrationStatus();
        if (refreshResponse.data) {
          setIntegrations(refreshResponse.data);
        }
      } else if (response.error) {
        toast.error('Disconnection Failed', {
          description: response.error,
        });
      }
    } catch (error) {
      toast.error('Disconnection Failed', {
        description: 'An unexpected error occurred',
      });
    } finally {
      setActionLoading(false);
      setDisconnectDialogOpen(false);
      setSelectedProvider(null);
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
      <div className="mb-6">
        <Link href="/dashboard">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Dashboard
          </Button>
        </Link>
      </div>

      <div className="mb-6">
        <h1 className="text-3xl font-bold">Integrations</h1>
        <p className="text-muted-foreground">Manage your external integrations</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {integrations.map((integration) => {
          const isConnected = integration.is_connected && integration.is_authenticated;
          const isDropbox = integration.provider === 'dropbox';
          const isBasecamp = integration.provider === 'basecamp';

          return (
            <Card key={integration.provider}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="capitalize">{integration.provider}</CardTitle>
                  {isConnected ? (
                    <Badge variant="default" className="bg-green-600">
                      <CheckCircle2 className="mr-1 h-3 w-3" />
                      Connected
                    </Badge>
                  ) : (
                    <Badge variant="destructive">
                      <XCircle className="mr-1 h-3 w-3" />
                      Not Connected
                    </Badge>
                  )}
                </div>
                <CardDescription>
                  {isConnected ? (
                    <div className="space-y-1">
                      {/* T012-T014, T033-T035: Display account info with truncation */}
                      {integration.account_name ? (
                        <div 
                          className="font-medium truncate max-w-[250px]" 
                          title={
                            isDropbox && integration.account_email
                              ? `${integration.account_name} (${integration.account_email})`
                              : integration.account_name
                          }
                        >
                          Connected as: {(() => {
                            // T033: Format Dropbox as "Name (email)"
                            const displayText = isDropbox && integration.account_email
                              ? `${integration.account_name} (${integration.account_email})`
                              : integration.account_name;
                            // T035: Truncate at 50 chars
                            return displayText.length > 50 
                              ? `${displayText.substring(0, 50)}...` 
                              : displayText;
                          })()}
                        </div>
                      ) : (
                        // T034: Generic message for legacy connections
                        <div className="font-medium">Connected</div>
                      )}
                      {/* T038-T040: Display connection date */}
                      {integration.connected_at && (
                        <div className="text-xs text-muted-foreground">
                          Connected on: {format(new Date(integration.connected_at), 'MMM d, yyyy')}
                        </div>
                      )}
                      <div className="text-xs">
                        Last synced: {format(new Date(integration.last_sync), 'PPp')}
                      </div>
                    </div>
                  ) : (
                    integration.reason || 'Not connected'
                  )}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-2">
                {isDropbox && (
                  <>
                    {isConnected ? (
                      <Button
                        variant="destructive"
                        size="sm"
                        className="w-full"
                        onClick={() => handleDisconnectClick(integration.provider)}
                        disabled={actionLoading}
                      >
                        Disconnect
                      </Button>
                    ) : (
                      <Button
                        variant="outline"
                        size="sm"
                        className="w-full"
                        onClick={() => handleConnect(integration.provider)}
                        disabled={actionLoading}
                      >
                        Connect Dropbox
                      </Button>
                    )}
                  </>
                )}
                {isBasecamp && (
                  <>
                    {isConnected ? (
                      <Button
                        variant="destructive"
                        size="sm"
                        className="w-full"
                        onClick={() => handleDisconnectClick(integration.provider)}
                        disabled={actionLoading}
                      >
                        Disconnect
                      </Button>
                    ) : (
                      <Button
                        variant="outline"
                        size="sm"
                        className="w-full"
                        onClick={() => handleConnect(integration.provider)}
                        disabled={actionLoading}
                      >
                        Connect Basecamp
                      </Button>
                    )}
                  </>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Disconnect Confirmation Dialog */}
      <Dialog open={disconnectDialogOpen} onOpenChange={setDisconnectDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Disconnect Integration?</DialogTitle>
            <DialogDescription>
              Are you sure you want to disconnect {selectedProvider}? You will need to
              re-authenticate to use this integration again.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setDisconnectDialogOpen(false)}
              disabled={actionLoading}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleDisconnectConfirm}
              disabled={actionLoading}
            >
              {actionLoading ? 'Disconnecting...' : 'Disconnect'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

