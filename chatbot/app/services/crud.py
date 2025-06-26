from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import date, time, datetime, timedelta
from typing import List, Optional
from app.models.models import Service, TimeSlot, Appointment, KnowledgeDocument, DocumentChunk, AdminUser, BookingAnalytics
from app.schemas.schemas import ServiceCreate, AppointmentCreate, TimeSlotCreate, KnowledgeDocumentCreate, KnowledgeDocumentUpdate

# Service CRUD
def get_services(db: Session, skip: int = 0, limit: int = 100) -> List[Service]:
    return db.query(Service).filter(Service.is_active == True).offset(skip).limit(limit).all()

def get_service(db: Session, service_id: int) -> Optional[Service]:
    return db.query(Service).filter(Service.id == service_id).first()

def create_service(db: Session, service: ServiceCreate) -> Service:
    db_service = Service(**service.dict())
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service

# TimeSlot CRUD
def get_available_slots(db: Session, date: date) -> List[TimeSlot]:
    return db.query(TimeSlot).filter(
        and_(
            TimeSlot.date == date,
            TimeSlot.is_available == True
        )
    ).all()
    
def get_slots(db: Session) -> List[TimeSlot]:
    return db.query(TimeSlot).filter(
        and_(
            TimeSlot.is_available == True
        )
    ).all()
    
def get_time_slot(db: Session, slot_id: int) -> Optional[TimeSlot]:
    return db.query(TimeSlot).filter(TimeSlot.id == slot_id).first()

def create_time_slot(db: Session, time_slot: TimeSlotCreate) -> TimeSlot:
    db_slot = TimeSlot(**time_slot.dict())
    db.add(db_slot)
    db.commit()
    db.refresh(db_slot)
    return db_slot

def update_slot_availability(db: Session, slot_id: int, is_available: bool):
    db_slot = db.query(TimeSlot).filter(TimeSlot.id == slot_id).first()
    if db_slot:
        db_slot.is_available = is_available
        db.commit()
        db.refresh(db_slot)
    return db_slot

# Appointment CRUD
def create_appointment(db: Session, appointment: dict) -> Appointment:
    db_appointment = Appointment(**appointment)
    db.add(db_appointment)
    
    # Mark the time slot as unavailable
    update_slot_availability(db, appointment["time_slot_id"], False)
    
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

def get_appointment(db: Session, appointment_id: int) -> Optional[Appointment]:
    return db.query(Appointment).filter(Appointment.id == appointment_id).first()

def get_appointments_by_phone(db: Session, phone: str) -> List[Appointment]:
    return db.query(Appointment).filter(
        and_(
            Appointment.customer_phone == phone,
            Appointment.status != "cancelled"
        )
    ).all()

def cancel_appointment(db: Session, appointment_id: int) -> Optional[Appointment]:
    db_appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if db_appointment:
        db_appointment.status = "cancelled"
        # Make the time slot available again
        update_slot_availability(db, db_appointment.time_slot_id, True)
        db.commit()
        db.refresh(db_appointment)
    return db_appointment

def get_all_appointments(db: Session, skip: int = 0, limit: int = 100) -> List[Appointment]:
    """Get all appointments with pagination"""
    return db.query(Appointment).offset(skip).limit(limit).all()

def update_appointment_status(db: Session, appointment_id: int, new_status: str) -> Optional[Appointment]:
    """Update appointment status"""
    db_appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if db_appointment:
        old_status = db_appointment.status
        db_appointment.status = new_status
        db_appointment.updated_at = datetime.utcnow()
        
        # Handle time slot availability based on status change
        if old_status != "cancelled" and new_status == "cancelled":
            # Make slot available when cancelling
            update_slot_availability(db, db_appointment.time_slot_id, True)
        elif old_status == "cancelled" and new_status != "cancelled":
            # Make slot unavailable when uncancelling
            update_slot_availability(db, db_appointment.time_slot_id, False)
        
        db.commit()
        db.refresh(db_appointment)
    return db_appointment

def generate_time_slots(db: Session, date: date, start_hour: int = 9, end_hour: int = 18, slot_duration_minutes: int = 60):
    """Generate time slots for a given date"""
    current_time = datetime.combine(date, time(hour=start_hour))
    end_time = datetime.combine(date, time(hour=end_hour))
    
    slots = []
    while current_time < end_time:
        slot_end = current_time + timedelta(minutes=slot_duration_minutes)
        if slot_end <= end_time:
            slot = TimeSlot(
                date=date,
                start_time=current_time.time(),
                end_time=slot_end.time(),
                is_available=True
            )
            db.add(slot)
            slots.append(slot)
        current_time = slot_end
    
    db.commit()
    return slots

