import { Navigation } from '@/components/layout/nav';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen">
      <Navigation />
      <main className="flex-1">{children}</main>
    </div>
  );
}

