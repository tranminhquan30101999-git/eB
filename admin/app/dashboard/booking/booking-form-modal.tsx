import { useState, useEffect } from "react";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue
} from "@/components/ui/select";
import { Calendar } from "@/components/ui/calendar";
import { format } from "date-fns";
import { TimeSlot } from "./type/booking-status";
import { DatePicker } from "@/components/ui/datepicker";

type Service = { id: number; name: string };

type BookingFormModalProps = {
  services: Service[];
  onBookingAdded: () => void;
};

export default function BookingFormModal({ services, onBookingAdded }: BookingFormModalProps) {
  const [open, setOpen] = useState(false);
  const [selectedDate, setSelectedDate] = useState<Date | undefined>(undefined);
  const [timeSlots, setTimeSlots] = useState<TimeSlot[]>([]);
  const [formData, setFormData] = useState({
    customer_name: "",
    customer_phone: "",
    customer_email: "email@gamil.com",
    service_id: 0,
    time_slot_id: 0,
    notes: ""
  });
  const API_BASE_URL = "http://localhost:8080/api/v1";

  useEffect(() => {
    if (selectedDate) {
      fetchTimeSlotsByDate(selectedDate);
    }
  }, [selectedDate]);

  const fetchTimeSlotsByDate = async (date: Date) => {
    const dateStr = format(date, "yyyy-MM-dd");

    const response = await fetch(`${API_BASE_URL}/admin/timeslots/${dateStr}`);
    const data = await response.json();
    setTimeSlots(data);
  };

  const handleChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async () => {
    const payload = {
      customer_name: formData.customer_name,
      customer_phone: formData.customer_phone,
      customer_email: formData.customer_email,
      service_id: formData.service_id,
      time_slot_id: formData.time_slot_id,
      notes: formData.notes
    };

    const response = await fetch(`${API_BASE_URL}/admin/appointments`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (response.ok) {
      setOpen(false);
      onBookingAdded();
    } else {
      console.error("Failed to create booking");
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="default">Add New Booking</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>New Booking</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          <Input
            placeholder="Customer Name"
            value={formData.customer_name}
            onChange={(e) => handleChange("customer_name", e.target.value)}
          />
          <Input
            placeholder="Phone"
            value={formData.customer_phone}
            onChange={(e) => handleChange("customer_phone", e.target.value)}
          />
          <Select onValueChange={(val) => handleChange("service_id", parseInt(val))} >
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Select Service" />
            </SelectTrigger>
            <SelectContent>
              {services.map((service) => (
                <SelectItem key={service.id} value={service.id.toString()}>
                  {service.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <div>
            <p className="mb-1 text-sm">Select Date</p>
            <DatePicker date={selectedDate} setDate={setSelectedDate} />
          </div>

          <Select onValueChange={(val) => handleChange("time_slot_id", parseInt(val))} disabled={!selectedDate}>
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Select Time Slot" />
            </SelectTrigger>
            <SelectContent>
              {timeSlots.filter(ts => ts.is_available).map((slot) => (
                <SelectItem key={slot.id} value={slot.id.toString()}>
                  {slot.start_time} - {slot.end_time}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Textarea
            placeholder="Notes"
            value={formData.notes}
            onChange={(e) => handleChange("notes", e.target.value)}
          />

          <Button onClick={handleSubmit} className="w-full">
            Submit
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
