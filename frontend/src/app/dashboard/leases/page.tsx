'use client';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from '@/components/ui/dialog';
import { Field, FieldGroup, FieldLabel } from '@/components/ui/field';
import { Input } from '@/components/ui/input';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table';
import { useAuth } from '@/hooks/useAuth';
import { useLeases } from '@/hooks/useLeases';
import { AgencyType, LeaseFormData, RunsheetStatus } from '@/lib/api/types';
import { format } from 'date-fns';
import {
    ChevronLeft,
    ChevronRight,
    Edit,
    ExternalLink,
    Plus,
    Trash2
} from 'lucide-react';
import { useSearchParams } from 'next/navigation';
import { Suspense, useEffect, useState } from 'react';

function LeaseStatusBadge({ status }: { status: RunsheetStatus }) {
  const variants: Record<RunsheetStatus, { variant: string; className: string }> = {
    Found: {
      variant: 'default',
      className: 'bg-green-500 hover:bg-green-500 text-white',
    },
    'Not Found': {
      variant: 'destructive',
      className: '',
    },
    Pending: {
      variant: 'secondary',
      className: 'bg-yellow-500 hover:bg-yellow-500 text-white',
    },
  };

  const config = variants[status];
  return (
    <Badge variant={config.variant as any} className={config.className}>
      {status}
    </Badge>
  );
}

