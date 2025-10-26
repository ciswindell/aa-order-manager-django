import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';
import { useLeases } from '@/hooks/useLeases';
import { AgencyType, LeaseFormData } from '@/lib/api/types';
import { X } from 'lucide-react';
import { useState } from 'react';

const AGENCY_TYPES: AgencyType[] = ['BLM', 'NMSLO'];

interface InlineLeaseCreateFormProps {
  onSuccess?: (leaseId: number) => void;
  onCancel?: () => void;
  initialLeaseNumber?: string;
}

export function InlineLeaseCreateForm({
  onSuccess,
  onCancel,
  initialLeaseNumber = '',
}: InlineLeaseCreateFormProps) {
  const { createLease, isCreating } = useLeases();
  const [formData, setFormData] = useState<LeaseFormData>({
    agency: 'BLM',
    lease_number: initialLeaseNumber,
  });

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    createLease(formData, {
      onSuccess: (lease) => {
        onSuccess?.(lease.id);
        // Reset form
        setFormData({ agency: 'BLM', lease_number: '' });
      },
    });
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !isCreating) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="space-y-3 p-3 border rounded-lg bg-background" onKeyDown={handleKeyDown}>
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-medium">Create New Lease</h3>
        {onCancel && (
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={onCancel}
            disabled={isCreating}
            className="h-6 w-6 p-0"
          >
            <X className="h-4 w-4" />
          </Button>
        )}
      </div>
      <div className="space-y-3">
        <div className="space-y-1.5">
          <label htmlFor="agency" className="text-xs font-medium">
            Agency
          </label>
          <Select
            value={formData.agency}
            onValueChange={(value: AgencyType) =>
              setFormData({ ...formData, agency: value })
            }
            disabled={isCreating}
          >
            <SelectTrigger className="w-full h-9">
              <SelectValue placeholder="Select agency" />
            </SelectTrigger>
            <SelectContent>
              {AGENCY_TYPES.map((agency) => (
                <SelectItem key={agency} value={agency}>
                  {agency}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-1.5">
          <label htmlFor="lease_number" className="text-xs font-medium">
            Lease Number
          </label>
          <Input
            id="lease_number"
            value={formData.lease_number}
            onChange={(e) =>
              setFormData({ ...formData, lease_number: e.target.value })
            }
            placeholder="Enter lease number..."
            required
            disabled={isCreating}
            className="h-9"
          />
        </div>
      </div>
      <div className="flex justify-end gap-2 pt-2">
        {onCancel && (
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={onCancel}
            disabled={isCreating}
          >
            Cancel
          </Button>
        )}
        <Button type="button" size="sm" onClick={() => handleSubmit()} disabled={isCreating}>
          {isCreating ? 'Creating...' : 'Create'}
        </Button>
      </div>
    </div>
  );
}

