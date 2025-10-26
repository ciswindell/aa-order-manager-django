import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from '@/components/ui/popover';
import { Lease } from '@/lib/api/types';
import { CheckCircle2, XCircle } from 'lucide-react';

interface LeaseDetailsPopoverProps {
  lease: Lease;
  children: React.ReactNode;
}

export function LeaseDetailsPopover({ lease, children }: LeaseDetailsPopoverProps) {
  return (
    <Popover>
      <PopoverTrigger asChild>
        {children}
      </PopoverTrigger>
      <PopoverContent className="w-80" align="start">
        <div className="space-y-3">
          <div>
            <h4 className="font-semibold text-sm mb-1">Lease Details</h4>
            <p className="text-sm text-muted-foreground">
              {lease.agency} {lease.lease_number}
            </p>
          </div>

          <div className="space-y-2 pt-2 border-t">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Agency:</span>
              <span className="text-sm font-medium">{lease.agency}</span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Lease Number:</span>
              <span className="text-sm font-medium">{lease.lease_number}</span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Runsheet Status:</span>
              <div className="flex items-center gap-1">
                {lease.runsheet_report_found ? (
                  <>
                    <CheckCircle2 className="h-4 w-4 text-green-500" />
                    <span className="text-sm font-medium">Found</span>
                  </>
                ) : (
                  <>
                    <XCircle className="h-4 w-4 text-red-500" />
                    <span className="text-sm font-medium">Not Found</span>
                  </>
                )}
              </div>
            </div>
          </div>

          {lease.notes && (
            <div className="pt-2 border-t">
              <span className="text-sm text-muted-foreground block mb-1">Notes:</span>
              <p className="text-sm">{lease.notes}</p>
            </div>
          )}

          {lease.created_at && (
            <div className="pt-2 border-t text-xs text-muted-foreground">
              Created: {new Date(lease.created_at).toLocaleDateString()}
            </div>
          )}
        </div>
      </PopoverContent>
    </Popover>
  );
}

