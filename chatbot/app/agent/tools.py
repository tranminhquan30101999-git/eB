from langchain_core.tools import tool
from typing import List, Dict, Any
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from app.services import crud
from app.database.config import SessionLocal
import json

@tool
def get_available_services() -> str:
    """Get list of all available nail services with their details including price and duration."""
    db = SessionLocal()
    try:
        services = crud.get_services(db)
        result = []
        for service in services:
            result.append({
                "id": service.id,
                "name": service.name,
                "description": service.description,
                "duration_minutes": service.duration_minutes,
                "price": service.price
            })
        return json.dumps(result, ensure_ascii=False)
    finally:
        db.close()

@tool
def check_available_slots(date_str: str) -> str:
    """Check available time slots for a specific date. Date should be in YYYY-MM-DD format."""
    db = SessionLocal()
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        
        # Generate slots if they don't exist for this date
        existing_slots = crud.get_available_slots(db, target_date)
        if not existing_slots:
            crud.generate_time_slots(db, target_date)
        
        slots = crud.get_available_slots(db, target_date)
        result = []
        for slot in slots:
            result.append({
                "id": slot.id,
                "date": slot.date.isoformat(),
                "start_time": slot.start_time.strftime("%H:%M"),
                "end_time": slot.end_time.strftime("%H:%M")
            })
        return json.dumps(result, ensure_ascii=False)
    except ValueError:
        return "Invalid date format. Please use YYYY-MM-DD format."
    finally:
        db.close()

@tool
def book_appointment(customer_name: str, customer_phone: str, service_id: int, 
                    time_slot_id: int, customer_email: str = None, notes: str = None) -> str:
    """Book an appointment for a customer with specified service and time slot."""
    db = SessionLocal()
    try:
        # Verify service exists
        service = crud.get_service(db, service_id)
        if not service:
            return f"Service with ID {service_id} not found."
        
        # Verify time slot exists and is available
        slot = crud.get_time_slot(db, time_slot_id)
        if not slot:
            return f"Time slot with ID {time_slot_id} not found."
        if not slot.is_available:
            return "This time slot is no longer available."
        
        # Create appointment
        appointment_data = {
            "customer_name": customer_name,
            "customer_phone": customer_phone,
            "customer_email": customer_email,
            "service_id": service_id,
            "time_slot_id": time_slot_id,
            "notes": notes
        }
        
        appointment = crud.create_appointment(db, appointment_data)
        
        return f"Appointment booked successfully! Appointment ID: #{appointment.id}. " \
               f"Service: {service.name} on {slot.date} from {slot.start_time.strftime('%H:%M')} to {slot.end_time.strftime('%H:%M')}."
    except Exception as e:
        return f"Error booking appointment: {str(e)}"
    finally:
        db.close()

@tool
def check_customer_appointments(customer_phone: str) -> str:
    """Check existing appointments for a customer by phone number."""
    db = SessionLocal()
    try:
        appointments = crud.get_appointments_by_phone(db, customer_phone)
        if not appointments:
            return "No appointments found for this phone number."
        
        result = []
        for apt in appointments:
            result.append({
                "id": apt.id,
                "service": apt.service.name,
                "date": apt.time_slot.date.isoformat(),
                "start_time": apt.time_slot.start_time.strftime("%H:%M"),
                "end_time": apt.time_slot.end_time.strftime("%H:%M"),
                "status": apt.status
            })
        return json.dumps(result, ensure_ascii=False)
    finally:
        db.close()

@tool
def cancel_appointment(appointment_id: int) -> str:
    """Cancel an existing appointment by appointment ID."""
    db = SessionLocal()
    try:
        appointment = crud.cancel_appointment(db, appointment_id)
        if appointment:
            return f"Appointment {appointment_id} has been cancelled successfully."
        else:
            return f"Appointment with ID {appointment_id} not found."
    finally:
        db.close()

@tool
def search_knowledge_base(query: str) -> str:
    """Search the knowledge base for information about nail services, procedures, policies, or general questions."""
    db = SessionLocal()
    try:
        if not query.strip():
            return "Please provide a search query."
        
        # Search for relevant content in the knowledge base
        chunks = crud.search_knowledge_content(db, query, limit=3)
        
        if not chunks:
            return "Tôi không tìm thấy thông tin liên quan trong cơ sở dữ liệu. Bạn có thể hỏi về các dịch vụ làm nail, đặt lịch, hoặc kiểm tra lịch hẹn."
        
        # Format the results
        result_text = "Dựa trên thông tin trong cơ sở dữ liệu:\n\n"
        
        for i, chunk in enumerate(chunks, 1):
            result_text += f"{i}. Từ tài liệu '{chunk.document.title}':\n"
            result_text += f"{chunk.content[:500]}...\n\n"
        
        return result_text
        
    except Exception as e:
        return f"Lỗi khi tìm kiếm thông tin: {str(e)}"
    finally:
        db.close()
# List of all available tools
nail_salon_tools = [
    get_available_services,
    check_available_slots,
    book_appointment,
    check_customer_appointments,
    cancel_appointment,
    search_knowledge_base,
]