from pydantic import BaseModel, EmailStr
from datetime import datetime, date, time
from typing import Optional, List

# Service schemas
class ServiceBase(BaseModel):
    name: str
    description: Optional[str] = None
    duration_minutes: int
    price: float

class ServiceCreate(ServiceBase):
    pass

class ServiceResponse(ServiceBase):
    id: int
    is_active: bool
    
    class Config:
        from_attributes = True

# TimeSlot schemas
class TimeSlotBase(BaseModel):
    date: date
    start_time: time
    end_time: time

class TimeSlotCreate(TimeSlotBase):
    pass

class TimeSlotResponse(TimeSlotBase):
    id: int
    is_available: bool
    
    class Config:
        from_attributes = True

# Appointment schemas
class AppointmentBase(BaseModel):
    customer_name: str
    customer_phone: str
    customer_email: Optional[EmailStr] = None
    service_id: int
    time_slot_id: int
    notes: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(BaseModel):
    status: str

class AppointmentResponse(AppointmentBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    service: ServiceResponse
    time_slot: TimeSlotResponse
    
    class Config:
        from_attributes = True

# Chat schemas
class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str

# Knowledge Base schemas
class KnowledgeDocumentBase(BaseModel):
    title: str
    file_name: str
    file_type: str
    tags: Optional[str] = None

class KnowledgeDocumentCreate(KnowledgeDocumentBase):
    file_size: int
    file_path: str
    content: Optional[str] = None

class KnowledgeDocumentUpdate(BaseModel):
    title: Optional[str] = None
    tags: Optional[str] = None
    status: Optional[str] = None
    content: Optional[str] = None
    error_message: Optional[str] = None

class KnowledgeDocumentResponse(KnowledgeDocumentBase):
    id: int
    file_size: int
    status: str
    error_message: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class DocumentChunkResponse(BaseModel):
    id: int
    content: str
    chunk_index: int
    tokens: Optional[int] = None
    
    class Config:
        from_attributes = True

# Admin User schemas
class AdminUserBase(BaseModel):
    username: str
    email: EmailStr

class AdminUserCreate(AdminUserBase):
    password: str

class AdminUserResponse(AdminUserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Analytics schemas
class BookingAnalyticsResponse(BaseModel):
    date: date
    total_bookings: int
    completed_bookings: int
    cancelled_bookings: int
    total_revenue: float
    avg_service_duration: float
    
    class Config:
        from_attributes = True

# File Upload schemas
class FileUploadResponse(BaseModel):
    success: bool
    message: str
    document_id: Optional[int] = None
    filename: str