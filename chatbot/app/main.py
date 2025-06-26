from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from app.api import chat, admin, knowledge
from app.database.config import engine
from app.models.models import Base
import os

# Create database tables
Base.metadata.create_all(bind=engine)

# Set up templates
# templates = Jinja2Templates(directory="app/templates")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting nail salon chatbot API...")
    yield
    # Shutdown
    print("Shutting down...")

app = FastAPI(
    title="Nail Salon Chatbot API",
    description="API for nail salon appointment scheduling chatbot",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Frontend route
@app.get("/chat", response_class=HTMLResponse)
async def chat_frontend(request: Request):
    """Serve the chat frontend interface"""
    # Get the base URL dynamically
    base_url = f"{request.url.scheme}://{request.url.netloc}"
    
    return templates.TemplateResponse("chat.html", {
        "request": request,
        "title": "Nail Salon Chatbot",
        "header_title": "Nail Salon Chatbot",
        "header_subtitle": "Xin chào! Tôi có thể giúp bạn đặt lịch làm nail",
        "welcome_message": """Chào bạn! Tôi là trợ lý ảo của tiệm nail. 
<br><br>Vui lòng chọn một trong các tùy chọn bên dưới hoặc nhập tin nhắn để bắt đầu:""",
        "input_placeholder": "Nhập tin nhắn...",
        "send_button_text": "Gửi",
        "api_url": f"{base_url}/api/v1"
    })

# Include routers
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(knowledge.router, prefix="/api/v1/knowledge", tags=["knowledge"])

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Nail Salon Chatbot API",
        "frontend": "/chat",
        "endpoints": {
            "chat_api": "/api/v1/chat",
            "services": "/api/v1/admin/services",
            "timeslots": "/api/v1/admin/timeslots/{date}",
            "appointments": "/api/v1/admin/appointments",
            "appointment_by_id": "/api/v1/admin/appointments/{id}",
            "appointment_status": "/api/v1/admin/appointments/{id}/status",
            "knowledge_documents": "/api/v1/knowledge/documents",
            "knowledge_upload": "/api/v1/knowledge/documents/upload",
            "knowledge_search": "/api/v1/knowledge/search",
            "health": "/api/v1/health"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}