import { LeaseSearchSelect } from '@/components/leases/LeaseSearchSelect';
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
import { Textarea } from '@/components/ui/textarea';
import { Lease, REPORT_TYPE_LABELS, ReportFormData, ReportType } from '@/lib/api/types';

const REPORT_TYPES: ReportType[] = [
  'RUNSHEET',
  'BASE_ABSTRACT',
  'SUPPLEMENTAL_ABSTRACT',
  'DOL_ABSTRACT',
];

interface ReportFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  mode: 'create' | 'edit';
  orderId: number;
  leases: Lease[];
  formData: ReportFormData;
  onFormDataChange: (data: ReportFormData) => void;
  onSubmit: (e: React.FormEvent) => void;
  isSubmitting: boolean;
}

export function ReportFormDialog({
  open,
  onOpenChange,
  mode,
  leases,
  formData,
  onFormDataChange,
  onSubmit,
  isSubmitting,
}: ReportFormDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <form onSubmit={onSubmit}>
          <DialogHeader>
            <DialogTitle>
              {mode === 'create' ? 'Create Report' : 'Edit Report'}
            </DialogTitle>
            <DialogDescription>
              {mode === 'create' 
                ? 'Add a new report to this order' 
                : 'Update report details'}
            </DialogDescription>
          </DialogHeader>
          <FieldGroup>
            <Field>
              <FieldLabel htmlFor="report_type">Report Type</FieldLabel>
              <Select
                value={formData.report_type}
                onValueChange={(value: string) =>
                  onFormDataChange({ ...formData, report_type: value })
                }
              >
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select report type" />
                </SelectTrigger>
                <SelectContent>
                  {REPORT_TYPES.map((type) => (
                    <SelectItem key={type} value={type}>
                      {REPORT_TYPE_LABELS[type]}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </Field>
            <Field>
              <FieldLabel htmlFor="legal_description">Legal Description</FieldLabel>
              <Textarea
                id="legal_description"
                value={formData.legal_description}
                onChange={(e) =>
                  onFormDataChange({
                    ...formData,
                    legal_description: e.target.value,
                  })
                }
                placeholder="Enter legal description..."
                required
              />
            </Field>
            <Field>
              <FieldLabel htmlFor="start_date">Start Date (Optional)</FieldLabel>
              <Input
                id="start_date"
                type="date"
                value={formData.start_date || ''}
                onChange={(e) =>
                  onFormDataChange({ ...formData, start_date: e.target.value })
                }
              />
            </Field>
            <Field>
              <FieldLabel htmlFor="end_date">End Date (Optional)</FieldLabel>
              <Input
                id="end_date"
                type="date"
                value={formData.end_date || ''}
                onChange={(e) =>
                  onFormDataChange({ ...formData, end_date: e.target.value })
                }
              />
            </Field>
            <Field>
              <FieldLabel htmlFor="report_notes">Notes (Optional)</FieldLabel>
              <Textarea
                id="report_notes"
                value={formData.report_notes || ''}
                onChange={(e) =>
                  onFormDataChange({ ...formData, report_notes: e.target.value })
                }
                placeholder="Enter any notes..."
              />
            </Field>
            <Field>
              <FieldLabel>Leases *</FieldLabel>
              <LeaseSearchSelect
                leases={leases}
                selectedLeaseIds={formData.lease_ids || []}
                onChange={(leaseIds) =>
                  onFormDataChange({ ...formData, lease_ids: leaseIds })
                }
                disabled={isSubmitting}
              />
            </Field>
          </FieldGroup>
          <DialogFooter className="mt-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting
                ? mode === 'create'
                  ? 'Creating...'
                  : 'Updating...'
                : mode === 'create'
                ? 'Create Report'
                : 'Update Report'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}



