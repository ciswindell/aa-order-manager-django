import { Order } from '@/lib/api/types';
import { format } from 'date-fns';
import { CalendarDays, FileText, User } from 'lucide-react';

interface OrderDetailsHeaderProps {
  order: Order;
}

export function OrderDetailsHeader({ order }: OrderDetailsHeaderProps) {
  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-3xl font-bold">{order.order_number}</h1>
        <p className="text-muted-foreground">Order Details</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <div className="flex items-start gap-3">
          <CalendarDays className="h-5 w-5 text-muted-foreground mt-0.5" />
          <div>
            <p className="text-sm font-medium">Order Date</p>
            <p className="text-sm text-muted-foreground">
              {format(new Date(order.order_date), 'PPP')}
            </p>
          </div>
        </div>

        {order.created_by_username && (
          <div className="flex items-start gap-3">
            <User className="h-5 w-5 text-muted-foreground mt-0.5" />
            <div>
              <p className="text-sm font-medium">Created By</p>
              <p className="text-sm text-muted-foreground">{order.created_by_username}</p>
            </div>
          </div>
        )}

        <div className="flex items-start gap-3">
          <FileText className="h-5 w-5 text-muted-foreground mt-0.5" />
          <div>
            <p className="text-sm font-medium">Reports</p>
            <p className="text-sm text-muted-foreground">{order.report_count} report(s)</p>
          </div>
        </div>
      </div>

      {order.order_notes && (
        <div className="rounded-lg border p-4">
          <p className="text-sm font-medium mb-2">Notes</p>
          <p className="text-sm text-muted-foreground whitespace-pre-wrap">{order.order_notes}</p>
        </div>
      )}

      {order.delivery_link && (
        <div className="rounded-lg border p-4">
          <p className="text-sm font-medium mb-2">Delivery Link</p>
          <a
            href={order.delivery_link}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-primary hover:underline break-all"
          >
            {order.delivery_link}
          </a>
        </div>
      )}
    </div>
  );
}

