from app.models.models import Appointment, TimeSlot
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date, datetime
from app.database.config import get_db
from app.schemas.schemas import AppointmentCreate, ServiceCreate, ServiceResponse, TimeSlotResponse, AppointmentResponse
from app.services import crud

router = APIRouter()

@router.post("/services", response_model=ServiceResponse)
def create_service(service: ServiceCreate, db: Session = Depends(get_db)):
    """Create a new nail service"""
    return crud.create_service(db, service)

@router.get("/services", response_model=List[ServiceResponse])
def list_services(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all available services"""
    return crud.get_services(db, skip=skip, limit=limit)

@router.get("/timeslots/{date}", response_model=List[TimeSlotResponse])
def get_slots_by_date(date: date, db: Session = Depends(get_db)):
    """Get available time slots for a specific date"""
    slots = crud.get_available_slots(db, date)
    if not slots:
        # Generate slots if they don't exist
        crud.generate_time_slots(db, date)
        slots = crud.get_available_slots(db, date)
    return slots

@router.post("/timeslots/generate/{date}")
def generate_slots(date: date, db: Session = Depends(get_db)):
    """Generate time slots for a specific date"""
    slots = crud.generate_time_slots(db, date)
    return {"message": f"Generated {len(slots)} time slots for {date}"}

@router.get("/appointments/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(appointment_id: int, db: Session = Depends(get_db)):
    """Get appointment details by ID"""
    appointment = crud.get_appointment(db, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment

@router.get("/appointments/phone/{phone}", response_model=List[AppointmentResponse])
def get_appointments_by_phone(phone: str, db: Session = Depends(get_db)):
    """Get all appointments for a customer by phone number"""
    return crud.get_appointments_by_phone(db, phone)

@router.get("/appointments", response_model=List[AppointmentResponse])
def get_all_appointments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all appointments"""
    return crud.get_all_appointments(db, skip=skip, limit=limit)

@router.patch("/appointments/{appointment_id}/status")
def update_appointment_status(
    appointment_id: int, 
    status_update: dict,
    db: Session = Depends(get_db)
):
    """Update appointment status"""
    appointment = crud.get_appointment(db, appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    new_status = status_update.get("status")
    if new_status not in ["scheduled", "checked-in", "serving", "completed", "cancelled"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    updated_appointment = crud.update_appointment_status(db, appointment_id, new_status)
    return {"message": "Status updated successfully", "appointment": updated_appointment}

@router.post("/appointments", response_model=AppointmentResponse)
def create_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db)):
    try:
        # Validate that the service exists
        service = crud.get_service(db, appointment.service_id)
        if not service:
            raise HTTPException(status_code=400, detail="Dịch vụ không tồn tại")
        
        # Validate that the time slot exists and is available
        time_slot = crud.get_time_slot(db, appointment.time_slot_id)
        if not time_slot:
            raise HTTPException(status_code=400, detail="Thời gian đã chọn không tồn tại")
        
        if not time_slot.is_available:
            raise HTTPException(status_code=400, detail="Thời gian đã chọn không còn trống. Vui lòng chọn thời gian khác")
        
        # Create appointment data
        appointment_data = {
            "customer_name": appointment.customer_name,
            "customer_phone": appointment.customer_phone,
            "service_id": appointment.service_id,
            "time_slot_id": appointment.time_slot_id,
            "notes": appointment.notes,
            "status": "scheduled"
        }
        
        # Create the appointment
        db_appointment = crud.create_appointment(db, appointment_data)
        
        return db_appointment
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {str(e)}")    
    
@router.get("/dashboard/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    total_bookings = db.query(Appointment).count()

    total_completed = db.query(Appointment).filter(Appointment.status == "completed").count()
    total_cancelled = db.query(Appointment).filter(Appointment.status == "cancelled").count()

    # Tính Completion Rate
    completion_rate = (total_completed / total_bookings * 100) if total_bookings > 0 else 0

    # Tính Cancellation Rate
    cancellation_rate = (total_cancelled / total_bookings * 100) if total_bookings > 0 else 0

    # Today's Bookings
    today = date.today()
    todays_bookings = db.query(Appointment).join(TimeSlot).filter(
        TimeSlot.start_time >= datetime.combine(today, datetime.min.time()),
        TimeSlot.start_time <= datetime.combine(today, datetime.max.time())
    ).count()

    return {
        "totalBookings": total_bookings,
        "completionRate": completion_rate,
        "todaysBookings": todays_bookings,
        "cancellationRate": cancellation_rate
    }
    
    
@router.get("/dashboard/recent-bookings")
def get_recent_bookings(db: Session = Depends(get_db), limit: int = 5):
    recent_appointments = (
        db.query(Appointment)
        .order_by(Appointment.created_at.desc())
        .limit(limit)
        .all()
    )

    result = []
    for appt in recent_appointments:
        result.append({
            "id": appt.id,
            "customer_name": appt.customer_name,
            "service": {
                "name": appt.service.name
            },
            "time_slot": {
                "start_time": appt.time_slot.start_time.strftime("%H:%M")
            },
            "status": appt.status
        })
    return result