# Knowledge Base CRUD
def create_knowledge_document(db: Session, document: KnowledgeDocumentCreate) -> KnowledgeDocument:
    """Create a new knowledge document"""
    db_document = KnowledgeDocument(**document.dict())
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

def get_knowledge_documents(db: Session, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> List[KnowledgeDocument]:
    """Get knowledge documents with optional search"""
    query = db.query(KnowledgeDocument).filter(KnowledgeDocument.is_active == True)
    
    if search:
        search_filter = or_(
            KnowledgeDocument.title.ilike(f"%{search}%"),
            KnowledgeDocument.content.ilike(f"%{search}%"),
            KnowledgeDocument.tags.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    return query.offset(skip).limit(limit).all()

def get_knowledge_document(db: Session, document_id: int) -> Optional[KnowledgeDocument]:
    """Get a knowledge document by ID"""
    return db.query(KnowledgeDocument).filter(
        and_(
            KnowledgeDocument.id == document_id,
            KnowledgeDocument.is_active == True
        )
    ).first()

def update_knowledge_document(db: Session, document_id: int, update_data: KnowledgeDocumentUpdate) -> Optional[KnowledgeDocument]:
    """Update a knowledge document"""
    db_document = get_knowledge_document(db, document_id)
    if not db_document:
        return None
    
    update_dict = update_data.dict(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(db_document, field, value)
    
    db_document.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_document)
    return db_document

def delete_knowledge_document(db: Session, document_id: int) -> bool:
    """Soft delete a knowledge document"""
    db_document = get_knowledge_document(db, document_id)
    if not db_document:
        return False
    
    db_document.is_active = False
    db_document.updated_at = datetime.utcnow()
    db.commit()
    return True

def search_knowledge_content(db: Session, query: str, limit: int = 5) -> List[DocumentChunk]:
    """Search document chunks for relevant content"""
    return db.query(DocumentChunk).join(KnowledgeDocument).filter(
        and_(
            KnowledgeDocument.is_active == True,
            KnowledgeDocument.status == "ready",
            DocumentChunk.content.ilike(f"%{query}%")
        )
    ).limit(limit).all()

def create_document_chunks(db: Session, document_id: int, chunks: List[str]) -> List[DocumentChunk]:
    """Create document chunks for a document"""
    db_chunks = []
    for i, chunk_content in enumerate(chunks):
        chunk = DocumentChunk(
            document_id=document_id,
            content=chunk_content,
            chunk_index=i,
            tokens=len(chunk_content.split())  # Simple token count
        )
        db.add(chunk)
        db_chunks.append(chunk)
    
    db.commit()
    for chunk in db_chunks:
        db.refresh(chunk)
    return db_chunks

# Analytics CRUD
def get_booking_analytics(db: Session, start_date: date, end_date: date) -> List[BookingAnalytics]:
    """Get booking analytics for a date range"""
    return db.query(BookingAnalytics).filter(
        and_(
            BookingAnalytics.date >= start_date,
            BookingAnalytics.date <= end_date
        )
    ).all()

def update_daily_analytics(db: Session, target_date: date = None) -> BookingAnalytics:
    """Update analytics for a specific date"""
    if target_date is None:
        target_date = date.today()
    
    # Calculate analytics from appointments
    appointments = db.query(Appointment).join(TimeSlot).filter(
        TimeSlot.date == target_date
    ).all()
    
    total_bookings = len(appointments)
    completed_bookings = len([a for a in appointments if a.status == "completed"])
    cancelled_bookings = len([a for a in appointments if a.status == "cancelled"])
    
    total_revenue = sum([a.service.price for a in appointments if a.status == "completed"])
    avg_duration = sum([a.service.duration_minutes for a in appointments]) / total_bookings if total_bookings > 0 else 0
    
    # Update or create analytics record
    analytics = db.query(BookingAnalytics).filter(BookingAnalytics.date == target_date).first()
    if analytics:
        analytics.total_bookings = total_bookings
        analytics.completed_bookings = completed_bookings
        analytics.cancelled_bookings = cancelled_bookings
        analytics.total_revenue = total_revenue
        analytics.avg_service_duration = avg_duration
    else:
        analytics = BookingAnalytics(
            date=target_date,
            total_bookings=total_bookings,
            completed_bookings=completed_bookings,
            cancelled_bookings=cancelled_bookings,
            total_revenue=total_revenue,
            avg_service_duration=avg_duration
        )
        db.add(analytics)
    
    db.commit()
    db.refresh(analytics)
    return analytics