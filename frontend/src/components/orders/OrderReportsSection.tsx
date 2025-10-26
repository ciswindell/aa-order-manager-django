import { LeaseDetailsPopover } from '@/components/leases/LeaseDetailsPopover';
import { Button } from '@/components/ui/button';
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from '@/components/ui/popover';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table';
import { Report } from '@/lib/api/types';
import { format } from 'date-fns';
import { Pencil, Plus, Trash2 } from 'lucide-react';

interface OrderReportsSectionProps {
  reports: Report[];
  isLoading: boolean;
  onAddReport?: () => void;
  onEditReport?: (report: Report) => void;
  onDeleteReport?: (report: Report) => void;
}

export function OrderReportsSection({
  reports,
  isLoading,
  onAddReport,
  onEditReport,
  onDeleteReport,
}: OrderReportsSectionProps) {
  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold">Reports</h2>
        </div>
        <div className="flex items-center justify-center py-8">
          <p className="text-muted-foreground">Loading reports...</p>
        </div>
      </div>
    );
  }

  const formatLeaseNumbers = (report: Report) => {
    if (!report.leases || report.leases.length === 0) {
      return <span className="text-muted-foreground">No leases</span>;
    }

    const maxVisible = 5;
    const visibleLeases = report.leases.slice(0, maxVisible);
    const remainingLeases = report.leases.slice(maxVisible);
    const hasMore = remainingLeases.length > 0;

    return (
      <div className="flex flex-wrap gap-1">
        {visibleLeases.map((lease) => (
          <LeaseDetailsPopover key={lease.id} lease={lease}>
            <button
              className="inline-flex items-center rounded-md bg-secondary px-2 py-1 text-xs font-medium hover:bg-secondary/80 transition-colors cursor-pointer"
            >
              {lease.lease_number}
            </button>
          </LeaseDetailsPopover>
        ))}
        {hasMore && (
          <Popover>
            <PopoverTrigger asChild>
              <button className="inline-flex items-center rounded-md bg-muted px-2 py-1 text-xs font-medium hover:bg-muted/80 transition-colors cursor-pointer">
                +{remainingLeases.length} more
              </button>
            </PopoverTrigger>
            <PopoverContent className="w-80" align="start">
              <div className="space-y-2">
                <h4 className="font-semibold text-sm mb-2">
                  Additional Leases ({remainingLeases.length})
                </h4>
                <div className="space-y-1 max-h-60 overflow-y-auto">
                  {remainingLeases.map((lease) => (
                    <LeaseDetailsPopover key={lease.id} lease={lease}>
                      <button className="w-full text-left px-2 py-1 text-xs rounded hover:bg-secondary transition-colors">
                        {lease.agency} {lease.lease_number}
                      </button>
                    </LeaseDetailsPopover>
                  ))}
                </div>
              </div>
            </PopoverContent>
          </Popover>
        )}
      </div>
    );
  };

  const formatDateRange = (startDate: string | null, endDate: string | null) => {
    if (!startDate && !endDate) {
      return <span className="text-muted-foreground">-</span>;
    }
    const start = startDate ? format(new Date(startDate), 'PP') : 'N/A';
    const end = endDate ? format(new Date(endDate), 'PP') : 'N/A';
    return `${start} - ${end}`;
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Reports</h2>
        {onAddReport && (
          <Button onClick={onAddReport}>
            <Plus className="mr-2 h-4 w-4" />
            Add Report
          </Button>
        )}
      </div>

      {reports.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12 text-center border rounded-lg">
          <p className="text-muted-foreground mb-4">No reports added yet</p>
          {onAddReport && (
            <Button onClick={onAddReport} variant="outline">
              <Plus className="mr-2 h-4 w-4" />
              Add your first report
            </Button>
          )}
        </div>
      ) : (
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Type</TableHead>
                <TableHead>Legal Description</TableHead>
                <TableHead>Date Range</TableHead>
                <TableHead>Lease Numbers</TableHead>
                {(onEditReport || onDeleteReport) && <TableHead className="text-right">Actions</TableHead>}
              </TableRow>
            </TableHeader>
            <TableBody>
              {reports.map((report) => (
                <TableRow key={report.id}>
                  <TableCell className="font-medium">{report.report_type}</TableCell>
                  <TableCell>
                    <div className="max-w-md truncate" title={report.legal_description}>
                      {report.legal_description}
                    </div>
                  </TableCell>
                  <TableCell>{formatDateRange(report.start_date, report.end_date)}</TableCell>
                  <TableCell>{formatLeaseNumbers(report)}</TableCell>
                  {(onEditReport || onDeleteReport) && (
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        {onEditReport && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => onEditReport(report)}
                          >
                            <Pencil className="h-4 w-4" />
                          </Button>
                        )}
                        {onDeleteReport && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => onDeleteReport(report)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                    </TableCell>
                  )}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  );
}

