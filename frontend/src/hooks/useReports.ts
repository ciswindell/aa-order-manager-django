import { createReport, deleteReport, getReports, updateReport } from '@/lib/api/reports';
import { Report, ReportFormData } from '@/lib/api/types';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';

export function useReports(page = 1, pageSize = 20, orderId?: number) {
  const queryClient = useQueryClient();

  const reportsQuery = useQuery({
    queryKey: ['reports', page, pageSize, orderId],
    queryFn: () => getReports(page, pageSize, orderId),
  });

  const createMutation = useMutation({
    mutationFn: (data: ReportFormData) => createReport(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reports'] });
      toast.success('Report Created', {
        description: 'The report has been created successfully',
        duration: 5000,
      });
    },
    onError: (error: any) => {
      toast.error('Creation Failed', {
        description: error?.message || 'Failed to create report',
      });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: ReportFormData }) => updateReport(id, data),
    onMutate: async ({ id, data }) => {
      await queryClient.cancelQueries({ queryKey: ['reports'] });
      const previousReports = queryClient.getQueryData(['reports', page, pageSize, orderId]);

      queryClient.setQueryData(['reports', page, pageSize, orderId], (old: any) => {
        if (!old?.data?.results) return old;
        return {
          ...old,
          data: {
            ...old.data,
            results: old.data.results.map((report: Report) =>
              report.id === id ? { ...report, ...data } : report
            ),
          },
        };
      });

      return { previousReports };
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reports'] });
      toast.success('Report Updated', {
        description: 'The report has been updated successfully',
        duration: 5000,
      });
    },
    onError: (error: any, _variables, context) => {
      if (context?.previousReports) {
        queryClient.setQueryData(['reports', page, pageSize, orderId], context.previousReports);
      }
      toast.error('Update Failed', {
        description: error?.message || 'Failed to update report',
      });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteReport(id),
    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: ['reports'] });
      const previousReports = queryClient.getQueryData(['reports', page, pageSize, orderId]);

      queryClient.setQueryData(['reports', page, pageSize, orderId], (old: any) => {
        if (!old?.data?.results) return old;
        return {
          ...old,
          data: {
            ...old.data,
            results: old.data.results.filter((report: Report) => report.id !== id),
            count: old.data.count - 1,
          },
        };
      });

      return { previousReports };
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reports'] });
      toast.success('Report Deleted', {
        description: 'The report has been deleted successfully',
        duration: 5000,
      });
    },
    onError: (error: any, _variables, context) => {
      if (context?.previousReports) {
        queryClient.setQueryData(['reports', page, pageSize, orderId], context.previousReports);
      }
      const errorMessage =
        error?.message || error?.response?.data?.error || 'Failed to delete report';
      toast.error('Deletion Failed', {
        description: errorMessage,
      });
    },
  });

  return {
    reports: reportsQuery.data?.data?.results || [],
    totalCount: reportsQuery.data?.data?.count || 0,
    isLoading: reportsQuery.isLoading,
    isError: reportsQuery.isError,
    error: reportsQuery.error,
    createReport: createMutation.mutate,
    updateReport: updateMutation.mutate,
    deleteReport: deleteMutation.mutate,
    isCreating: createMutation.isPending,
    isUpdating: updateMutation.isPending,
    isDeleting: deleteMutation.isPending,
  };
}

