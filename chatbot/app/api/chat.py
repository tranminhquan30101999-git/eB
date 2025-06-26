from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.schemas.schemas import ChatMessage, ChatResponse, AppointmentCreate, AppointmentResponse
from app.database.config import get_db
from app.agent.graph import get_or_create_agent
from app.services import crud
from langchain_core.messages import HumanMessage
import uuid

router = APIRouter()

@router.get("/health")
async def api_health_check():
    """Health check endpoint for the API"""
    return {"status": "healthy", "service": "nail-salon-chatbot-api"}

@router.post("/chat", response_model=ChatResponse)
async def chat_with_bot(message: ChatMessage, db: Session = Depends(get_db)):
    """
    Chat endpoint for the nail salon chatbot
    """
    try:
        # Get or create the agent
        agent = get_or_create_agent()
        
        # Check if agent is initialized
        if agent is None:
            # Return a helpful response when API key is not configured
            conversation_id = message.conversation_id or str(uuid.uuid4())
            return ChatResponse(
                response="Xin chào! Hiện tại chatbot chưa được cấu hình đầy đủ (thiếu OpenAI API key). "
                        "Để sử dụng đầy đủ tính năng, vui lòng:\n"
                        "1. Lấy API key từ OpenAI (https://platform.openai.com/api-keys)\n"
                        "2. Thêm vào file .env: OPENAI_API_KEY=your_actual_api_key\n"
                        "3. Khởi động lại server\n\n"
                        "Trong thời gian này, bạn có thể kiểm tra các dịch vụ qua API admin endpoints.",
                conversation_id=conversation_id
            )
        
        # Generate conversation ID if not provided
        conversation_id = message.conversation_id or str(uuid.uuid4())
        
        # Create config for the agent with thread ID
        config = {"configurable": {"thread_id": conversation_id}}
        
        # Invoke the agent with the user message
        response = agent.invoke(
            {"messages": [HumanMessage(content=message.message)]},
            config=config
        )
        
        # Extract the last AI message as the response
        ai_messages = [msg for msg in response["messages"] if msg.type == "ai"]
        if not ai_messages:
            raise HTTPException(status_code=500, detail="No response from agent")
        
        last_response = ai_messages[-1].content
        
        return ChatResponse(
            response=last_response,
            conversation_id=conversation_id
        )
        
    except Exception as e:
        # Better error handling with more specific error messages
        error_message = str(e)
        if "authentication" in error_message.lower() or "api_key" in error_message.lower():
            error_response = "Lỗi xác thực OpenAI API. Vui lòng kiểm tra API key."
        elif "rate_limit" in error_message.lower():
            error_response = "Đã vượt quá giới hạn API. Vui lòng thử lại sau."
        else:
            error_response = f"Xin lỗi, có lỗi xảy ra: {error_message}"
        
        raise HTTPException(status_code=500, detail=error_response)

@router.post("/book-appointment", response_model=dict)
async def book_appointment_form(appointment: AppointmentCreate, db: Session = Depends(get_db)):
    """
    Book appointment through the form (bypasses chatbot for direct booking)
    """
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
            "customer_email": appointment.customer_email,
            "service_id": appointment.service_id,
            "time_slot_id": appointment.time_slot_id,
            "notes": appointment.notes,
            "status": "scheduled"
        }
        
        # Create the appointment
        db_appointment = crud.create_appointment(db, appointment_data)
        
        return {
            "success": True,
            "message": "Đặt lịch thành công",
            "appointment_id": db_appointment.id,
            "customer_name": db_appointment.customer_name,
            "service_name": service.name,
            "appointment_date": time_slot.date.isoformat(),
            "appointment_time": f"{time_slot.start_time} - {time_slot.end_time}"
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {str(e)}")