function LeasesPageContent() {
  const { user } = useAuth();
  const searchParams = useSearchParams();
  const [page, setPage] = useState(1);
  const [selectedAgency, setSelectedAgency] = useState<string | undefined>(undefined);
  const [reportIdFilter, setReportIdFilter] = useState<number | undefined>(undefined);
  const pageSize = 20;

  // Get report_id from URL query parameter if present
  useEffect(() => {
    const reportIdParam = searchParams.get('report_id');
    if (reportIdParam) {
      setReportIdFilter(Number(reportIdParam));
    }
  }, [searchParams]);

  const {
    leases,
    totalCount,
    isLoading,
    createLease,
    updateLease,
    deleteLease,
    isCreating,
    isUpdating,
    isDeleting,
  } = useLeases(page, pageSize, reportIdFilter, selectedAgency);

  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedLease, setSelectedLease] = useState<any>(null);

  const AGENCY_OPTIONS: AgencyType[] = ['BLM', 'NMSLO'];

  const [formData, setFormData] = useState<LeaseFormData>({
    agency: 'BLM',
    lease_number: '',
  });

  const totalPages = Math.ceil(totalCount / pageSize);

  // Get unique agency names from leases for filter dropdown
  const uniqueAgencies = Array.from(new Set(leases.map((l) => l.agency))).sort();

  const handleCreateClick = () => {
    setFormData({
      agency: 'BLM',
      lease_number: '',
    });
    setCreateDialogOpen(true);
  };

  const handleEditClick = (lease: any) => {
    setSelectedLease(lease);
    setFormData({
      agency: lease.agency,
      lease_number: lease.lease_number,
    });
    setEditDialogOpen(true);
  };

  const handleDeleteClick = (lease: any) => {
    setSelectedLease(lease);
    setDeleteDialogOpen(true);
  };

  const handleCreateSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createLease(formData, {
      onSuccess: () => {
        setCreateDialogOpen(false);
      },
    });
  };

  const handleEditSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedLease) {
      updateLease(
        { id: selectedLease.id, data: formData },
        {
          onSuccess: () => {
            setEditDialogOpen(false);
            setSelectedLease(null);
          },
        }
      );
    }
  };

  const handleDeleteConfirm = () => {
    if (selectedLease) {
      deleteLease(selectedLease.id);
      setDeleteDialogOpen(false);
      setSelectedLease(null);
    }
  };

  if (!user) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-muted-foreground">Loading...</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Leases</h1>
          <p className="text-muted-foreground">Manage your leases</p>
        </div>
        <div className="flex gap-2">
          {uniqueAgencies.length > 0 && (
            <Select
              value={selectedAgency || 'all'}
              onValueChange={(value: string) => {
                if (value === 'all') {
                  setSelectedAgency(undefined);
                } else {
                  setSelectedAgency(value);
                }
                setPage(1);
              }}
            >
              <SelectTrigger className="w-[200px]">
                <SelectValue placeholder="Filter by Agency" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Agencies</SelectItem>
                {uniqueAgencies.map((agency) => (
                  <SelectItem key={agency} value={agency}>
                    {agency}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
          <Button onClick={handleCreateClick}>
            <Plus className="mr-2 h-4 w-4" />
            Create Lease
          </Button>
        </div>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-8">
          <p className="text-muted-foreground">Loading leases...</p>
        </div>
      ) : leases.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <p className="text-muted-foreground mb-4">
            {selectedAgency || reportIdFilter ? 'No leases found for selected filter' : 'No leases found'}
          </p>
          <Button onClick={handleCreateClick} variant="outline">
            <Plus className="mr-2 h-4 w-4" />
            Create your first lease
          </Button>
        </div>
      ) : (
        <>
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Agency</TableHead>
                  <TableHead>Lease Number</TableHead>
                  <TableHead>Runsheet Status</TableHead>
                  <TableHead>Runsheet Link</TableHead>
                  <TableHead>Documents Link</TableHead>
                  <TableHead>Created</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {leases.map((lease) => (
                  <TableRow key={lease.id}>
                    <TableCell className="font-medium">{lease.agency}</TableCell>
                    <TableCell>{lease.lease_number}</TableCell>
                    <TableCell>
                      <LeaseStatusBadge status={lease.runsheet_status} />
                    </TableCell>
                    <TableCell>
                      {lease.runsheet_link || lease.runsheet_archive_link ? (
                        <a
                          href={lease.runsheet_link || lease.runsheet_archive_link || '#'}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1 text-primary hover:underline"
                        >
                          <ExternalLink className="h-4 w-4" />
                        </a>
                      ) : (
                        <span className="text-muted-foreground">-</span>
                      )}
                    </TableCell>
                    <TableCell>
                      {lease.document_archive_link ? (
                        <a
                          href={lease.document_archive_link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1 text-primary hover:underline"
                        >
                          <ExternalLink className="h-4 w-4" />
                        </a>
                      ) : (
                        <span className="text-muted-foreground">-</span>
                      )}
                    </TableCell>
                    <TableCell>{format(new Date(lease.created_at), 'PP')}</TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button variant="ghost" size="sm" onClick={() => handleEditClick(lease)}>
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDeleteClick(lease)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>

          {totalPages > 1 && (
            <div className="flex items-center justify-between mt-4">
              <div className="text-sm text-muted-foreground">
                Page {page} of {totalPages} ({totalCount} total leases)
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage(page - 1)}
                  disabled={page === 1}
                >
                  <ChevronLeft className="h-4 w-4 mr-1" />
                  Previous
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage(page + 1)}
                  disabled={page === totalPages}
                >
                  Next
                  <ChevronRight className="h-4 w-4 ml-1" />
                </Button>
              </div>
            </div>
          )}
        </>
      )}

      {/* Create Lease Dialog */}
      <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
        <DialogContent>
          <form onSubmit={handleCreateSubmit}>
            <DialogHeader>
              <DialogTitle>Create Lease</DialogTitle>
              <DialogDescription>Add a new lease to the system</DialogDescription>
            </DialogHeader>
            <FieldGroup>
              <Field>
                <FieldLabel htmlFor="agency">Agency</FieldLabel>
                <Select
                  value={formData.agency}
                  onValueChange={(value: AgencyType) => setFormData({ ...formData, agency: value })}
                >
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Select agency" />
                  </SelectTrigger>
                  <SelectContent>
                    {AGENCY_OPTIONS.map((agency) => (
                      <SelectItem key={agency} value={agency}>
                        {agency}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </Field>
              <Field>
                <FieldLabel htmlFor="lease_number">Lease Number</FieldLabel>
                <Input
                  id="lease_number"
                  value={formData.lease_number}
                  onChange={(e) => setFormData({ ...formData, lease_number: e.target.value })}
                  placeholder="e.g., NM-12345"
                  required
                />
              </Field>
            </FieldGroup>
            <DialogFooter className="mt-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => setCreateDialogOpen(false)}
                disabled={isCreating}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={isCreating}>
                {isCreating ? 'Creating...' : 'Create Lease'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Edit Lease Dialog */}
      <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
        <DialogContent>
          <form onSubmit={handleEditSubmit}>
            <DialogHeader>
              <DialogTitle>Edit Lease</DialogTitle>
              <DialogDescription>
                Update lease details (runsheet fields are managed automatically)
              </DialogDescription>
            </DialogHeader>
            <FieldGroup>
              <Field>
                <FieldLabel htmlFor="edit_agency">Agency</FieldLabel>
                <Select
                  value={formData.agency}
                  onValueChange={(value: AgencyType) => setFormData({ ...formData, agency: value })}
                >
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Select agency" />
                  </SelectTrigger>
                  <SelectContent>
                    {AGENCY_OPTIONS.map((agency) => (
                      <SelectItem key={agency} value={agency}>
                        {agency}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </Field>
              <Field>
                <FieldLabel htmlFor="edit_lease_number">Lease Number</FieldLabel>
                <Input
                  id="edit_lease_number"
                  value={formData.lease_number}
                  onChange={(e) => setFormData({ ...formData, lease_number: e.target.value })}
                  placeholder="e.g., NM-12345"
                  required
                />
              </Field>
              {selectedLease && (
                <div className="rounded-md bg-muted p-3 text-sm">
                  <p className="font-semibold mb-1">Runsheet Information (Read-Only)</p>
                  <p className="text-muted-foreground">
                    Status: {selectedLease.runsheet_status}
                  </p>
                  <p className="text-muted-foreground text-xs mt-1">
                    Runsheet links are managed automatically by background tasks
                  </p>
                </div>
              )}
            </FieldGroup>
            <DialogFooter className="mt-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => setEditDialogOpen(false)}
                disabled={isUpdating}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={isUpdating}>
                {isUpdating ? 'Updating...' : 'Update Lease'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Lease?</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete lease &quot;{selectedLease?.lease_number}&quot; from{' '}
              {selectedLease?.agency}? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setDeleteDialogOpen(false)}
              disabled={isDeleting}
            >
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleDeleteConfirm} disabled={isDeleting}>
              {isDeleting ? 'Deleting...' : 'Delete'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

export default function LeasesPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-screen items-center justify-center">
          <p className="text-muted-foreground">Loading...</p>
        </div>
      }
    >
      <LeasesPageContent />
    </Suspense>
  );
}

