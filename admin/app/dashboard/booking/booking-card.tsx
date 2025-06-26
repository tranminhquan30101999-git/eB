import { useState, useEffect } from "react";
import {
  DndContext,
  DragEndEvent,
  DragStartEvent,
  DragOverlay,
  pointerWithin,
} from "@dnd-kit/core";
import { SortableContext, verticalListSortingStrategy } from "@dnd-kit/sortable";
import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { Card, CardHeader, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { Clock, MoreVertical, Edit, X, Phone, Calendar, RefreshCw, Plus, Layout, List } from "lucide-react";
import { useDroppable } from "@dnd-kit/core";
import { Booking, BookingStatus } from "./type/booking-status";



function BookingCard({booking}: { booking: Booking}) {
    const {
      attributes,
      listeners,
      setNodeRef,
      transform,
      transition,
      isDragging,
    } = useSortable({ id: booking.id });
  
    const style = {
      transform: CSS.Transform.toString(transform),
      transition,
      opacity: isDragging ? 0.3 : 1,
      zIndex: isDragging ? 50 : 1,
    };
  
    const initials = booking.customer_name
      .split(" ")
      .map((name) => name[0])
      .join("")
      .toUpperCase();

    const allStatuses: BookingStatus[] = ["scheduled", "checked-in", "serving", "completed", "cancelled"];
    const availableStatuses = allStatuses.filter(status => status !== booking.status);
  
    const getServiceColor = (serviceName: string): string => {
        const colors = {
        "Làm móng gel": "bg-purple-100 text-purple-800",
        "Làm móng gel kèm vẽ": "bg-pink-100 text-pink-800",
        "Sơn móng thường": "bg-blue-100 text-blue-800",
        "Cắt và dũa móng": "bg-green-100 text-green-800",
        "Làm móng đính đá": "bg-yellow-100 text-yellow-800",
        "Tẩy và làm lại móng": "bg-indigo-100 text-indigo-800",
        };
        return colors[serviceName as keyof typeof colors] || "bg-gray-100 text-gray-800";
    };
    return (
      <Card
        ref={setNodeRef}
        style={style}
        {...attributes}
        {...listeners}
        className={`cursor-grab active:cursor-grabbing ${isDragging ? "shadow-xl scale-105" : ""}`}
      >
        <CardContent className="p-4">
          <div className="flex items-start justify-between mb-3">
            <div className="flex items-center gap-3">
              <Avatar className="h-8 w-8">
                <AvatarFallback className="text-xs">{initials}</AvatarFallback>
              </Avatar>
              <div>
                <p className="font-medium text-sm">{booking.customer_name}</p>
                <p className="text-xs text-muted-foreground flex items-center gap-1">
                  <Phone className="h-3 w-3" />
                  {booking.customer_phone}
                </p>
              </div>
            </div>
            {/* <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="sm" className="h-6 w-6 p-0">
                  <MoreVertical className="h-3 w-3" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                {availableStatuses.map(status => (
                    <DropdownMenuItem
                        key={status}
                        onClick={() => onStatusChange(booking.id, status)}
                    >
                        {status.charAt(0).toUpperCase() + status.slice(1)}
                    </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu> */}
          </div>
  
          <div className="space-y-2">
            <Badge className={getServiceColor(booking.service.name)} variant="secondary">
              {booking.service.name}
            </Badge>
            <div className="flex items-center gap-4 text-xs text-muted-foreground">
              <div className="flex items-center gap-1">
                <Calendar className="h-3 w-3" />
                {new Date(booking.time_slot.date).toLocaleDateString()} {booking.time_slot.start_time}
              </div>
              <div className="flex items-center gap-1">
                <Clock className="h-3 w-3" />
                {booking.service.duration_minutes}min
              </div>
            </div>
            {booking.notes && (
              <p className="text-xs text-gray-600 mt-1">{booking.notes}</p>
            )}
          </div>
        </CardContent>
      </Card>
    );
}
export default BookingCard;