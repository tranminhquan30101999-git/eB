#!/usr/bin/env python3
"""
Create test appointments for demonstration purposes
"""

from datetime import date, timedelta
from app.database.config import SessionLocal
from app.services import crud
from app.models.models import Service, TimeSlot

def create_test_appointments():
    """Create some test appointments for the demo"""
    db = SessionLocal()
    
    try:
        # Get available services
        services = crud.get_services(db)
        if not services:
            print("No services found. Please run init_data.py first.")
            return
        
        # Get today's time slots
        today = date.today()
        slots = crud.get_available_slots(db, today)
        
        if not slots:
            print("No time slots found for today. Generating slots...")
            crud.generate_time_slots(db, today)
            slots = crud.get_available_slots(db, today)
        
        if len(slots) < 3:
            print("Not enough available slots for demo. Need at least 3 slots.")
            return
        
        # Create test appointments
        test_appointments = [
            {
                "customer_name": "Nguyễn Văn A",
                "customer_phone": "0901234567",
                "customer_email": "nguyenvana@example.com",
                "service_id": services[0].id,  # First service
                "time_slot_id": slots[0].id,   # First available slot
                "notes": "Khách hàng VIP, cần dịch vụ tốt nhất",
                "status": "scheduled"
            },
            {
                "customer_name": "Trần Thị B",
                "customer_phone": "0902345678",
                "customer_email": "tranthib@example.com",
                "service_id": services[1].id if len(services) > 1 else services[0].id,
                "time_slot_id": slots[1].id,
                "notes": "Làn da nhạy cảm, cần chú ý",
                "status": "checked-in"
            },
            {
                "customer_name": "Lê Văn C",
                "customer_phone": "0903456789",
                "service_id": services[2].id if len(services) > 2 else services[0].id,
                "time_slot_id": slots[2].id,
                "status": "serving"
            }
        ]
        
        created_count = 0
        for appointment_data in test_appointments:
            try:
                appointment = crud.create_appointment(db, appointment_data)
                created_count += 1
                print(f"✓ Created appointment for {appointment.customer_name}")
            except Exception as e:
                print(f"✗ Failed to create appointment for {appointment_data['customer_name']}: {e}")
        
        print(f"\nCreated {created_count} test appointments successfully!")
        print(f"You can now view them in the admin dashboard at: http://localhost:3000/dashboard/booking")
        
    except Exception as e:
        print(f"Error creating test appointments: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_appointments()