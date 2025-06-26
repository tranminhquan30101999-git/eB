"use client";

import { useState, useEffect } from "react";
import {
  DndContext,
  DragEndEvent,
  DragStartEvent,
  DragOverlay,
  pointerWithin,
} from "@dnd-kit/core";
import { SortableContext, verticalListSortingStrategy } from "@dnd-kit/sortable";
import { useDroppable } from "@dnd-kit/core";
import { Card, CardHeader, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { RefreshCw, Plus, Layout, List } from "lucide-react";
import BookingCard from "./booking-card";
import BookingTable from "./booking-table";
import { Booking, BookingStatus, Service, TimeSlot } from "./type/booking-status";
import DroppableColumn from "./droppable-column";
import BookingFormModal from "./booking-form-modal";

// Constants
const API_BASE_URL = "http://localhost:8080/api/v1";

const columns: { id: BookingStatus; title: string; color: string }[] = [
  { id: "scheduled", title: "Scheduled", color: "bg-blue-50 border-blue-200" },
  { id: "checked-in", title: "Checked In", color: "bg-yellow-50 border-yellow-200" },
  { id: "serving", title: "Serving", color: "bg-green-50 border-green-200" },
  { id: "completed", title: "Completed", color: "bg-gray-50 border-gray-200" },
  { id: "cancelled", title: "Cancelled", color: "bg-red-50 border-red-200" },
];



export default function BookingPage() {
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [activeBooking, setActiveBooking] = useState<Booking | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string>("");
  const [services, setServices] = useState<Service[]>([]);
  const [viewMode, setViewMode] = useState<"kanban" | "list">("kanban");
  const [isMobile, setIsMobile] = useState(false);

  // Responsive check
  useEffect(() => {
    const checkScreenSize = () => {
      setIsMobile(window.innerWidth < 768); // Tailwind md breakpoint
    };
    checkScreenSize();
    window.addEventListener("resize", checkScreenSize);
    return () => window.removeEventListener("resize", checkScreenSize);
  }, []);

  // Nếu mobile => luôn về list mode
  useEffect(() => {
    if (isMobile) setViewMode("list");
  }, [isMobile]);

  const fetchBookings = async () => {
    try {
      setIsLoading(true);
      setError("");

      const servicesResponse = await fetch(`${API_BASE_URL}/admin/services`);
      if (!servicesResponse.ok) throw new Error("Failed to fetch services");
      const servicesData = await servicesResponse.json();
      setServices(servicesData);

      const bookingsResponse = await fetch(`${API_BASE_URL}/admin/appointments`);
      if (!bookingsResponse.ok) throw new Error("Failed to fetch bookings");
      const bookingsData = await bookingsResponse.json();
      setBookings(bookingsData);
    } catch (err: any) {
      console.error("Error fetching data:", err);
      setError(err.message || "Failed to connect to backend");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchBookings();
  }, []);

  const handleDragStart = (event: DragStartEvent) => {
    const booking = bookings.find((b) => b.id === Number(event.active.id));
    setActiveBooking(booking || null);
  };

  const updateBookingStatus = async (bookingId: number, newStatus: BookingStatus) => {
    try {
      const response = await fetch(`${API_BASE_URL}/admin/appointments/${bookingId}/status`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: newStatus }),
      });
      if (!response.ok) throw new Error("Failed to update booking status");

      setBookings((prev) => prev.map((b) => (b.id === bookingId ? { ...b, status: newStatus } : b)));
    } catch (err) {
      console.error("Error updating booking:", err);
      await fetchBookings();
    }
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    setActiveBooking(null);
    if (!over) return;

    const activeBooking = bookings.find((b) => b.id === Number(active.id));
    if (!activeBooking) return;

    const newStatus = over.id as BookingStatus;
    if (newStatus !== activeBooking.status) {
      setBookings((prev) =>
        prev.map((b) => (b.id === activeBooking.id ? { ...b, status: newStatus } : b))
      );
      updateBookingStatus(activeBooking.id, newStatus);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Booking Board</h1>
          <p className="text-muted-foreground">Manage customer bookings with drag and drop</p>
          {!isLoading && services.length > 0 && (
            <p className="text-sm text-green-600 mt-1">
              ✓ Connected to backend ({services.length} services available)
            </p>
          )}
        </div>

        <div className="flex flex-wrap gap-2">
          <Button variant="outline" onClick={fetchBookings} disabled={isLoading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? "animate-spin" : ""}`} />
            {isLoading ? "Loading..." : "Refresh"}
          </Button>

          {!isMobile && (
            <Button
              variant="outline"
              onClick={() => setViewMode(viewMode === "kanban" ? "list" : "kanban")}
            >
              {viewMode === "kanban" ? (
                <>
                  <List className="h-4 w-4 mr-2" />
                  List View
                </>
              ) : (
                <>
                  <Layout className="h-4 w-4 mr-2" />
                  Kanban View
                </>
              )}
            </Button>
          )}

        <BookingFormModal services={services}  onBookingAdded={fetchBookings} />


        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
          {columns.map((column) => (
            <Card key={column.id} className={`min-h-[400px] ${column.color}`}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold text-lg">{column.title}</h3>
                  <Badge variant="outline" className="bg-white">0</Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-gray-900 mx-auto"></div>
                  <p className="mt-2 text-sm text-gray-600">Loading...</p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (viewMode === "kanban" && !isMobile) ? (
        <DndContext onDragStart={handleDragStart} onDragEnd={handleDragEnd} collisionDetection={pointerWithin}>
          <div className="flex overflow-x-auto gap-4 pb-4">
            {columns.map((column) => (
              <div key={column.id} className="min-w-[280px] md:min-w-0 flex-1">
                <DroppableColumn column={column} bookings={bookings}/>
              </div>
            ))}
          </div>
          <DragOverlay>{activeBooking && <BookingCard booking={activeBooking}/>}</DragOverlay>
        </DndContext>
      ) : (
        <div className="space-y-3">
          <BookingTable 
            bookings={bookings} 
            onStatusChange={(bookingId, newStatus) => updateBookingStatus(bookingId, newStatus)}
          />
        </div>
      )}


    </div>


  );
}
