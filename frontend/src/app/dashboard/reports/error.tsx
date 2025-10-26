'use client';

import { Button } from '@/components/ui/button';
import { AlertCircle } from 'lucide-react';
import { useEffect } from 'react';

export default function ReportsError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error('Reports error:', error);
  }, [error]);

  return (
    <div className="flex min-h-screen items-center justify-center p-6">
      <div className="max-w-md text-center">
        <AlertCircle className="mx-auto h-12 w-12 text-destructive mb-4" />
        <h2 className="text-2xl font-bold mb-2">Something went wrong!</h2>
        <p className="text-muted-foreground mb-6">
          An error occurred while loading reports. Please try again.
        </p>
        {error.message && (
          <p className="text-sm text-muted-foreground mb-4 p-3 bg-muted rounded">
            {error.message}
          </p>
        )}
        <div className="flex gap-2 justify-center">
          <Button onClick={reset}>Try again</Button>
          <Button variant="outline" onClick={() => (window.location.href = '/dashboard')}>
            Go to Dashboard
          </Button>
        </div>
      </div>
    </div>
  );
}

