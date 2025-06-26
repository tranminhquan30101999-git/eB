# Nail Salon Chatbot API

A FastAPI-based chatbot for nail salon appointment scheduling using LangGraph, LangChain, and OpenAI GPT-4o-mini.

## Features

- **Schedule Appointments** (Đặt lịch làm nail)
- **Check Availability** (Kiểm tra lịch trống)
- **Service Consultation** (Tư vấn dịch vụ nail)
- **Cancel Appointments** (Hủy Lịch)

## Tech Stack

- **FastAPI**: Web framework
- **LangGraph**: Agent orchestration
- **LangChain**: LLM tools and chains
- **OpenAI GPT-4o-mini**: Language model
- **SQLite**: Database for development
- **SQLAlchemy**: ORM

## Installation

1. Clone the repository
```bash
git clone git@github.com:haimatrix99/nail-chatbot.git
cd nail-chatbot
```

2. Install dependencies using uv (recommended)
```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync
```

Alternatively, using pip:
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi jinja2 langchain langchain-openai langgraph pydantic python-dotenv uvicorn sqlalchemy python-multipart aiofiles 'pydantic[email]'

```

3. Create `.env` file
```bash
cp .env.example .env
```

4. Add your OpenAI API key to `.env`
```
OPENAI_API_KEY=your_openai_api_key_here
```

## Running the Application

### Using uv (recommended)
```bash
# Run the application with sample data initialization
uv run python run.py
```

### Alternative methods
```bash
# Option 1: Direct run with sample data
python run.py

# Option 2: Manual setup
python init_data.py  # Initialize sample data
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

2. The API will be available at `http://localhost:8080`
3. The chat frontend will be available at `http://localhost:8080/chat`

## API Endpoints

### Frontend Interface
- **GET** `/chat` - Web-based chat interface with Vietnamese language support and interactive option buttons

### Chat Endpoint  
- **POST** `/api/v1/chat`
```json
{
  "message": "Tôi muốn đặt lịch làm móng",
  "conversation_id": "optional-conversation-id"
}
```

### Admin Endpoints
- **GET** `/api/v1/admin/services` - List all services
- **POST** `/api/v1/admin/services` - Create a new service
- **GET** `/api/v1/admin/timeslots/{date}` - Get available slots for a date
- **GET** `/api/v1/admin/appointments/{id}` - Get appointment details
- **GET** `/api/v1/admin/appointments/phone/{phone}` - Get appointments by phone

## Sample Conversations

### Booking an appointment:
```
User: Xin chào, tôi muốn đặt lịch làm móng
Bot: Chào bạn! Tôi sẽ giúp bạn đặt lịch làm nail. Chúng tôi có các dịch vụ sau...

User: Tôi muốn làm móng gel vào ngày mai
Bot: Để kiểm tra lịch trống ngày mai, bạn cho tôi biết ngày cụ thể được không?...
```

### Checking appointments:
```
User: Kiểm tra lịch hẹn của tôi, số điện thoại 0901234567
Bot: Tôi sẽ kiểm tra lịch hẹn cho số điện thoại 0901234567...
```

## Features

### Interactive Booking Form
- **Direct booking interface** - Click "📅 Đặt lịch làm nail" to access a structured form
- **Real-time validation** - Form validates phone numbers, email, and required fields
- **Dynamic time slots** - Automatically loads available time slots for selected dates
- **Mobile responsive** - Optimized for both desktop and mobile devices

### Conversational AI
- **Vietnamese language support** - Full conversation in Vietnamese
- **Service consultation** - Ask about nail services, prices, and duration
- **Appointment management** - Book, check, and cancel appointments through chat
- **Smart context** - Remembers conversation history within sessions

## Development

### Package Management
This project uses **uv** for fast Python package management. uv provides:
- Faster dependency resolution and installation
- Better dependency locking with `uv.lock`
- Simplified virtual environment management

### Project Structure
```
chatbot/
├── app/
│   ├── agent/         # LangGraph agent and tools
│   ├── api/           # FastAPI endpoints
│   ├── database/      # Database configuration
│   ├── models/        # SQLAlchemy models
│   ├── schemas/       # Pydantic schemas
│   └── services/      # CRUD operations
├── init_data.py       # Initialize sample data
├── run.py             # Run the application
├── pyproject.toml     # Project configuration and dependencies
└── uv.lock           # Dependency lock file
```

### Adding Dependencies
```bash
# Add new dependencies
uv add package_name

# Add development dependencies
uv add --dev package_name

# Update existing dependencies
uv sync
```

### Adding New Services
You can add new services through the admin API or by modifying `init_data.py`.

### Extending the Agent
To add new capabilities, modify:
1. `app/agent/tools.py` - Add new tools
2. `app/agent/graph.py` - Update the system prompt

### Development Commands
```bash
# Run tests
uv run python test_chatbot.py

# Start development server
uv run uvicorn app.main:app --reload --port 8080

# Initialize database
uv run python init_data.py
```