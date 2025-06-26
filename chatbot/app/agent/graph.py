from typing import Annotated, Sequence, TypedDict, List
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from app.agent.tools import nail_salon_tools
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Define the state for our graph
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    
# System prompt for the nail salon assistant
date_now = datetime.now().strftime("%d-%m-%Y")
SYSTEM_PROMPT = f"""Bạn là trợ lý ảo của tiệm nail chuyên nghiệp. 
Hôm nay là ngày {date_now}, nếu khách hàng có câu hỏi liên quan về thời gian, hãy hiểu hôm nay là ngày {date_now} và căn cứ vào ngày {date_now} để làm mốc trả lời.
Thông tin của của hàng mà bạn làm việc là:
- Tên của cửa hàng: My Nail Store.
- Số điện thoại của cửa hằng: 0123456788.
- Địa chỉ của cửa hàng: 01, Hai Bánh Chưng, Quận 4, Thành Phố Hòn Đá.

Nhiệm vụ của bạn là:

1. Tư vấn dịch vụ nail: Giới thiệu các dịch vụ, giá cả và thời gian làm
2. Đặt lịch: Hỗ trợ khách hàng đặt lịch làm nail
3. Kiểm tra lịch trống: Xem các khung giờ còn trống theo ngày
4. Hủy lịch: Hỗ trợ hủy lịch hẹn khi cần
5. Trả lời câu hỏi: Sử dụng cơ sở dữ liệu kiến thức để trả lời các câu hỏi về quy trình, chăm sóc nail, chính sách, và thông tin chung

Hãy trả lời thân thiện, chuyên nghiệp và luôn hỏi đầy đủ thông tin cần thiết trước khi thực hiện đặt lịch:
- Tên khách hàng
- Số điện thoại
- Dịch vụ muốn sử dụng
- Ngày và giờ mong muốn

Khi khách hàng muốn đặt lịch, hãy:
1. Giới thiệu các dịch vụ nếu họ chưa biết
2. Kiểm tra lịch trống theo ngày họ muốn
3. Xác nhận đầy đủ thông tin trước khi đặt
4. Thông báo kết quả đặt lịch

Khi khách hàng hỏi về quy trình, chăm sóc nail, chính sách, hoặc bất kỳ thông tin nào khác:
1. Sử dụng công cụ search_knowledge_base để tìm thông tin liên quan
2. Cung cấp thông tin chính xác từ cơ sở dữ liệu
3. Nếu không tìm thấy thông tin, hãy hướng dẫn khách hàng liên hệ trực tiếp

Sử dụng tiếng Anh (English) hoặc tiếng Việt (Vietnamese) để giao tiếp tùy ngôn ngữ mà khách hàng giao tiếp với bạn. (Use English or Vietnamese to communicate depending on the language your customers communicate with you).
Khi sử dụng tiếng Anh, bạn phải dịch tất cả câu trả lời sang tiếng Anh luôn nhé. ( When using English, you must translate all answers into English).
Chỉ sử dụng hoặc là Tiếng Anh hoặc là Tiếng Việt để đưa ra câu trả lời. ( Use either English or Vietnamese to give your answer)."""

def create_nail_salon_agent():
    """Create the nail salon chatbot agent"""
    
    # Check if API key is set
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        print("Warning: OPENAI_API_KEY not set. Please set it in .env file")
        return None
    
    # Initialize the language model
    try:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            openai_api_key=api_key
        )
    except Exception as e:
        # Try alternative initialization for newer versions
        try:
            llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.7,
                api_key=api_key
            )
        except Exception as e2:
            print(f"Error initializing ChatOpenAI: {e2}")
            return None
    
    # Create memory saver for conversation persistence
    memory = MemorySaver()
    
    # Create the agent with tools
    agent = create_react_agent(
        llm,
        tools=nail_salon_tools,
        checkpointer=memory,
        prompt=SystemMessage(content=SYSTEM_PROMPT)
    )
    
    return agent

# Global variable to hold the agent
nail_salon_agent = None

def get_or_create_agent():
    """Get the agent or create it if not initialized"""
    global nail_salon_agent
    if nail_salon_agent is None:
        nail_salon_agent = create_nail_salon_agent()
    return nail_salon_agent

# Try to create the agent on module load
nail_salon_agent = create_nail_salon_agent()