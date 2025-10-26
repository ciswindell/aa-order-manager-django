import { createLease, deleteLease, getLeases, updateLease } from '@/lib/api/leases';
import { Lease, LeaseFormData } from '@/lib/api/types';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';

export function useLeases(page = 1, pageSize = 20, reportId?: number, agency?: string) {
  const queryClient = useQueryClient();

  const leasesQuery = useQuery({
    queryKey: ['leases', page, pageSize, reportId, agency],
    queryFn: () => getLeases(page, pageSize, reportId, agency),
  });

  const createMutation = useMutation({
    mutationFn: (data: LeaseFormData) => createLease(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leases'] });
      toast.success('Lease Created', {
        description: 'The lease has been created successfully',
        duration: 5000,
      });
    },
    onError: (error: any) => {
      toast.error('Creation Failed', {
        description: error?.message || 'Failed to create lease',
      });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: LeaseFormData }) => updateLease(id, data),
    onMutate: async ({ id, data }) => {
      await queryClient.cancelQueries({ queryKey: ['leases'] });
      const previousLeases = queryClient.getQueryData([
        'leases',
        page,
        pageSize,
        reportId,
        agency,
      ]);

      queryClient.setQueryData(
        ['leases', page, pageSize, reportId, agency],
        (old: any) => {
          if (!old?.data?.results) return old;
          return {
            ...old,
            data: {
              ...old.data,
              results: old.data.results.map((lease: Lease) =>
                lease.id === id ? { ...lease, ...data } : lease
              ),
            },
          };
        }
      );

      return { previousLeases };
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leases'] });
      toast.success('Lease Updated', {
        description: 'The lease has been updated successfully',
        duration: 5000,
      });
    },
    onError: (error: any, _variables, context) => {
      if (context?.previousLeases) {
        queryClient.setQueryData(
          ['leases', page, pageSize, reportId, agency],
          context.previousLeases
        );
      }
      toast.error('Update Failed', {
        description: error?.message || 'Failed to update lease',
      });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteLease(id),
    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: ['leases'] });
      const previousLeases = queryClient.getQueryData([
        'leases',
        page,
        pageSize,
        reportId,
        agency,
      ]);

      queryClient.setQueryData(
        ['leases', page, pageSize, reportId, agency],
        (old: any) => {
          if (!old?.data?.results) return old;
          return {
            ...old,
            data: {
              ...old.data,
              results: old.data.results.filter((lease: Lease) => lease.id !== id),
              count: old.data.count - 1,
            },
          };
        }
      );

      return { previousLeases };
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leases'] });
      toast.success('Lease Deleted', {
        description: 'The lease has been deleted successfully',
        duration: 5000,
      });
    },
    onError: (error: any, _variables, context) => {
      if (context?.previousLeases) {
        queryClient.setQueryData(
          ['leases', page, pageSize, reportId, agency],
          context.previousLeases
        );
      }
      const errorMessage =
        error?.message || error?.response?.data?.error || 'Failed to delete lease';
      toast.error('Deletion Failed', {
        description: errorMessage,
      });
    },
  });

  return {
    leases: leasesQuery.data?.data?.results || [],
    totalCount: leasesQuery.data?.data?.count || 0,
    isLoading: leasesQuery.isLoading,
    isError: leasesQuery.isError,
    error: leasesQuery.error,
    createLease: createMutation.mutate,
    updateLease: updateMutation.mutate,
    deleteLease: deleteMutation.mutate,
    isCreating: createMutation.isPending,
    isUpdating: updateMutation.isPending,
    isDeleting: deleteMutation.isPending,
  };
}

