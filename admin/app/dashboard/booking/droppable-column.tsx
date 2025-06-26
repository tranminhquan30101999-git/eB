import { useDroppable } from "@dnd-kit/core";
import { Booking, BookingStatus } from "./type/booking-status";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { SortableContext, verticalListSortingStrategy } from "@dnd-kit/sortable";
import BookingCard from "./booking-card";

export default function DroppableColumn({
  column,
  bookings,
}: {
  column: { id: BookingStatus; title: string; color: string };
  bookings: Booking[];
}) {
  const { setNodeRef } = useDroppable({ id: column.id });
  const columnBookings = bookings.filter((booking) => booking.status === column.id);

  return (
    <div ref={setNodeRef} className={`rounded-lg border-2 border-dashed p-4 min-h-[600px] ${column.color}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-lg">{column.title}</h3>
        <Badge variant="outline" className="bg-white">
          {columnBookings.length}
        </Badge>
      </div>

      <SortableContext items={columnBookings.map((b) => b.id)} strategy={verticalListSortingStrategy}>
        <div className="space-y-3">
          {columnBookings.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <p className="text-sm">No {column.title.toLowerCase()} bookings</p>
              <p className="text-xs">Connect to backend to load real data</p>
            </div>
          ) : (
            columnBookings.map((booking) => <BookingCard key={booking.id} booking={booking}/>)
          )}
        </div>
      </SortableContext>
    </div>
  );
}