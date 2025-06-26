export interface Booking {
    id: number;
    customer_name: string;
    customer_phone: string;
    customer_email?: string;
    service: {
      id: number;
      name: string;
      duration_minutes: number;
      price: number;
    };
    time_slot: {
      id: number;
      date: string;
      start_time: string;
      end_time: string;
    };
    status: BookingStatus;
    notes?: string;
    created_at: string;
    updated_at: string;
  }
export type BookingStatus = "scheduled" | "checked-in" | "serving" | "completed" | "cancelled";

export interface Service {
  id: number;
  name: string;
  description?: string;
  duration_minutes: number;
  price: number;
  is_active: boolean;
}

export interface TimeSlot {
    id: number;
    date: string;
    start_time: string;
    end_time: string;
    is_available: boolean;

}