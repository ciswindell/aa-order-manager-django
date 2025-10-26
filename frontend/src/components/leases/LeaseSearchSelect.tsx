import { InlineLeaseCreateForm } from '@/components/leases/InlineLeaseCreateForm';
import { Button } from '@/components/ui/button';
import { MultiSelect } from '@/components/ui/multi-select';
import { searchLeases } from '@/lib/api/leases';
import { Lease, LeaseOption } from '@/lib/api/types';
import { useQuery } from '@tanstack/react-query';
import { Plus } from 'lucide-react';
import { useCallback, useEffect, useMemo, useState } from 'react';

interface LeaseSearchSelectProps {
  leases: Lease[];
  selectedLeaseIds: number[];
  onChange: (leaseIds: number[]) => void;
  disabled?: boolean;
  allowInlineCreate?: boolean;
}

export function LeaseSearchSelect({
  leases,
  selectedLeaseIds,
  onChange,
  disabled,
  allowInlineCreate = true,
}: LeaseSearchSelectProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [debouncedSearchTerm, setDebouncedSearchTerm] = useState('');
  const [showInlineCreate, setShowInlineCreate] = useState(false);

  // Debounce search term (300ms)
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearchTerm(searchTerm);
    }, 300);

    return () => clearTimeout(timer);
  }, [searchTerm]);

  // Search leases on backend when search term changes
  const { data: searchResults, isLoading } = useQuery({
    queryKey: ['leases', 'search', debouncedSearchTerm],
    queryFn: () => searchLeases(debouncedSearchTerm),
    enabled: debouncedSearchTerm.length > 0,
    staleTime: 30000, // Cache for 30 seconds
  });

  // Use search results if searching, otherwise use provided leases
  const availableLeases = useMemo(() => {
    if (debouncedSearchTerm.length > 0 && searchResults?.data?.results) {
      return searchResults.data.results;
    }
    return leases;
  }, [debouncedSearchTerm, searchResults, leases]);

  // Convert leases to options format
  const leaseOptions = useMemo(
    () =>
      availableLeases.map((lease) => ({
        label: `${lease.agency} ${lease.lease_number}`,
        value: lease.id,
        lease,
      })) as LeaseOption[],
    [availableLeases]
  );

  // Ensure selected leases are always included in options
  const selectedLeases = useMemo(() => {
    return leases.filter((lease) => selectedLeaseIds.includes(lease.id));
  }, [leases, selectedLeaseIds]);

  const allOptions = useMemo(() => {
    const selectedOptions = selectedLeases.map((lease) => ({
      label: `${lease.agency} ${lease.lease_number}`,
      value: lease.id,
      lease,
    })) as LeaseOption[];

    // Merge selected options with search results, removing duplicates
    const optionMap = new Map<number, LeaseOption>();
    selectedOptions.forEach((opt) => optionMap.set(opt.value as number, opt));
    leaseOptions.forEach((opt) => optionMap.set(opt.value as number, opt));

    return Array.from(optionMap.values());
  }, [leaseOptions, selectedLeases]);

  const handleSearchChange = useCallback((value: string) => {
    setSearchTerm(value);
  }, []);

  const handleLeaseCreated = useCallback(
    (leaseId: number) => {
      // Auto-select the newly created lease
      onChange([...selectedLeaseIds, leaseId]);
      // Hide the inline form
      setShowInlineCreate(false);
    },
    [selectedLeaseIds, onChange]
  );

  const handleToggleInlineCreate = useCallback(() => {
    setShowInlineCreate((prev) => !prev);
  }, []);

  return (
    <MultiSelect
      options={allOptions}
      selected={selectedLeaseIds}
      onChange={(selected) => onChange(selected as number[])}
      placeholder="Select leases..."
      emptyText={isLoading ? 'Searching...' : 'No leases found.'}
      disabled={disabled}
      onSearchChange={handleSearchChange}
      emptyAction={
        allowInlineCreate && !disabled && searchTerm.length > 0 ? (
          showInlineCreate ? (
            <InlineLeaseCreateForm
              onSuccess={handleLeaseCreated}
              onCancel={handleToggleInlineCreate}
              initialLeaseNumber={searchTerm}
            />
          ) : (
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={handleToggleInlineCreate}
              className="w-full mt-2"
            >
              <Plus className="h-4 w-4 mr-2" />
                  Add &quot;{searchTerm}&quot;
            </Button>
          )
        ) : undefined
      }
    />
  );
}



