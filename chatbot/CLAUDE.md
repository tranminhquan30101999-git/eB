# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Vietnamese nail salon chatbot API built with FastAPI, LangGraph, and OpenAI GPT-4o-mini. The chatbot handles appointment scheduling, service consultation, availability checking, appointment cancellation, and **knowledge base queries** using natural language conversations in Vietnamese.

The system now includes a **knowledge base management system** integrated with an admin dashboard for uploading and managing documents that the chatbot can reference to answer user questions.

## Key Commands

### Running the Application
```bash
# Full application with database initialization
python run.py

# Alternative: Initialize data separately
python init_data.py
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

### Testing
```bash
# Test chatbot functionality
python test_chatbot.py

# Test individual endpoints
curl -X POST "http://localhost:8080/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Xin chào"}'

# Access frontend interface
# Navigate to http://localhost:8080/chat in browser

# Test API health endpoint
curl http://localhost:8080/api/v1/health
```

### Development Setup
```bash
# Install dependencies (uses uv for package management)
uv sync

# Set up environment
cp .env.example .env
# Add your OPENAI_API_KEY to .env
```

### Knowledge Base Management
```bash
# Upload documents via API
curl -X POST "http://localhost:8080/api/v1/knowledge/documents/upload" \
  -F "file=@document.pdf" \
  -F "title=Document Title" \
  -F "tags=tag1,tag2"

# Get all documents
curl "http://localhost:8080/api/v1/knowledge/documents"

# Search knowledge base
curl "http://localhost:8080/api/v1/knowledge/search?query=nail care"

# Admin Dashboard: http://localhost:3000/dashboard/knowledge
```

## Architecture

### LangGraph Agent Flow
The chatbot uses a ReAct agent pattern with the following components:
- **Agent State**: Manages conversation history with `add_messages` reducer
- **Tools**: Database interaction functions for services, appointments, scheduling, and **knowledge base search**
- **Memory**: Persistent conversation state via `MemorySaver` with thread-based sessions
- **System Prompt**: Vietnamese-language prompt defining the nail salon assistant's behavior and knowledge base usage

### Database Design
**Core Booking System:**
- **Service**: Nail services with pricing and duration
- **TimeSlot**: Available appointment slots (auto-generated)  
- **Appointment**: Customer bookings linking services and time slots

**Knowledge Base System:**
- **KnowledgeDocument**: Uploaded documents with metadata, processing status
- **DocumentChunk**: Text chunks for efficient search and retrieval
- **AdminUser**: User management for admin dashboard
- **ChatSession**: Conversation tracking and history
- **BookingAnalytics**: Performance metrics and reporting

### API Structure
- **Chat Endpoint** (`/api/v1/chat`): Main conversational interface
- **Admin Endpoints** (`/api/v1/admin/*`): Service and appointment management
- **Knowledge Endpoints** (`/api/v1/knowledge/*`): Document upload, management, and search
- **Frontend Template** (`/chat`): Jinja2-rendered chat interface
- **CORS enabled** for frontend integration

### Knowledge Base Integration
- **File Upload**: Supports PDF, DOCX, DOC, TXT files
- **Document Processing**: Automatic text extraction and chunking
- **Search Integration**: Chatbot can search and reference uploaded documents
- **Admin Interface**: Web UI for document management at `/dashboard/knowledge`
- **Agent Tool**: `search_knowledge_base` tool for answering questions from documents

### Frontend Template System
The application uses FastAPI's Jinja2Templates for serving the chat interface:
- **Template Location**: `app/templates/chat.html`
- **Route**: `/chat` serves the Vietnamese chat interface
- **Dynamic API URL**: Templates automatically detect and use the correct API base URL
- **Template Variables**: Configurable Vietnamese content (titles, messages, placeholders)
- **Interactive Features**: 
  - Option buttons for main services (Tư vấn dịch vụ, Đặt lịch, Kiểm tra lịch, Hủy lịch)
  - "Trở về menu chính" button to reset conversation
  - Connection status indicator
  - Improved error handling and line break support

## Critical Implementation Details

### Agent Initialization
The agent uses a global singleton pattern with fallback initialization. If OpenAI API key is missing, the chat endpoint returns helpful Vietnamese error messages rather than failing.

```python
# Agent creation handles version compatibility issues
llm = ChatOpenAI(openai_api_key=api_key)  # Primary
# Falls back to: ChatOpenAI(api_key=api_key)
```

### Database Session Management
Tools use `SessionLocal()` context managers for database access. Time slots are auto-generated when queried if they don't exist for a given date.

### Conversation Threading
Each chat uses a `conversation_id` for thread-based memory persistence, allowing multiple concurrent conversations.

## Environment Configuration

### Required Environment Variables
- `OPENAI_API_KEY`: OpenAI API key for GPT-4o-mini
- `DATABASE_URL`: SQLite database path (defaults to `sqlite:///./nail_salon.db`)

### Required Dependencies
- `fastapi`: Web framework
- `sqlalchemy`: Database ORM
- `langchain`: LLM framework
- `langchain-openai`: OpenAI integration
- `langgraph`: Agent framework
- `aiofiles`: Async file operations
- `python-multipart`: File upload support
- `pypdf2`: PDF processing
- `python-docx`: Word document processing

### Server Configuration
- Default port: 8080
- Vietnamese language responses
- Thread-safe conversation management
- File upload directory: `uploads/documents/`

## Debugging Common Issues

### Agent Not Initializing
1. Check `.env` file has valid `OPENAI_API_KEY`
2. Restart server after adding API key
3. Check console for ChatOpenAI initialization errors

### Database Issues
Run `python init_data.py` to recreate sample data and time slots.

### Version Compatibility
The project uses specific LangChain versions (0.2.x) for stability. If upgrading packages, test agent initialization carefully.